import requests
from bs4 import BeautifulSoup
import json
import webbrowser
from datetime import datetime
import os

# Step 1: Fetch the webpage content
url = "https://www.polskieradio.pl/399/8097"
response = requests.get(url)
web_content = response.text

# Step 2: Create BeautifulSoup object
soup = BeautifulSoup(web_content, 'html.parser')

# Step 3: Extract all HTML classes and their content
class_content = {}
for tag in soup.find_all(True):  # True finds all tags
    if 'class' in tag.attrs:
        for cls in tag.attrs['class']:
            text = tag.get_text(strip=True)
            if text:  # Only add non-empty text
                if cls not in class_content:
                    class_content[cls] = []
                class_content[cls].append(text)

# Remove classes with only one article, duplicated articles, or articles with only one word
class_content = {
    cls: [article for article in articles if len(article.split()) > 1]
    for cls, articles in class_content.items()
    if len(articles) > 1 and len(set(articles)) == len(articles)
}

def create_html_report(class_content):
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Content Class Analysis Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .class-container { 
                margin: 20px 0;
                padding: 15px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            .class-name { 
                font-weight: bold;
                color: #333;
                margin-bottom: 10px;
                background-color: #f0f0f0;
                padding: 5px;
                border-radius: 3px;
            }
            .article {
                margin: 10px 0;
                padding: 10px;
                background-color: #f9f9f9;
                border-radius: 3px;
                border-left: 3px solid #4CAF50;
            }
            .stats {
                color: #666;
                font-size: 0.9em;
                margin-top: 5px;
            }
        </style>
    </head>
    <body>
        <h1>Website Content Classes Report</h1>
        <p>Generated on: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
        <p>URL: """ + url + """</p>
    """

    # Add all classes and their content
    for cls, articles in class_content.items():
        html_content += f"""
        <div class="class-container">
            <div class="class-name">Class: {cls}</div>
            <div class="stats">Number of articles: {len(articles)}</div>
        """
        for article in articles:
            html_content += f"""
            <div class="article">
                {article}
            </div>
            """
        html_content += "</div>"

    html_content += """
    </body>
    </html>
    """

    # Save the HTML file
    report_path = "content_classes_report.html"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    # Open in browser
    webbrowser.open('file://' + os.path.realpath(report_path))

# Create and open the HTML report
create_html_report(class_content)

# Save the classes and their content to a JSON file
with open("html_classes_with_content.json", "w", encoding="utf-8") as file:
    json.dump(class_content, file, ensure_ascii=False, indent=4)
