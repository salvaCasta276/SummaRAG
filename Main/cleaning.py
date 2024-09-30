import re
import json

def clean_content(text):
    # Remove CSS-like selectors and their declarations
    cleaned = re.sub(r'(\s*:\s*focus\s*,?\s*body\s*:\s*focus\s*\*\s*\{[^}]*\})', '', text)
    cleaned = re.sub(r'(\s*>\s*>\s*>\s*>\s*>\s*\*\s*\{[^}]*\})', '', cleaned)
    cleaned = re.sub(r'(\s*>\s*svg\s*\{[^}]*\})', '', cleaned)
    cleaned = re.sub(r'\.[\w-]+(?:\s*>\s*\*|\s*\+\s*\.[\w-]+|\[[\w\[\]:^$*]+\])?(?:\s*,\s*\.[\w-]+(?:\s*>\s*\*|\s*\+\s*\.[\w-]+|\[[\w\[\]:^$*]+\])?)*\s*(\{[^}]*\})?', '', cleaned)
    cleaned = re.sub(r'@font-face\s*\{[^}]*\}', '', cleaned)
    cleaned = re.sub(r'@font-face', '', cleaned)
    cleaned = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', cleaned, flags=re.DOTALL)
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
