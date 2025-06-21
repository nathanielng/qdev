#!/usr/bin/env python

import boto3
import json
import hashlib
import os
import requests
import time

from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

# Configuration
HTML_CACHE_DIR = "./html"
JSON_OUTPUT_FILE = os.environ.get("JSON_OUTPUT_FILE", "url_data.json")
MAX_WORKERS = 5
REQUEST_TIMEOUT = 10
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# Create cache directory if it doesn't exist
os.makedirs(HTML_CACHE_DIR, exist_ok=True)

def get_filename_from_url(url):
    """Generate a filename from URL using hash to avoid filesystem issues"""
    url_hash = hashlib.md5(url.encode()).hexdigest()
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.replace(".", "_")
    return f"{domain}_{url_hash}.html"

def fetch_html(url):
    """Fetch HTML content from URL or retrieve from cache"""
    filename = get_filename_from_url(url)
    cache_path = os.path.join(HTML_CACHE_DIR, filename)
    
    # Check if cached version exists
    if os.path.exists(cache_path):
        print(f"Using cached version for {url}")
        with open(cache_path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    
    # Fetch from web
    try:
        print(f"Fetching {url}")
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        html_content = response.text
        
        # Cache the content
        with open(cache_path, 'w', encoding='utf-8', errors='replace') as f:
            f.write(html_content)
        
        # Be nice to servers
        time.sleep(1)
        return html_content
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_content(url, html_content):
    """Extract title and body text from HTML"""
    if not html_content:
        return {"url": url, "title": "", "body": ""}
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract title
        title = ""
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)
        
        # Extract body text
        # First try to find main content areas
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
        
        if main_content:
            # Extract text from main content
            paragraphs = main_content.find_all('p')
            body = ' '.join([p.get_text(strip=True) for p in paragraphs])
        else:
            # Fallback to all paragraphs
            paragraphs = soup.find_all('p')
            body = ' '.join([p.get_text(strip=True) for p in paragraphs])
        
        # Truncate body if it's too long (to avoid issues with Bedrock API limits)
        if len(body) > 10000:
            body = body[:10000] + "..."
            
        return {"url": url, "title": title, "body": body}
    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
        return {"url": url, "title": "", "body": ""}

def generate_hashtags(title, body):
    """Generate hashtags using Amazon Bedrock Nova model"""
    try:
        # Initialize Bedrock client
        bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-west-2')
        
        # Prepare prompt for Nova
        prompt = f"""
        Based on the following title and content, suggest 3-5 relevant hashtags.
        Return only the hashtags separated by spaces, without any explanation.
        
        Title: {title}
        
        Content: {body[:1000]}  # Limit content to avoid token limits
        """
        
        # Call Bedrock Nova model
        response = bedrock_runtime.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',  # Using Claude 3 Sonnet
            contentType='application/json',
            accept='application/json',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 100,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
        )
        
        # Parse response
        response_body = json.loads(response['body'].read().decode('utf-8'))
        hashtags = response_body['content'][0]['text'].strip()
        
        return hashtags
    except Exception as e:
        print(f"Error generating hashtags: {e}")
        return ""

def process_url(url):
    """Process a single URL: fetch HTML, extract content, generate hashtags"""
    html_content = fetch_html(url)
    content_data = extract_content(url, html_content)
    
    # Generate hashtags if we have content
    if content_data["title"] or content_data["body"]:
        hashtags = generate_hashtags(content_data["title"], content_data["body"])
        content_data["hashtags"] = hashtags
    else:
        content_data["hashtags"] = ""
    
    return content_data

def process_urls_from_file(input_file):
    """Process all URLs from input file"""
    # Read URLs from file
    with open(input_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    results = []
    
    # Process URLs in parallel
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = list(executor.map(process_url, urls))
    
    # Write results to JSON
    with open(JSON_OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"Processed {len(results)} URLs. Results saved to {JSON_OUTPUT_FILE}")

def update_json_with_hashtags():
    """Update existing JSON with hashtags"""
    if not os.path.exists(JSON_OUTPUT_FILE):
        print(f"JSON file {JSON_OUTPUT_FILE} not found")
        return
    
    # Read existing JSON
    with open(JSON_OUTPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Check if any entry is missing hashtags
    missing_hashtags = False
    for entry in data:
        if "hashtags" not in entry or not entry["hashtags"]:
            missing_hashtags = True
            break
    
    if not missing_hashtags:
        print("Hashtags already exist for all entries")
        return
    
    # Generate hashtags for each entry
    for entry in data:
        if "hashtags" not in entry or not entry["hashtags"]:
            hashtags = generate_hashtags(entry["title"], entry["body"])
            entry["hashtags"] = hashtags
            print(f"Generated hashtags for {entry['url']}: {hashtags}")
    
    # Save updated JSON
    with open(JSON_OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print(f"Updated {JSON_OUTPUT_FILE} with hashtags")

if __name__ == "__main__":
    
    input_file = "extracted-urls-2025-06-13.txt"
    
    # Check if JSON already exists
    if os.path.exists(JSON_OUTPUT_FILE):
        print(f"JSON file {JSON_OUTPUT_FILE} already exists.")
        choice = input("Do you want to (1) process URLs again, (2) update with hashtags only, or (3) exit? ")
        
        if choice == "1":
            process_urls_from_file(input_file)
        elif choice == "2":
            update_json_with_hashtags()
        else:
            print("Exiting without changes")
    else:
        # Process URLs from scratch
        process_urls_from_file(input_file)
