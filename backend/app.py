from fastapi import FastAPI, HTTPException,Request
from pydantic import BaseModel,HttpUrl,field_validator
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from urllib.parse import urlparse
import redis.asyncio as redis
import torch
from transformers import BertTokenizer
from bs4 import BeautifulSoup
from model import JobPostingClassifier
import spacy
import time
from typing import List, Optional, Dict, Any
import random
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import random
import logging
import nest_asyncio

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('job_fraud_detector.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

#headless
from contextlib import asynccontextmanager
@asynccontextmanager
async def lifespan(app:FastAPI):
    #statrup logic
    try:
        #initialize redis
        redis_client = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True
        )
        await FastAPILimiter.init(redis_client)
        logger.info("Application startup complete - Redis initialized")

        yield
    except Exception as e:
        logger.critical(f"Startup initialization failed: {e}")
        raise

    finally:
        #shutdown logic
        logger.info("Application shutting down")

app = FastAPI(
    title='Job Posting Fraud Detector',
    description='Advanced API for detecting fraudulent job postings',
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# app.add_middleware(
#     TrustedHostMiddleware, 
#     allowed_hosts=["localhost", "127.0.0.1"]
# )

class JobSearchRequest(BaseModel):
    url: HttpUrl  # Changed from urls to a single URL

    @field_validator("url")
    @classmethod
    def validate_url(cls, url):
        try:
            parsed_url = urlparse(str(url))
            if not all([
                parsed_url.scheme in ['http', 'https'],
                parsed_url.netloc,  # must have a domain
                len(parsed_url.netloc) > 0,
                len(str(url)) <= 2000
            ]):
                raise ValueError("Invalid URL format")
            return url
        except Exception as e:
            logging.getLogger(__name__).error(f"URL validation error: {e}")
            raise ValueError("Invalid URL format")

# class JobSearchRequest(BaseModel):
#     urls: List[str]

   
async def init_redis():
    redis_client = redis.Redis(
        host='localhost',
        port=6379,
        db=0,
        decode_responses=True
    )
    await FastAPILimiter.init(redis_client)

def log_execute_time(func):

    def wrapper(*args,**kwargs):
        start_time = time.time()
        try:
            result = func(*args,**kwargs)
            execution_time = time.time()-start_time
            logger.info(f"{func.__name__} excuted in {execution_time:.2f} seconds")
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            raise
    return wrapper

model = JobPostingClassifier(n_classes=2)
try:
    model.load_state_dict(torch.load('job_posting_classifier.pth', map_location=torch.device('cpu')))
    model.eval()
    logger.info("Model loaded successfully")
except Exception as e:
    logger.critical(f"Failed to load model: {e}")
    raise

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
nlp = spacy.load('en_core_web_sm')

# Function to preprocess input text for the BERT model
#@log_execute_time
def prepare_sample(text):
    try:
        encoding = tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=128,
            return_token_type_ids=False,
            padding='max_length',
            return_attention_mask=True,
            return_tensors='pt',
            truncation=True
        )
        return encoding['input_ids'], encoding['attention_mask']
    except Exception as e:
        logger.error(f"Text preparation error: {e}")
        raise

#@log_execute_time
def predict(text):
    try:
        input_ids, attention_mask = prepare_sample(text)
        with torch.no_grad():
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            _, preds = torch.max(outputs, dim=1)
        
        classification = "Fraudulent" if preds.item() == 1 else "Legitimate"
        logger.info(f"Job posting classified as: {classification}")
        return classification
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise

PROXIES = [
    "103.216.82.18:6667",
    "51.79.144.52:3128",
    "185.112.12.34:8080",
    "85.25.197.10:5566",
    "45.77.195.146:8080",
    "103.16.214.142:10017",
    "103.163.62.9:8080",
    "5.161.75.45:3128",
    "103.125.216.10:8080",
    "143.198.182.218:80"
]
USER_AGENTS = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.95 Safari/537.36"
            ]

import random
import requests
import aiohttp
import asyncio

async def is_proxy_alive(proxy):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://httpbin.org/ip", 
                proxy=f"http://{proxy}", 
                timeout=5
            ) as response:
                return response.status == 200
    except:
        return False

async def get_random_proxy():
    random.shuffle(PROXIES)
    for proxy in PROXIES:
        if await is_proxy_alive(proxy):
            return proxy
    return None  # No working proxies found


def get_random_user_agent():
    return random.choice(USER_AGENTS)

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# Global variable to store the Playwright instance
_playwright = None

async def initialize_playwright():
    global _playwright
    try:
        _playwright = await async_playwright().__aenter__()
        print("Playwright initialized successfully")
        return _playwright
    except Exception as e:
        logger.error(f"Failed to initialize Playwright: {e}")
        return None

async def get_browser():
    global _playwright
    if _playwright is None:
        _playwright = await initialize_playwright()
    
    if _playwright is None:
        logger.error("Playwright not initialized")
        return None
    
    try:
        browser = await _playwright.chromium.launch(
            headless=False,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-software-rasterizer'
            ],
            timeout=60000  # 60 seconds timeout

        )
        return browser
    except Exception as e:
        logger.error(f"Failed to launch browser: {e}")
        return None
#Scraper setup error for
# async def scrape_job_posting(url):
#     logger = logging.getLogger(__name__)
#     logger.info(f"Scraping URL: {url}")
    
#     playwright = None
#     try:
#         # Install browsers if not already installed
#         try:
#             import sys
#             import subprocess
#             subprocess.check_call([sys.executable, '-m', 'playwright', 'install'])
#         except Exception as install_err:
#             logger.error(f"Playwright installation error: {install_err}")
        
#         # Explicitly create Playwright instance
#         playwright = await async_playwright().start()
        
#         # Launch browser with more detailed configuration
#         browser = await playwright.chromium.launch(
#             headless=False,
#             args=[
#                 '--no-sandbox',
#                 '--disable-setuid-sandbox',
#                 '--disable-dev-shm-usage',
#                 '--disable-gpu',
#                 '--disable-software-rasterizer'
#             ],
#             timeout=60000  # 60 seconds timeout
#         )

#         try:
#             # Create a new browser context
#             context = await browser.new_context(
#                 user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
#             )
            
#             # Create a new page
#             page = await context.new_page()

#             try:
#                 # Navigate to the URL with extended timeout
#                 await page.goto(url, timeout=45000, wait_until='networkidle')
                
#                 # Wait for potential dynamic content
#                 await page.wait_for_timeout(3000)

#                 # Scroll to trigger lazy-loading
#                 await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
#                 await page.wait_for_timeout(2000)
                
#                 # Extract page content
#                 content = await page.content()
#                 soup = BeautifulSoup(content, "html.parser")
#                 text = soup.get_text(separator=" ", strip=True)
                
#                 if not text:
#                     logger.warning(f"No text content extracted from {url}")
#                     return None
                
#                 return text 
            
#             except Exception as e:
#                 logger.error(f"Scraping error for {url}: {e}")
#                 return None
            
#             finally:
#                 # Close context and browser
#                 await context.close()
#                 await browser.close()
        
#         except Exception as e:
#             logger.error(f"Browser context error for {url}: {e}")
#             return None
        
#     except Exception as e:
#         logger.error(f"Scraper setup error for {url}: {e}")
#         return None
    
#     finally:
#         # Ensure Playwright is closed
#         if playwright:
#             await playwright.stop()
       
async def scrape_job_posting(url):
    logger = logging.getLogger(__name__)
    logger.info(f"Scraping URL: {url}")
    
    # Ensure proper event loop policy for Windows
    import sys
    if sys.platform == "win32":
        import asyncio
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # Import Playwright synchronously to avoid async initialization issues
    from playwright.sync_api import sync_playwright
    
    try:
        # Use sync_playwright with context manager
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-software-rasterizer'
                ]
            )
            
            # Create context
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
            
            # Create page
            page = context.new_page()
            
            try:
                # Navigate to URL
                page.goto(url, timeout=45000, wait_until='networkidle')
                
                # Wait for potential dynamic content
                page.wait_for_timeout(3000)
                
                # Scroll to trigger lazy-loading
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(2000)
                
                # Extract page content
                content = page.content()
                soup = BeautifulSoup(content, "html.parser")
                text = soup.get_text(separator=" ", strip=True)
                
                if not text:
                    logger.warning(f"No text content extracted from {url}")
                    return None
                
                return text 
            
            except Exception as e:
                logger.error(f"Scraping error for {url}: {e}")
                return None
            
            finally:
                # Close browser
                browser.close()
    
    except Exception as e:
        logger.error(f"Playwright setup error for {url}: {e}")
        return None

#use name entity recognition (ner)
def extract_job_details(text):
    doc = nlp(text)
    
    job_info = {
        "Company": [],
        "Job Title": [],
        "Salary": [],
        "Location": []
    }

    for ent in doc.ents:
        if ent.label_ == "ORG":  # Company Names
            job_info["Company"].append(ent.text)
        elif ent.label_ == "MONEY":  # Salary
            job_info["Salary"].append(ent.text)
        elif ent.label_ == "GPE":  # Locations
            job_info["Location"].append(ent.text)

    # Ensure only unique values are stored
    for key in job_info:
        job_info[key] = list(set(job_info[key]))

    # Job Title Extraction
    job_title_patterns = r"""
        (?:(?:Hiring for|Position:|Role:|Opening for)\s+)?   # Optional match for job title prefixes
        (?:[-•]*)\s*                                         # Matches bullet points like "• Software Engineer"
        ([A-Z][a-zA-Z\s\-\/]+?)                              # Captures job titles (Capitalized Words, hyphens, slashes)
        (?=\sat|at\s|\s-\s|,|$)                              # Ends at 'at', '-', or ',' to avoid extra words
    """
    import re
    matches = re.findall(job_title_patterns, text, re.IGNORECASE | re.VERBOSE)

    for match in matches:
        job_info["Job Title"].append(match.strip())

    # Ensure only unique job titles are stored
    job_info["Job Title"] = list(set(job_info["Job Title"]))

    return job_info


from json import JSONDecodeError
def scrape_job_posting_sync(url):
    logger = logging.getLogger(__name__)
    logger.info(f"Scraping URL (Sync): {url}")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu'
                ]
            )
            
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = context.new_page()
            
            try:
                page.goto(url, timeout=45000, wait_until='networkidle')
                page.wait_for_timeout(3000)
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(2000)
                
                content = page.content()
                soup = BeautifulSoup(content, "html.parser")
                text = soup.get_text(separator=" ", strip=True)
                
                if not text:
                    logger.warning(f"No text content extracted from {url}")
                    return None
                
                return text
            
            except Exception as e:
                logger.error(f"Synchronous scraping error for {url}: {e}")
                return None
            
            finally:
                context.close()
                browser.close()
    
    except Exception as e:
        logger.error(f"Synchronous scraper setup error for {url}: {e}")
        return None
    
@app.post("/analyze-job")
async def analyze_job(request: Request):
    try:
        body = await request.json()
        url = body.get('url')
        
        if not url:
            raise HTTPException(status_code=422, detail="URL is required")

        # Use async scraper
        job_text = await scrape_job_posting(url)
        
        if not job_text: 
            logger.warning(f"No content retrieved for URL: {url}")
            return {
                "url": url,
                "classification": "Unable to Retrieve",
                "job_details": {},
                "error": "Could not scrape job posting content"
            }

        job_details = extract_job_details(job_text)
        classification = predict(job_text)

        logger.info(f"Analyzed job posting from {url}")
        return {
            "url": url,
            "job_details": job_details,
            "classification": classification
        }
    
    except Exception as e:
        logger.error(f"Job analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
# Add shutdown event to close Playwright
@app.on_event("shutdown")
async def shutdown_event():
    global _playwright
    if _playwright:
        await _playwright.__aexit__(None, None, None)
        
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
