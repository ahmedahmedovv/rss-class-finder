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

# Modified filtering of classes
class_content = {
    cls: articles 
    for cls, articles in class_content.items()
    if len(articles) > 1  # Only keep classes with more than one article
    and len(set(articles)) == len(articles)  # Remove duplicates
    and all(len(article.split()) > 1 for article in articles)  # Skip single-word articles
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
            .class-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 10px;
                background-color: #f0f0f0;
                padding: 10px;
                border-radius: 3px;
            }
            .class-info {
                flex-grow: 1;
            }
            .class-name { 
                font-weight: bold;
                color: #333;
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
            .export-button {
                padding: 5px 15px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 3px;
                cursor: pointer;
                margin-left: 15px;
            }
            .export-button:hover {
                background-color: #45a049;
            }
        </style>
        <script>
            function exportClass(className, articles) {
                const jsonData = JSON.stringify({ [className]: articles }, null, 2);
                const blob = new Blob([jsonData], { type: 'application/json' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `class_${className}.json`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                alert(`Class "${className}" exported successfully!`);
            }
        </script>
    </head>
    <body>
        <h1>Website Content Classes Report</h1>
        <p>Generated on: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
        <p>URL: """ + url + """</p>
        <div class="summary">
            <p>Total number of classes with multiple articles: {len(class_content)}</p>
        </div>
    """

    # Add all classes and their content
    for cls, articles in class_content.items():
        if len(articles) > 1:
            # Convert articles list to JSON string for JavaScript
            articles_json = json.dumps(articles, ensure_ascii=False)
            
            html_content += f"""
            <div class="class-container">
                <div class="class-header">
                    <div class="class-info">
                        <div class="class-name">Class: {cls}</div>
                        <div class="stats">Number of articles: {len(articles)}</div>
                    </div>
                    <button class="export-button" 
                            onclick='exportClass("{cls}", {articles_json})'>
                        Export to JSON
                    </button>
                </div>
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
