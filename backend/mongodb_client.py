import pymongo
from pymongo import MongoClient
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class MongoDBClient:
    def __init__(self, connection_string="mongodb+srv://notsomeoneyouexpected:B7JBGhk3oGeKWW7q@cluster0.mg4logn.mongodb.net/"):
        try:
            self.client = MongoClient(connection_string)
            self.db = self.client.job_fraud_detector
            self.collection = self.db.global_collection
            # Create index on url for faster lookups
            self.collection.create_index("url", unique=True)
            logger.info("MongoDB connection established successfully")
        except Exception as e:
            logger.error(f"MongoDB connection error: {e}")
            raise

    def get_job_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve job details from database by URL
        """
        try:
            result = self.collection.find_one({"url": url})
            if result:
                # Remove MongoDB _id field before returning
                if "_id" in result:
                    del result["_id"]
                logger.info(f"Job details found in database for URL: {url}")
            else:
                logger.info(f"No job details found in database for URL: {url}")
            return result
        except Exception as e:
            logger.error(f"Error retrieving job from database: {e}")
            return None

    def add_job(self, job_data: Dict[str, Any], user_id: Optional[str] = None) -> bool:
        """
        Add job details to database
        
        Args:
            job_data: Dictionary containing job details (must include 'url')
            user_id: Optional user ID who requested the job analysis
            
        Returns:
            bool: True if insertion was successful, False otherwise
        """
        if not job_data.get("url"):
            logger.error("Cannot add job without URL")
            return False
            
        try:
            # Add user_id if provided
            if user_id:
                job_data["user_id"] = user_id
                
            # Use update_one with upsert to avoid duplicates
            self.collection.update_one(
                {"url": job_data["url"]},
                {"$set": job_data},
                upsert=True
            )
            logger.info(f"Job details stored in database for URL: {job_data['url']}")
            return True
        except Exception as e:
            logger.error(f"Error adding job to database: {e}")
            return False
    
    def update_job_classification(self,url,classification,user_id=None):
        update_data = {
            'classification':classification,
            'updated_at': datetime.now()
        }
        if user_id:
            update_data['updated_by'] = user_id
        result = self.collection.update_one(
            {'url':url},
            {'$set':update_data}
        )
        return result.modified_count>0
