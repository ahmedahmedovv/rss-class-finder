import requests
from bs4 import BeautifulSoup
from supabase import create_client
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import pytz
from feedgen.feed import FeedGenerator
from urllib.parse import urlparse

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

def analyze_page(url, class_name):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    articles = []
    elements = soup.find_all(class_=class_name)
    
    for element in elements:
        text = element.get_text().strip()
        if text and len(text.split()) > 1:
            articles.append(text)
    
    return articles

def update_rss_feed(url, class_name, articles):
    fg = FeedGenerator()
    fg.title(f'HTML Class Content: {class_name}')
    fg.description(f'Content extracted from HTML elements with class "{class_name}"')
    fg.link(href=url)
    fg.language('en')
    
    current_time = datetime.now(pytz.UTC)
    
    for article in articles:
        fe = fg.add_entry()
        fe.title(article[:50] + '...' if len(article) > 50 else article)
        fe.description(article)
        fe.link(href=url)
        fe.pubDate(current_time)
    
    return fg.rss_str(pretty=True)

def main():
    # Get all existing feeds from Supabase storage
    files = supabase.storage.from_('class-analysis').list()
    
    for file in files:
        try:
            # Parse filename to get original URL and class name
            filename = file['name']
            if not filename.endswith('.xml'):
                continue
                
            parts = filename.split('_class_')
            if len(parts) != 2:
                continue
                
            domain = parts[0]
            class_name = parts[1].split('_')[0]
            
            # Reconstruct URL (assuming http/https)
            url = f"https://{domain}"
            
            # Get fresh content
            articles = analyze_page(url, class_name)
            
            if articles:
                # Generate new RSS feed
                rss_content = update_rss_feed(url, class_name, articles)
                
                # Update the file in Supabase
                supabase.storage \
                    .from_('class-analysis') \
                    .update(filename, rss_content)
                
                print(f"Updated feed for {url} - class: {class_name}")
            
        except Exception as e:
            print(f"Error updating {filename}: {str(e)}")

if __name__ == "__main__":
    main() 