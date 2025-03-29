import json
import os
from typing import Dict, Any
from google.oauth2 import service_account
from googleapiclient.discovery import build
import re
import aiohttp
import asyncio

class GoogleSearchClient:
    """
    Client for interacting with Google Search API to analyze URLs, 
    particularly job postings for potential scams
    """
    
    def __init__(self):
        """Initialize the Google Search client"""
        try:
            # Try to load credentials from service account file
            credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'service-account.json')
            self.credentials = service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=['https://www.googleapis.com/auth/cloud-platform',
                        'https://www.googleapis.com/auth/cse']
            )
            
            # Build the API client for Google Search
            self.service = build('customsearch', 'v1', developerKey=self.api_key)
            #self.search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID', 'YOUR_SEARCH_ENGINE_ID')
            self.search_engine_id = '0597815c0a75e4879'
            
            print("Google Search API client initialized successfully")
        except Exception as e:
            print(f"Error initializing Google Search API client: {str(e)}")
            # Still initialize the class, but with a flag indicating the service is not available
            self.service = None
    
    async def fetch_url_content(self, url: str) -> str:
        """Fetch content from a URL to analyze"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        return await response.text()
                    return ""
        except Exception as e:
            print(f"Error fetching URL content: {str(e)}")
            return ""

    async def search_job(self, url: str) -> Dict[str, Any]:
        """
        Analyze a job posting URL to determine if it's potentially fake
        
        Returns:
            Dict with is_phishing (1 for fake, 0 for legitimate), source, and other metadata
        """
        if not self.service:
            return {"is_phishing": 1, "source": "google_search_api_unavailable"}
        
        try:
            # Extract company name and job title from URL if available
            company_match = re.search(r'company=([^&]+)', url)
            title_match = re.search(r'title=([^&]+)', url)
            
            company_name = company_match.group(1).replace('+', ' ') if company_match else ""
            job_title = title_match.group(1).replace('+', ' ') if title_match else ""
            
            # If not in URL, try to extract from the content
            if not company_name or not job_title:
                content = await self.fetch_url_content(url)
                # Basic extraction - could be enhanced with more sophisticated parsing
                if not company_name:
                    company_match = re.search(r'company.*?["\']([^"\']+)["\']', content, re.IGNORECASE)
                    if company_match:
                        company_name = company_match.group(1)
                
                if not job_title:
                    title_match = re.search(r'position.*?["\']([^"\']+)["\']', content, re.IGNORECASE)
                    if title_match:
                        job_title = title_match.group(1)
            
            # Build search queries to check legitimacy
            search_queries = []
            if company_name and job_title:
                search_queries.append(f"\"{company_name}\" \"{job_title}\" scam OR fake OR fraud")
                search_queries.append(f"\"{company_name}\" legitimate company")
            elif company_name:
                search_queries.append(f"\"{company_name}\" scam OR fake OR fraud")
                search_queries.append(f"\"{company_name}\" legitimate company")
            else:
                # If no company info, just search the URL
                search_queries.append(f"\"{url}\" scam OR fake OR fraud")
            
            # Track risk signals
            risk_signals = 0
            scam_results_count = 0
            legitimate_results_count = 0
            
            # Execute searches
            for query in search_queries:
                search_results = self.service.cse().list(
                    q=query,
                    cx=self.search_engine_id,
                    num=10
                ).execute()
                
                # Analyze search results
                items = search_results.get('items', [])
                for item in items:
                    snippet = item.get('snippet', '').lower()
                    title = item.get('title', '').lower()
                    
                    # Check for scam indicators
                    if 'scam' in snippet or 'fake' in snippet or 'fraud' in snippet:
                        if 'not a scam' not in snippet and 'isn\'t a scam' not in snippet:
                            scam_results_count += 1
                            risk_signals += 1
                    
                    # Check for legitimacy indicators
                    if 'legitimate' in snippet or 'real company' in snippet:
                        if 'not legitimate' not in snippet:
                            legitimate_results_count += 1
                            risk_signals -= 1
            
            # Determine if the job is likely fake based on signals
            is_phishing = None if scam_results_count == 0 and legitimate_results_count == 0 else (1 if risk_signals > 0 or scam_results_count > legitimate_results_count else 0)
            
            return {
                "is_phishing": is_phishing,
                "source": "google_search_api",
                "details": {
                    "risk_signals": risk_signals,
                    "scam_results": scam_results_count,
                    "legitimate_results": legitimate_results_count,
                    "company_name": company_name,
                    "job_title": job_title
                }
            }
            
        except Exception as e:
            print(f"Error in Google Search API job analysis: {str(e)}")
            return {"is_phishing": None, "source": "google_search_api_error", "error": str(e)}
    
    