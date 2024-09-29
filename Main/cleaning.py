import re
import json

def clean_content(text):
    # Remove CSS selectors and their declarations
    cleaned = re.sub(r'\.[\w-]+(?:\s*>\s*\*|\s*\+\s*\.[\w-]+|\[[\w\[\]:^$*]+\])?(?:\s*,\s*\.[\w-]+(?:\s*>\s*\*|\s*\+\s*\.[\w-]+|\[[\w\[\]:^$*]+\])?)*\s*(\{[^}]*\})?', '', text)
    
    # Remove @font-face declarations
    cleaned = re.sub(r'@font-face\s*\{[^}]*\}', '', cleaned)
    
    # Remove any remaining @font-face references
    cleaned = re.sub(r'@font-face', '', cleaned)
    
    # Remove <script> and <style> tags and their content
    cleaned = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', cleaned, flags=re.DOTALL)
    
    # Remove HTML tags and extra spaces
    cleaned = re.sub(r'<[^>]+>', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    return cleaned.strip()

def process_posts(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        posts = json.load(f)
    
    cleaned_posts = []
    for post in posts:
        cleaned_post = {
            'url': post['url'],
            'title': post['title'],
            'author': post['author'],
            'date': post['date'][0],
            'content': clean_content(post['content'])
        }
        cleaned_posts.append(cleaned_post)
    
    return cleaned_posts

# Usage
cleaned_posts = process_posts('posts.json')

# Save cleaned posts
with open('cleaned_posts.json', 'w', encoding='utf-8') as f:
    json.dump(cleaned_posts, f, ensure_ascii=False, indent=4)