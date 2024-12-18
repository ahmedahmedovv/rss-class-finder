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
    files = supabase.storage.from_('class-analysis').list()
    print(f"Total files found: {len(files)}")
    
    for file in files:
        try:
            filename = file['name']
            print(f"\nProcessing file: {filename}")
            
            if not filename.endswith('.xml'):
                print(f"Skipping: Not an XML file")
                continue
                
            parts = filename.split('_class_', 1)
            if len(parts) != 2:
                print(f"Skipping: Invalid filename format")
                continue
            
            # Remove any existing http:__ or https:__ prefix
            url_part = parts[0]
            if url_part.startswith('http:__'):
                url_part = url_part[7:]
            elif url_part.startswith('https:__'):
                url_part = url_part[8:]
            
            # Replace double underscores with forward slashes
            url = f"https://{url_part.replace('__', '/')}"
            class_name = parts[1].split('_')[0]
                
            print(f"Attempting to fetch: {url}")
            
            articles = analyze_page(url, class_name)
            print(f"Found {len(articles)} articles for class '{class_name}'")
            
            if articles:
                rss_content = update_rss_feed(url, class_name, articles)
                
                supabase.storage \
                    .from_('class-analysis') \
                    .update(filename, rss_content)
                
                print(f"Updated feed for {url} - class: {class_name}")
            else:
                print(f"No articles found for {url} with class '{class_name}'")
            
        except Exception as e:
            print(f"Error updating {filename}: {str(e)}")

if __name__ == "__main__":
    main() 