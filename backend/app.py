from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from google_search_client import GoogleSearchClient
from database import get_fake_job_postings, add_fake_job_posting, update_job_posting_tag, untag_job
from middleware import setup_middleware

app = FastAPI(title='FishGuard API - Job Posting Analyzer')

setup_middleware(app)

google_search_client = GoogleSearchClient()

class JobURLCheckRequest(BaseModel):
    url: str
    content: Optional[str] = None
    source: str  # Where the link was found (e.g., 'linkedin', 'indeed', 'email')
    user_id: Optional[str] = None  # Optional user_id for personalized results

class JobTagRequest(BaseModel):
    job_id: str
    url: str
    is_fake: bool
    user_id: str
    source: Optional[str] = "user_tagged"

class UntagJobRequest(BaseModel):
    job_id: str
    user_id: str

class JobAnalysisRequest(BaseModel):
    url: str
    content: Optional[str] = None
    user_id: Optional[str] = None
    job_id: str
    company_name: Optional[str] = ""
    job_title: Optional[str] = ""

@app.get("/")
def read_root():
    return {"message": "Welcome to FishGuard Job Posting Analyzer API"}

@app.post("/check-url")
async def check_url(request: JobURLCheckRequest):
    """
    Analyze a URL to determine if it's a fake job posting
    This endpoint handles any URL, classifying non-job URLs as fake job postings
    """
    print(f"Checking job URL: {request.url} for user: {request.user_id} from source: {request.source}")
    
    # Generate a job_id if not provided (using URL hash or similar)
    job_id = request.url.replace("https://", "").replace("http://", "").replace("/", "_")
    
    # Check if job already in database
    job_data = get_fake_job_postings(job_id, request.user_id)

    if job_data:
        response = {
            'is_fake': job_data['is_fake'],
            'source': 'database',
            'job_id': job_id
        }
        if job_data.get('personalized'):
            response['personalized'] = 1
            print(f"Returning personalized result for {request.url}: {response['is_fake']}")
        
        return response
    
    try:
        # Use Google Search API client to analyze content
        # This will scrape content and check if it's a legitimate job posting
        google_result = await google_search_client.search_job(request.url)
        
        # Our model classifies non-job content as fake job postings
        # The is_fake field will be 1 if:
        # 1. URL doesn't lead to a job posting
        # 2. Job appears to be fraudulent based on content analysis
        is_fake = google_result.get("is_fake", 1)
        
        # Add to database
        result_doc = add_fake_job_posting(
            job_id, 
            is_fake,
            google_result.get("source", "model_analysis"),
            google_result.get("content", ""),
            google_result.get("company_name", "Unknown"),
            google_result.get("job_title", "Unknown"),
            request.user_id
        )
        
        if not result_doc:
            raise HTTPException(status_code=500, detail="Failed to save job analysis to database")
        
        return {
            "is_fake": is_fake,
            "source": google_result.get("source", "model_analysis"),
            "job_id": job_id
        }
    except Exception as e:
        print(f"Error analyzing job URL: {str(e)}")
        return {"is_fake": 1, "source": "error", "error": str(e), "job_id": job_id}

@app.post('/tag-job')
async def tag_job(request: JobTagRequest):
    """
    Allow users to manually tag job postings as fake or legitimate
    """
    result = update_job_posting_tag(request.job_id, request.url, request.is_fake, request.user_id, request.source)
    if not result:
        raise HTTPException(status_code=404, detail="Job not found in database")
    return {"message": "Job tagged successfully", "personalized": 1}

@app.post('/untag-job')
async def untag_job_endpoint(request: UntagJobRequest):
    """
    Remove user's personal tag from a job posting
    """
    result = untag_job(request.job_id, request.user_id)
    if not result:
        raise HTTPException(status_code=404, detail="Job not found or no user tag exists")
    return {"message": "Job untagged successfully", "personalized": 1}

@app.post('/analyze-job')
async def analyze_job(request: JobAnalysisRequest):
    """
    Detailed job posting analysis with additional metadata
    """
    # Check if job already in database
    job_data = get_fake_job_postings(request.job_id, request.user_id)
    
    if job_data:
        response = {
            'is_fake': job_data['is_fake'],
            'source': 'database',
            'job_id': request.job_id
        }
        if job_data.get('personalized'):
            response['personalized'] = 1
        
        return response
    
    try:
        # Use Google Search API client to analyze job posting
        google_result = await google_search_client.search_job(request.url)
        
        # Our model classifies if this is a legitimate job posting
        is_fake = google_result.get("is_fake", 1)
        
        # Add to database with more metadata
        result_doc = add_fake_job_posting(
            request.job_id, 
            is_fake,
            google_result.get("source", "model_analysis"),
            google_result.get("content", ""),
            request.company_name or google_result.get("company_name", "Unknown"),
            request.job_title or google_result.get("job_title", "Unknown"),
            request.user_id
        )
        
        if not result_doc:
            raise HTTPException(status_code=500, detail="Failed to save job to database")
        
        return {
            "is_fake": is_fake,
            "source": google_result.get("source", "model_analysis"),
            "job_id": request.job_id,
            "details": google_result.get("details", {})
        }
    except Exception as e:
        print(f"Error analyzing job: {str(e)}")
        return {"is_fake": 1, "source": "error", "error": str(e), "job_id": request.job_id}