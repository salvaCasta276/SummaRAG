import re
import json
from bs4 import BeautifulSoup

def clean_content(content):
    # Parse the HTML
    soup = BeautifulSoup(content, 'html.parser')

    # Remove script and style elements
    for element in soup(["script", "style"]):
        element.decompose()

    # Remove SVG elements
    for svg in soup.find_all('svg'):
        svg.decompose()

    # Extract text
    text = soup.get_text()

    # Handle MathJax content
    text = re.sub(r'\$\$(.*?)\$\$', r'\1', text)  # Replace inline math with its content
    text = re.sub(r'\\\[(.*?)\\\]', r'\1', text)  # Replace display math with its content

    # Remove excessive whitespace and newlines
    text = re.sub(r'\s+', ' ', text).strip()

    # Remove any remaining HTML entities
    text = re.sub(r'&[a-z]+;', '', text)

    return text

def process_posts(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        posts = json.load(f)
    
    cleaned_posts = []
    for post in posts:
        cleaned_post = {
            'url': post['url'],
            'title': clean_content(' '.join(post['title'])),
            'author': clean_content(' '.join(post['author'])),
            'date': post['date'][0],
            'content': clean_content(post['content'])
        }
        cleaned_posts.append(cleaned_post)
    
    return cleaned_posts

# Usage
cleaned_posts = process_posts('posts.json')

# Save cleaned posts
with open('cleaned_posts.json', 'w', encoding='utf-8') as f:
    json.dump(cleaned_posts, f, ensure_ascii=False, indent=2)