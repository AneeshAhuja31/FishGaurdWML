# import torch
# from torch import nn


# from transformers import BertModel, BertTokenizer
# import numpy as np
# from typing import Dict, List, Union, Optional
# import requests
# from bs4 import BeautifulSoup
# from google_search_client import GoogleSearchClient

# class FakeJobDetectionModel:
#     def __init__(self, model_path: str = "job_posting_classifier.pth"):
#         self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#         self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
#         self.bert = BertModel.from_pretrained('bert-base-uncased')
#         self.classifier = nn.Sequential(
#             nn.Linear(768, 256),
#             nn.ReLU(),
#             nn.Dropout(0.1),
#             nn.Linear(256, 1),
#             nn.Sigmoid()
#         )
        
#         # Check if pre-trained model exists
#         try:
#             self.load_model(model_path)
#             print(f"Loaded pre-trained model from {model_path}")
#         except FileNotFoundError:
#             print("No pre-trained model found. You'll need to train the model first.")
        
#         self.google_search_client = GoogleSearchClient()
    
#     def load_model(self, model_path: str):
#         """Load a pre-trained model"""
#         checkpoint = torch.load(model_path, map_location=self.device)
#         self.bert.load_state_dict(checkpoint['bert_state_dict'])
#         self.classifier.load_state_dict(checkpoint['classifier_state_dict'])
#         self.bert.to(self.device)
#         self.classifier.to(self.device)
#         self.bert.eval()
#         self.classifier.eval()
    
#     def save_model(self, model_path: str):
#         """Save the trained model"""
#         torch.save({
#             'bert_state_dict': self.bert.state_dict(),
#             'classifier_state_dict': self.classifier.state_dict(),
#         }, model_path)
        
#     def preprocess_text(self, text: str) -> Dict:
#         """Tokenize and prepare text for BERT model"""
#         encoded_input = self.tokenizer.encode_plus(
#             text,
#             max_length=512,
#             truncation=True,
#             padding='max_length',
#             return_tensors='pt'
#         )
#         return {k: v.to(self.device) for k, v in encoded_input.items()}
    
#     def extract_content_from_url(self, url: str) -> str:
#         """Extract and clean content from a URL using Google Search API"""
#         try:
#             # Use Google Search API to get additional information
#             search_results = self.google_search_client.search_job_info(url)
            
#             # Attempt to directly scrape the URL
#             response = requests.get(url, timeout=10)
#             if response.status_code == 200:
#                 soup = BeautifulSoup(response.text, 'html.parser')
                
#                 # Extract job description and relevant content
#                 job_description = ""
                
#                 # Look for common job description containers
#                 description_elements = soup.select('.job-description, .description, [data-automation="jobDescription"], .jobsearch-jobDescriptionText')
                
#                 if description_elements:
#                     for element in description_elements:
#                         job_description += element.get_text() + " "
#                 else:
#                     # Fallback to main content or body
#                     main_content = soup.select('main, .main-content, article, .job-content')
#                     if main_content:
#                         job_description = main_content[0].get_text()
#                     else:
#                         # Last resort, get all paragraph text
#                         paragraphs = soup.select('p')
#                         job_description = " ".join([p.get_text() for p in paragraphs])
                
#                 # Combine with search results
#                 combined_content = f"{job_description} {search_results}"
#                 return combined_content
            
#             # If direct scraping fails, just return search results
#             return search_results
            
#         except Exception as e:
#             print(f"Error extracting content from URL: {e}")
#             return ""
    
#     def predict(self, text: str) -> float:
#         """Predict if a job posting is fake (1) or legitimate (0)"""
#         with torch.no_grad():
#             inputs = self.preprocess_text(text)
#             outputs = self.bert(**inputs)
#             cls_output = outputs.last_hidden_state[:, 0, :]
#             prediction = self.classifier(cls_output)
#             return prediction.item()
    
#     def check_job_posting(self, url: str, content: Optional[str] = None) -> Dict[str, Union[int, str]]:
#         """Check if a job posting URL contains a fake job posting"""
#         try:
#             # If content is not provided, extract it from the URL
#             if not content:
#                 content = self.extract_content_from_url(url)
            
#             if not content:
#                 return {"is_fake": 1, "source": "error", "confidence": 0.9}
            
#             # Make prediction
#             prediction_score = self.predict(content)
#             is_fake = 1 if prediction_score > 0.5 else 0
            
#             return {
#                 "is_fake": is_fake,
#                 "source": "bert_model",
#                 "confidence": prediction_score if is_fake else 1 - prediction_score
#             }
            
#         except Exception as e:
#             print(f"Error checking job posting: {e}")
#             return {"is_fake": 1, "source": "error", "confidence": 0.9}
import torch
import torch.nn as nn
from transformers import BertModel

class JobPostingClassifier(nn.Module):
    
    def __init__(self, n_classes):
        super(JobPostingClassifier, self).__init__()
        self.bert = BertModel.from_pretrained('bert-base-uncased')
        self.dropout = nn.Dropout(p=0.3)
        self.out = nn.Linear(self.bert.config.hidden_size, n_classes)

    def forward(self, input_ids, attention_mask):
        _, pooled_output = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask,
            return_dict=False
        )
        output = self.dropout(pooled_output)
        logits = self.out(output)
        return torch.softmax(logits,dim=1)
    