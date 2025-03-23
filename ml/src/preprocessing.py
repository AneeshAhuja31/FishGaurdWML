import pandas as pd
import os
import re
from sklearn.model_selection import train_test_split
from bs4 import BeautifulSoup
# def clean_url(url):
#     url = url.strip()
#     if not url.startswith(('http://','https://')):
#         url = 'http://'+url
    
#     while url.endswith('/'): #remove trailing slashes
#         url = url[:-1]
    
#     return url

def process_dataset(input_file,output_dir='ml/data/processed'):
    
    df = pd.read_csv(input_file)

    df = df.drop_duplicates(subset=['url'])

    df = df.dropna(subset=['url'])
    df = df.drop_duplicates(subset=['url'])

    df['label'] = df['status'].map({'phishing':1,'legitimate':0})
    phishing_df = df[df['status'] == 'phishing']
    legitimate_df = df[df['status'] == 'legitimate']

    phishing_df.to_csv(f"{output_dir}/phishing_urls_processed.csv", index=False)
    legitimate_df.to_csv(f"{output_dir}/legitimate_urls_processed.csv", index=False)
    
    return df

def prepare_datasets(input_file,processed_dir='ml/data/processed',test_size=0.2,val_size=0.15):
    df = process_dataset(input_file,processed_dir)
    model_df = df[['url','label']]

    train_df,temp_df = train_test_split(model_df,test_size=test_size+val_size,random_state=42,stratify=model_df['label'])

    val_size = val_size/(test_size+val_size)
    val_df,test_df = train_test_split(temp_df,test_size=1-val_size,random_state=42,stratify=temp_df['label'])

    train_df.to_csv(f"{processed_dir}/train_urls.csv",index=False)
    val_df.to_csv(f"{processed_dir}/val_urls.csv",index=False)
    test_df.to_csv(f"{processed_dir}/test_urls.csv",index=False)

    #for analysis
    combined_df = pd.concat([
        train_df.sample(n=min(5000, len(train_df)), random_state=42),
        val_df.sample(n=min(1000, len(val_df)), random_state=42),
        test_df.sample(n=min(1000, len(test_df)), random_state=42)
    ])
    combined_df.to_csv(f"{processed_dir}/sample_urls.csv", index=False)
    
    print(f"Created datasets:")
    print(f"Training: {len(train_df)} samples")
    print(f"Validation: {len(val_df)} samples")
    print(f"Testing: {len(test_df)} samples")
    print(f"Sample dataset: {len(combined_df)} samples")
    
    # Return dataset sizes for reference
    return {
        'train_size': len(train_df),
        'val_size': len(val_df),
        'test_size': len(test_df),
        'phishing_count': sum(df['label'] == 1),
        'legitimate_count': sum(df['label'] == 0)
    }

def analyze_dataset(input_file, output_dir="ml/data/processed"):
    """Analyze the dataset and generate statistics."""
    df = pd.read_csv(input_file)
    
    # Basic statistics
    total_urls = len(df)
    unique_urls = len(df['url'].unique())
    phishing_count = sum(df['status'] == 'phishing')
    legitimate_count = sum(df['status'] == 'legitimate')
    
    # URL length analysis
    df['url_length'] = df['url'].apply(len)
    avg_length = df['url_length'].mean()
    max_length = df['url_length'].max()
    min_length = df['url_length'].min()
    
    # Domain analysis
    df['domain'] = df['url'].apply(lambda x: x.split('/')[2] if '://' in x and '/' in x.split('://', 1)[1] else '')
    unique_domains = len(df['domain'].unique())
    
    # Schema analysis
    df['has_https'] = df['url'].apply(lambda x: 1 if x.startswith('https://') else 0)
    https_count = sum(df['has_https'])
    http_count = total_urls - https_count
    
    # Create statistics dataframe
    stats = {
        'Metric': [
            'Total URLs', 'Unique URLs', 'Phishing URLs', 'Legitimate URLs',
            'Average URL Length', 'Max URL Length', 'Min URL Length',
            'Unique Domains', 'HTTPS URLs', 'HTTP URLs'
        ],
        'Value': [
            total_urls, unique_urls, phishing_count, legitimate_count,
            avg_length, max_length, min_length,
            unique_domains, https_count, http_count
        ]
    }
    
    stats_df = pd.DataFrame(stats)
    stats_df.to_csv(f"{output_dir}/dataset_statistics.csv", index=False)
    
    print(f"Dataset statistics saved to {output_dir}/dataset_statistics.csv")
    
    # Return key statistics
    return {
        'total_urls': total_urls,
        'phishing_percent': (phishing_count / total_urls) * 100,
        'legitimate_percent': (legitimate_count / total_urls) * 100,
        'avg_length': avg_length,
        'https_percent': (https_count / total_urls) * 100
    }

if __name__ == "__main__":
    # Example usage
    input_file = r"C:\Users\HP\OneDrive\Desktop\FISHGUARD\ml\data\raw\dataset_phishing.csv"
    processed_dir = "ml/data/processed"
    
    # Ensure directories exist
    os.makedirs(processed_dir, exist_ok=True)
    
    # Process and prepare datasets
    stats = prepare_datasets(input_file, processed_dir)
    print("\nDataset preparation complete!")
    
    # Analyze the dataset
    analysis = analyze_dataset(input_file, processed_dir)
    print("\nDataset analysis complete!")
    print(f"Total URLs: {analysis['total_urls']}")
    print(f"Phishing URLs: {analysis['phishing_percent']:.2f}%")
    print(f"Legitimate URLs: {analysis['legitimate_percent']:.2f}%")
    print(f"Average URL length: {analysis['avg_length']:.2f} characters")
    print(f"HTTPS usage: {analysis['https_percent']:.2f}%")