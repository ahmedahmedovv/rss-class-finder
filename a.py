import requests
from bs4 import BeautifulSoup
from transformers import pipeline

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
            if cls not in class_content:
                class_content[cls] = []
            class_content[cls].append(tag.get_text(strip=True))

# Step 4: Set up a Hugging Face model if needed
# For example, using a text classification model
classifier = pipeline("text-classification", model="xlm-roberta-large")

# Step 5: Save the classes and their content to a markdown file with UTF-8 encoding
with open("html_classes_with_content.md", "w", encoding="utf-8") as file:
    file.write("# HTML Classes and their Content:\n")
    for cls, contents in class_content.items():
        file.write(f"## {cls}\n")
        for content in contents:
            if content:  # Only write non-empty content
                file.write(f"- {content}\n")
        file.write("\n")

# If you need to classify or analyze the text, you can use the classifier
# Example: result = classifier("Some text to classify")
