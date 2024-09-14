import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, urljoin
from PIL import Image
from io import BytesIO

def extract_article_text(url):
    """
    Extract the main article text from a given URL.
    """
    try:
        # Fetch the webpage
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Find the main content (this may need adjustment based on the website structure)
        main_content = soup.find('article') or soup.find('main') or soup.find('div', class_=re.compile('(content|article)'))
        
        if main_content:
            # Extract text from paragraphs within the main content
            paragraphs = main_content.find_all('p')
            text = ' '.join([p.get_text().strip() for p in paragraphs])
        else:
            # Fallback: get all text if no main content is identified
            text = soup.get_text()
        
        # Clean up the text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text

    except requests.RequestException as e:
        print(f"Error fetching or parsing the webpage: {e}")
        return None



def is_valid_image_url(url):
    """
    Check if a given URL is likely to be a valid image URL.
    """
    if not url:
        return False
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme) and any(parsed.path.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp'])

def get_image_size(url):
    """
    Get the size of an image from its URL.
    """
    try:
        response = requests.get(url, stream=True, timeout=5)
        img = Image.open(BytesIO(response.content))
        return img.size
    except Exception as e:
        print(f"Error getting image size: {e}")
        return (0, 0)

def extract_image_url(img_element, base_url):
    """
    Extract the most likely image URL from an img element.
    """
    url_attributes = ['data-src', 'data-original', 'src']
    for attr in url_attributes:
        url = img_element.get(attr)
        if is_valid_image_url(url):
            return urljoin(base_url, url)
    return None

def is_high_quality_image(url, min_width=300, min_height=200):
    """
    Check if an image meets minimum quality standards.
    """
    width, height = get_image_size(url)
    return width >= min_width and height >= min_height

# def extract_article_all(url):
#     """
#     Extract the main article text and image URLs from a given URL,
#     maintaining the relative positioning of images within the text.
#     """
#     try:
#         # Fetch the webpage
#         response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
#         response.raise_for_status()
        
#         # Parse the HTML content
#         soup = BeautifulSoup(response.text, 'html.parser')
        
#         # Remove script and style elements
#         for script in soup(["script", "style"]):
#             script.decompose()
        
#         # Find the main content
#         main_content = soup.find('article') or soup.find('main') or soup.find('div', class_=re.compile('(content|article)'))
        
#         if not main_content:
#             main_content = soup  # Fallback to entire body if no main content is identified
        
#         # Extract text and images, maintaining order
#         content = []
#         for element in main_content.descendants:
#             if element.name == 'p':
#                 text = element.get_text().strip()
#                 if text:
#                     content.append(('text', text))
#             elif element.name == 'img':
#                 src = extract_image_url(element, url)
#                 alt = element.get('alt', '')
#                 caption = element.find_next('figcaption')
#                 caption_text = caption.get_text().strip() if caption else ''
                
#                 if src and is_high_quality_image(src) and (alt or caption_text):
#                     content.append(('image', {'url': src, 'alt': alt, 'caption': caption_text}))
        
#         # Combine text elements for readability
#         combined_content = []
#         current_text = []
#         for item_type, item in content:
#             if item_type == 'text':
#                 current_text.append(item)
#             else:  # image
#                 if current_text:
#                     combined_content.append(('text', ' '.join(current_text)))
#                     current_text = []
#                 combined_content.append((item_type, item))
#         if current_text:
#             combined_content.append(('text', ' '.join(current_text)))
        
#         return combined_content

#     except requests.RequestException as e:
#         print(f"Error fetching or parsing the webpage: {e}")
#         return None


def extract_article_all(url):
    """
    Extract the main article text and image URLs from a given URL,
    maintaining the relative positioning of images within the text and preserving paragraph structure.
    """
    try:
        # Fetch the webpage
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Find the main content
        main_content = soup.find('article') or soup.find('main') or soup.find('div', class_=re.compile('(content|article)'))
        
        if not main_content:
            main_content = soup  # Fallback to entire body if no main content is identified
        
        # Extract text and images, maintaining order and paragraph structure
        content = []
        current_paragraph = []
        
        for element in main_content.descendants:
            if element.name == 'p':
                if current_paragraph:
                    content.append(('text', '\n\n'.join(current_paragraph)))
                    current_paragraph = []
                text = element.get_text().strip()
                if text:
                    current_paragraph.append(text)
            elif element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                if current_paragraph:
                    content.append(('text', '\n\n'.join(current_paragraph)))
                    current_paragraph = []
                text = element.get_text().strip()
                if text:
                    content.append(('text', f"\n\n{text}\n"))
            elif element.name == 'img':
                if current_paragraph:
                    content.append(('text', '\n\n'.join(current_paragraph)))
                    current_paragraph = []
                src = extract_image_url(element, url)
                alt = element.get('alt', '')
                caption = element.find_next('figcaption')
                caption_text = caption.get_text().strip() if caption else ''
                
                if src and is_high_quality_image(src) and (alt or caption_text):
                    content.append(('image', {'url': src, 'alt': alt, 'caption': caption_text}))
        
        # Add any remaining paragraph text
        if current_paragraph:
            content.append(('text', '\n\n'.join(current_paragraph)))
        
        return content

    except requests.RequestException as e:
        print(f"Error fetching or parsing the webpage: {e}")
        return None




# Example usage
if __name__ == "__main__":
    url = "https://www.lavanguardia.com/politica/20240905/9914032/presidenta-ts-pide-cesen-ataques-injustificados-socavan-legitimidad-jueces.html"
    # article_text = extract_article_text(url)
    article_content = extract_article_all(url)
    if article_content:
        for item_type, item in article_content:
            if item_type == 'text':
                print(f"Text: {item[:100]}...")  # Print first 100 characters of each text block
            else:  # image
                print(f"Image: {item['url']} (Alt: {item['alt']})")
    else:
        print("Failed to extract article content.")