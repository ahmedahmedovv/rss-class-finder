from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup
import requests
import os
from supabase import create_client, Client
from dotenv import load_dotenv
import json
import time
from feedgen.feed import FeedGenerator
from datetime import datetime
import pytz
from urllib.parse import urlparse

load_dotenv()

app = Flask(__name__)

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')

if not supabase_url or not supabase_key:
    raise ValueError("Missing required environment variables: SUPABASE_URL and SUPABASE_KEY must be set")

try:
    supabase: Client = create_client(
        supabase_url=supabase_url,
        supabase_key=supabase_key,
        options={
            'headers': {
                'Authorization': f'Bearer {supabase_key}'
            }
        }
    )
except Exception as e:
    print(f"Error initializing Supabase client: {str(e)}")
    raise

def analyze_classes(html_content):
    # Parse HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    class_content = {}
    
    # Find all elements
    all_elements = soup.find_all(class_=True)
    
    # Analyze classes
    for element in all_elements:
        classes = element.get('class', [])
        text = element.get_text().strip()
        
        if text:
            for cls in classes:
                if cls not in class_content:
                    class_content[cls] = set()
                class_content[cls].add(text)
    
    # Filter and convert to dict
    filtered_content = {
        cls: list(texts)
        for cls, texts in class_content.items()
        if len(texts) > 1 and all(len(text.split()) > 1 for text in texts)
    }
    
    return filtered_content

def create_rss_feed(class_name, articles, base_url):
    fg = FeedGenerator()
    fg.title(f'HTML Class Content: {class_name}')
    fg.description(f'Content extracted from HTML elements with class "{class_name}"')
    fg.link(href=base_url)  # Use actual base URL
    fg.language('en')
    
    current_time = datetime.now(pytz.UTC)
    
    for article in articles:
        fe = fg.add_entry()
        fe.title(article[:50] + '...' if len(article) > 50 else article)
        fe.description(article)
        fe.link(href=base_url)  # Use actual base URL
        fe.pubDate(current_time)
    
    return fg.rss_str(pretty=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    url = request.json.get('url')
    try:
        response = requests.get(url)
        results = analyze_classes(response.text)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/save-to-supabase', methods=['POST'])
def save_to_supabase():
    try:
        data = request.json
        class_name = data.get('className')
        articles = data.get('articles')
        base_url = data.get('baseUrl')
        
        if not all([class_name, articles, base_url]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Generate RSS feed with base URL
        rss_content = create_rss_feed(class_name, articles, base_url)
        
        # Create filename using base URL
        domain = urlparse(base_url).netloc
        filename = f"{domain}_class_{class_name}_{int(time.time())}.xml"
        
        try:
            # Upload to Supabase Storage
            result = supabase.storage \
                .from_('class-analysis') \
                .upload(filename, rss_content)
                
            # Get public URL
            file_url = supabase.storage \
                .from_('class-analysis') \
                .get_public_url(filename)
                
            return jsonify({
                'success': True,
                'url': file_url,
                'format': 'RSS'
            })
        except Exception as storage_error:
            print(f"Supabase storage error: {str(storage_error)}")
            return jsonify({'error': 'Storage operation failed'}), 500
            
    except Exception as e:
        print(f"General error: {str(e)}")
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True) 