from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, HttpUrl, field_validator
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from urllib.parse import urlparse
import redis.asyncio as redis
import torch
from transformers import BertTokenizer
from bs4 import BeautifulSoup
from model import JobPostingClassifier
from botasaurus.user_agent import UserAgent
import spacy
import time
from typing import List, Optional, Dict, Any
import logging
import sys
import asyncio
import google.generativeai as genai
from mongodb_client import MongoDBClient

# Import Botasaurus
from botasaurus.browser import browser,Driver
from botasaurus.soupify import soupify

genai.configure(api_key="AIzaSyD8r3yWvcVMYP-K-oqjP_leaB6TRkooO_o")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('job_fraud_detector.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from contextlib import asynccontextmanager
@asynccontextmanager
async def lifespan(app:FastAPI):
    try:
        redis_client = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True
        )
        await FastAPILimiter.init(redis_client)
        app.state.mongo_client = MongoDBClient()
        logger.info("Application startup complete - Redis initialized")

        yield
    except Exception as e:
        logger.critical(f"Startup initialization failed: {e}")
        raise

    finally:
        logger.info("Application shutting down")

app = FastAPI(
    title='Job Posting Fraud Detector',
    description='Advanced API for detecting fraudulent job postings',
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class JobSearchRequest(BaseModel):
    url: HttpUrl
    user_id: Optional[str] = None
    @field_validator("url")
    @classmethod
    def validate_url(cls, url):
        try:
            parsed_url = urlparse(str(url))
            if not all([
                parsed_url.scheme in ['http', 'https'],
                parsed_url.netloc,
                len(parsed_url.netloc) > 0,
                len(str(url)) <= 2000
            ]):
                raise ValueError("Invalid URL format")
            return url
        except Exception as e:
            logging.getLogger(__name__).error(f"URL validation error: {e}")
            raise ValueError("Invalid URL format")

# # Load model and tokenizer
# model = JobPostingClassifier(n_classes=2)
# try:
#     model.load_state_dict(torch.load('job_posting_classifier.pth', map_location=torch.device('cpu')))
#     model.eval()
#     logger.info("Model loaded successfully")
# except Exception as e:
#     logger.critical(f"Failed to load model: {e}")
#     raise

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
nlp = spacy.load('en_core_web_sm')

# # Function to preprocess input text for the BERT model
# def prepare_sample(text):
#     try:
#         encoding = tokenizer.encode_plus(
#             text,
#             add_special_tokens=True,
#             max_length=128,
#             return_token_type_ids=False,
#             padding='max_length',
#             return_attention_mask=True,
#             return_tensors='pt',
#             truncation=True
#         )
#         return encoding['input_ids'], encoding['attention_mask']
#     except Exception as e:
#         logger.error(f"Text preparation error: {e}")
#         raise

# def predict(text):
#     try:
#         input_ids, attention_mask = prepare_sample(text)
#         with torch.no_grad():
#             outputs = model(input_ids=input_ids, attention_mask=attention_mask)
#             _, preds = torch.max(outputs, dim=1)
        
#         classification = "Fraudulent" if preds.item() == 1 else "Legitimate"
#         logger.info(f"Job posting classified as: {classification}")
#         return classification
#     except Exception as e:
#         logger.error(f"Prediction error: {e}")
#         raise

def predict_job_posting(text):
    """
    Use Gemini API to classify job posting
    
    Returns:
    - "Legitimate": for genuine job postings
    - "Fraudulent": for suspicious or potentially fake job postings
    - "Unrelated": for content not related to job postings
    """
    try:
        # Truncate text to prevent exceeding API limits
        text = text[:5000]
        
        # Configure Gemini model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # prompt = f"""Analyze the following text and classify it as:
        # - "Legitimate" if it appears to be ANY job-related content, including job listings, job boards, career pages, 
        #   or pages containing job titles, skills, salaries, locations, or any employment-related information. BE VERY LIBERAL 
        #   with this classification - if there's ANY job-related content, classify as "Legitimate".
        
        # - "Fraudulent" if it shows clear signs of being a scam or suspicious job offer (unrealistic salaries, upfront payments, 
        #   vague responsibilities with high pay, poor grammar/spelling throughout).
        
        # - "Unrelated" ONLY if the text has absolutely no connection to employment, careers, jobs, or work opportunities.

        # Text to analyze:
        # {text}

        # Return ONLY one of these exact words: "Legitimate", "Fraudulent", or "Unrelated".
        # """
        prompt = f"""Analyze the following job posting and classify it as:
        
        - "Fraudulent" if ANY of these red flags are present:
          * Requests for payment from applicants
          * Unrealistically high salary for minimal qualifications
          * Personal bank account information requested
          * Job offers without interviews
          * Work-from-home jobs promising very high pay for minimal work
          * Requests for sensitive personal information early in the process
          * Use of personal email domains (gmail, yahoo, etc.) for company contacts
          * Poor grammar and spelling throughout the text
          * Suspicious contact methods (like WhatsApp only)
          * Extremely vague job descriptions paired with high salary promises
          * Claims of immediate hiring with no interview process
        
        - "Legitimate" if it appears to be a professional job posting without the fraud indicators above.
          Note: The job posting might be incomplete due to scraping limitations - this does NOT make it fraudulent.
        
        - "Unrelated" ONLY if the text has absolutely no connection to employment, careers, jobs, or work.

        Text to analyze:
        {text}

        Return ONLY one of these exact words: "Legitimate", "Fraudulent", or "Unrelated".
        """
        
        # Generate response
        response = model.generate_content(prompt)
        
        # Extract classification
        classification = response.text.strip()
        
        # Validate classification
        valid_classifications = ["Legitimate", "Fraudulent", "Unrelated"]
        if classification not in valid_classifications:
            logger.warning(f"Invalid classification received: {classification}. Defaulting to 'Unrelated'")
            classification = "Unrelated"
        
        logger.info(f"Job posting classified as: {classification}")
        return classification
    
    except Exception as e:
        logger.error(f"Gemini API prediction error: {e}")
        return "Unrelated"  # Default to unrelated in case of any error



@browser(
    max_retry=5,
    parallel=True,
    wait_for_complete_page_load=True,
    headless=True,
    user_agent=UserAgent.RANDOM,
    block_images_and_css=False,
    cache=True
        )
def scrape_job_posting(driver:Driver,url):
    logger = logging.getLogger(__name__)
    logger.info(f"Scraping URL: {url}")
    
    try:
        driver.get(url)
        #driver.sleep(5)
        
        #driver.run_js("window.scrollTo(0, document.body.scrollHeight);")
        #driver.sleep(3) 
    
        from botasaurus.browser import Wait
        elements = ["h1", "p", "ul", "span"]
    
        for selector in elements:
            try:
                driver.wait_for_element(selector, wait=Wait.VERY_LONG)
                print(f"✅ Found: {selector}")
            except Exception as e:
                print(f"⚠️ Not found: {selector} - {e}")

        
        # Get page source
        try:
            h1_content = driver.get_text("h1")
            if h1_content is None:
                h1_content = ""
            h1_soup = soupify(h1_content)
            h1_text = h1_soup.get_text(separator=" ",strip=True)
        except Exception as e:
            print(f"Warning: Could not find <h1> tag. Error: {e}")
            h1_text = ""
        try:
            h2_content = driver.get_text("h2")
            if h2_content is None:
                h2_content = ""
            h2_soup = soupify(h2_content)
            h2_text = h2_soup.get_text(separator=" ",strip=True)
        except Exception as e:
            print(f"Warning: Could not find <h2> tag. Error: {e}")
            h2_text = ""

        try:
            p_content = driver.get_text("p")
            if p_content is None:
                p_content=""
            p_soup = soupify(p_content)
            p_text = p_soup.get_text(separator=" ",strip=True)
        except Exception as e:
            print(f"Warning: Could not find <p> tag. Error: {e}")
            p_text = ""
        try:
            ul_content = driver.get_text("ul")
            if ul_content is None:
                ul_content = ""
            ul_soup = soupify(ul_content)
            ul_text = ul_soup.get_text(separator=" ",strip=True)
        
        except Exception as e:
            print(f"Warning: Could not find <ul> tag. Error: {e}")
            ul_text = ""
        
        try:
            span_content = driver.get_text("span")
            if span_content is None:
                span_content = ""
            span_soup = soupify(span_content)
            span_text = span_soup.get_text(separator=" ",strip=True)
        except Exception as e:
            print(f"Warning: Could not find <h2> tag. Error: {e}")
            span_text = ""
        
        #text = ' '.join([h1_text, h2_text, p_text, ul_text])
        text = h1_text+" "+h2_text+" "+ul_text+" "+p_text+" "+span_text
        print(text)
        if not text:
            logger.warning(f"No text content extracted from {url}")
            return None
        
        return text
        
    except Exception as e:
        logger.error(f"Scraping error for {url}: {e}")
        return None

    finally:
        driver.close()

def extract_job_details(text):
    doc = nlp(text)
    
    job_info = {
        "Company": [],
        "Job Title": [],
        "Salary": [],
        "Location": []
    }

    # Job-related keywords to validate the content
    job_keywords = [
        'job', 'hiring', 'career', 'position', 'role', 'employment', 
        'vacancy', 'opportunity', 'recruit', 'wanted', 'seeking'
    ]

    # Check if the text contains job-related keywords
    text_lower = text.lower()
    if not any(keyword in text_lower for keyword in job_keywords):
        return job_info

    # Company Names
    for ent in doc.ents:
        if ent.label_ == "ORG":
            # Additional filtering to ensure it's a potential company
            if len(ent.text.split()) <= 5 and not any(keyword in ent.text.lower() for keyword in ['movie', 'film', 'entertainment']):
                job_info["Company"].append(ent.text)

    # Location Extraction
    for ent in doc.ents:
        if ent.label_ == "GPE":
            # Filter out generic locations
            if len(ent.text.split()) <= 3 and not any(keyword in ent.text.lower() for keyword in ['movie', 'film', 'entertainment']):
                job_info["Location"].append(ent.text)

    # Salary Extraction with strict filtering
    for ent in doc.ents:
        if ent.label_ == "MONEY":
            # Strict salary pattern matching
            import re
            salary_patterns = [
                r'\$\d+(?:,\d{3})*(?:k)?\s*(?:per\s*(?:year|month|hour|week))?',
                r'\d+(?:,\d{3})*\s*(?:\$|dollars)\s*(?:per\s*(?:year|month|hour|week))?'
            ]
            
            for pattern in salary_patterns:
                if re.search(pattern, ent.text, re.IGNORECASE):
                    job_info["Salary"].append(ent.text)

    # Job Title Extraction with improved regex
    job_title_patterns = r"""
        (?:(?:Hiring|Position|Role|Opening)\s+(?:for|in)\s+)?
        ([A-Z][a-zA-Z\s\-\/]+?)
        (?=\sat|at\s|\s-\s|,|$)
    """
    import re
    matches = re.findall(job_title_patterns, text, re.IGNORECASE | re.VERBOSE)

    for match in matches:
        # Additional filtering for job titles
        if len(match.split()) <= 6 and not any(keyword in match.lower() for keyword in ['movie', 'film', 'entertainment']):
            job_info["Job Title"].append(match.strip())

    # Ensure only unique values are stored
    for key in job_info:
        job_info[key] = list(set(job_info[key]))

    return job_info

@app.post("/analyze-job")
async def analyze_job(request: Request):
    try:
        body = await request.json()
        url = body.get('url')
        user_id = body.get('user_id')
        
        if not url:
            raise HTTPException(status_code=422, detail="URL is required")
        # Validate URL more strictly
        parsed_url = urlparse(url)
        if parsed_url.scheme not in ['http', 'https']:
            logger.warning(f"Invalid URL scheme: {url}")
            return {
                "url": url,
                "classification": "Invalid URL",
                "job_details": {},
                "error": "Only HTTP and HTTPS URLs are supported"
            }
        # First, check if the URL exists in MongoDB
        mongo_client = app.state.mongo_client
        cached_result = mongo_client.get_job_by_url(url)
        
        if cached_result:
            logger.info(f"Retrieved cached result for URL: {url}")
            return cached_result
        
        # If not in DB, proceed with scraping and analysis
        logger.info(f"No cached result found for URL: {url}, proceeding with scraping")
        
        # Use Botasaurus scraper
        job_text = scrape_job_posting(url)
        
        if not job_text: 
            logger.warning(f"No content retrieved for URL: {url}")
            return {
                "url": url,
                "classification": "Unable to Retrieve",
                "job_details": {},
                "error": "Could not scrape job posting content"
            }
        # Truncate very long text to prevent model overload
        job_text = job_text[:5000]  # Limit to 5000 characters

        job_details = extract_job_details(job_text)
        print(f"THE JOB TEXT IS: {job_text}")
        print(f"THE JOB DETAILS AFTER NER ARE: {job_details}")
        
        #classification = predict(job_text)
        classification = predict_job_posting(job_text)
        logger.info(f"Analyzed job posting from {url}")
        result =  {
            "url": url,
            "job_details": job_details,
            "classification": classification
        }
        # Only store in database if scraping and prediction were successful
        # and classification is not "Unable to Retrieve"
        if job_text and classification not in ["Unable to Retrieve"]:
            # Store in MongoDB
            mongo_client.add_job(result, user_id)
            logger.info(f"Stored new job analysis in database for URL: {url}")
        
        logger.info(f"Analyzed job posting from {url}")
        return result
    
    except Exception as e:
        logger.error(f"Job analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update-classification")
async def update_classification(request: Request):
    try:
        body = await request.json()
        url = body.get('url')
        new_classification = body.get('classification')
        user_id = body.get('user_id')

        if not url:
            raise HTTPException(status_code=422,detail="URL is required")
        
        if not new_classification:
            raise HTTPException(status_code=422,detail="Classification is required")
        
        if new_classification not in ["Legitimate", "Fraudulent", "Unrelated"]:
            raise HTTPException(status_code=422, detail="Classification must be one of: Legitimate, Fraudulent, or Unrelated")
        
        mongo_client = app.state.mongo_client
        
        # Check if the URL exists in MongoDB
        job_data = mongo_client.get_job_by_url(url)

        if not job_data:
            raise HTTPException(status_code=404, detail="URL not found in database")
        updated = mongo_client.update_job_classification(url, new_classification, user_id)
        
        if not updated:
            raise HTTPException(status_code=500, detail="Failed to update classification")
        
        logger.info(f"Updated classification for URL: {url} to {new_classification}")
        return {
            "classification": new_classification,
            "message": "Classification updated successfully"
        }
    except HTTPException as he:
        raise he
    
    except Exception as e:
        logger.error(f"Error updating classification: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
        

from datetime import datetime
@app.get("/health")
async def health_check():
    return {
        "status":"healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
def home():
    return {"message": "Welcome to the Job Fraud Detector API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")