from pymongo import MongoClient
import os
from datetime import datetime

# MongoDB connection setup
try:
    mongo_client = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017/"))
    db = mongo_client.fishguard
    
    # Collections
    phishing_urls = db.phishing_urls
    user_url_tags = db.user_url_tags
    job_postings = db.job_postings
    user_job_tags = db.user_job_tags
    
    print("Connected to MongoDB successfully")
except Exception as e:
    print(f"Error connecting to MongoDB: {str(e)}")
    raise e

# URL-related functions
def get_phishing_urls(url, user_id=None):
    """
    Get URL data with user-specific tagging if available
    """
    global_data = phishing_urls.find_one({'url': url})
    
    if not global_data:
        return global_data
    
    if not user_id:
        return global_data
    
    user_tag = user_url_tags.find_one({
        'user_id': user_id,
        'url': url
    })
    
    if user_tag:  # if user has tagged this url, override global value
        result = global_data.copy()  # Create a copy to avoid modifying the global data
        result['is_phishing'] = int(user_tag['is_phishing'])
        result['personalized'] = True
        
        # Add debug line
        print(f"User tag found for URL {url}: is_phishing={result['is_phishing']}, source={user_tag.get('source', 'unknown')}")
        return result
    return global_data

def add_phishing_url(url, is_phishing, source, user_id=None):
    """
    Add or update a URL in the database
    """
    doc = {
        "url": url,
        "is_phishing": int(is_phishing),
        "source": source,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }
    
    result = phishing_urls.update_one(  # update global url database
        {'url': url},
        {'$set': doc},
        upsert=True
    )
    
    # Auto-tag for user if url is phishing and user_id is provided
    if user_id and int(is_phishing) == 1:
        add_url_tag(url, is_phishing, user_id, source)
    
    return phishing_urls.find_one({'url': url})

def add_url_tag(url, is_phishing, user_id, source="auto_tagged"):
    """
    Add user-specific tag for a URL
    """
    tag_doc = {
        'user_id': user_id,
        'url': url,
        'is_phishing': int(is_phishing),
        'source': source,
        'tagged_at': datetime.now()
    }
    result = user_url_tags.update_one(
        {
            'user_id': user_id,
            'url': url
        },
        {'$set': tag_doc},
        upsert=True
    )
    return result

def update_phishing_url_tag(url, is_phishing, user_id, source="user_tagged"):
    """
    Update user-specific tag for a URL
    """
    # First verify url exists in global db
    global_url = phishing_urls.find_one({'url': url})
    if not global_url:
        # If not exists, create minimal record
        doc = {
            "url": url,
            "is_phishing": int(is_phishing),
            "source": source,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        phishing_urls.insert_one(doc)
    
    tag_result = add_url_tag(url, is_phishing, user_id, source)
    return tag_result.modified_count > 0 or tag_result.upserted_id is not None

def untag_url(url, user_id):
    """
    Remove user-specific tag for a URL
    """
    global_url = phishing_urls.find_one({'url': url})
    if not global_url:
        return False
    
    # Remove the user tag completely
    result = user_url_tags.delete_one({
        'user_id': user_id,
        'url': url
    })
    
    return result.deleted_count > 0

# Job posting related functions
def get_fake_job_postings(job_id, user_id=None):
    """
    Get job posting data with user-specific tagging if available
    """
    global_data = job_postings.find_one({'job_id': job_id})

    if not global_data:
        return global_data
    
    if not user_id:
        return global_data
    
    user_tag = user_job_tags.find_one({
        'user_id': user_id,
        'job_id': job_id
    })
    
    if user_tag:  # if user has tagged this job, override global is_fake value
        result = global_data.copy()  # Create a copy to avoid modifying the global data
        result['is_fake'] = int(user_tag['is_fake'])
        result['personalized'] = True
        
        # Add debug line
        print(f"User tag found for job {job_id}: is_fake={result['is_fake']}, source={user_tag.get('source', 'unknown')}")
        return result
    return global_data

def add_fake_job_posting(job_id, is_fake, source, content="", company_name="", job_title="", user_id=None):
    """
    Add or update a job posting in the database
    """
    doc = {
        "job_id": job_id,
        "is_fake": int(is_fake),
        "source": source,
        "content": content,
        "company_name": company_name,
        "job_title": job_title,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }
    
    result = job_postings.update_one(  # update global job database
        {'job_id': job_id},
        {'$set': doc},
        upsert=True
    )
    
    # Auto-tag for user if job is fake and user_id is provided
    if user_id and int(is_fake) == 1:
        add_job_tag(job_id, is_fake, user_id, source)
    
    return job_postings.find_one({'job_id': job_id})

def add_job_tag(job_id, is_fake, user_id, source="auto_tagged"):
    """
    Add user-specific tag for a job posting
    """
    tag_doc = {
        'user_id': user_id,
        'job_id': job_id,
        'is_fake': int(is_fake),
        'source': source,
        'tagged_at': datetime.now()
    }
    result = user_job_tags.update_one(
        {
            'user_id': user_id,
            'job_id': job_id
        },
        {'$set': tag_doc},
        upsert=True
    )
    return result

def update_job_posting_tag(job_id, is_fake, user_id, source="user_tagged"):
    """
    Update user-specific tag for a job posting
    """
    # First verify job exists in global db
    global_job = job_postings.find_one({'job_id': job_id})
    if not global_job:
        # If not exists, create minimal record
        doc = {
            "job_id": job_id,
            "is_fake": int(is_fake),
            "source": source,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        job_postings.insert_one(doc)
    
    tag_result = add_job_tag(job_id, is_fake, user_id, source)
    return tag_result.modified_count > 0 or tag_result.upserted_id is not None

def untag_job(job_id, user_id):
    """
    Remove user-specific tag for a job posting
    """
    global_job = job_postings.find_one({'job_id': job_id})
    if not global_job:
        return False
    
    # Remove the user tag completely
    result = user_job_tags.delete_one({
        'user_id': user_id,
        'job_id': job_id
    })
    
    return result.deleted_count > 0