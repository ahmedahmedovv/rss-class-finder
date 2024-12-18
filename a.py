import requests
from bs4 import BeautifulSoup
from transformers import pipeline
import json

# Step 1: Fetch the webpage content
url = "https://www.polskieradio.pl/399/8097"
response = requests.get(url)
web_content = response.text

# Step 2: Parse the HTML content
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

# Additional filtering to ensure classes with only one article are skipped
class_content = {cls: articles for cls, articles in class_content.items() if len(articles) > 1}

# Step 4: Set up a Hugging Face model if needed
# For example, using a text classification model
classifier = pipeline("text-classification", model="xlm-roberta-large")

# Step 5: Save the classes and their content to a JSON file with UTF-8 encoding
with open("html_classes_with_content.json", "w", encoding="utf-8") as file:
    json.dump(class_content, file, ensure_ascii=False, indent=4)

# If you need to classify or analyze the text, you can use the classifier
# Example: result = classifier("Some text to classify")
