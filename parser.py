import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from scrapper import extract_article_all

def fetch_rss(url):
    """
    Fetch RSS content from a given URL.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        print(f"Error fetching RSS feed: {e}")
        return None

def parse_rss(content, hours=24):
    """
    Parse RSS content and return a list of articles from the last specified hours.
    """
    articles = []
    try:
        root = ET.fromstring(content)
        current_time = datetime.now(timezone.utc)
        time_threshold = current_time - timedelta(hours=hours)
        
        for item in root.findall('.//item'):
            pub_date_str = item.find('pubDate').text if item.find('pubDate') is not None else ''
            if pub_date_str:
                pub_date = parsedate_to_datetime(pub_date_str)
                if pub_date > time_threshold:
                    article = {
                        'title': item.find('title').text if item.find('title') is not None else '',
                        'link': item.find('link').text if item.find('link') is not None else '',
                        'description': item.find('description').text if item.find('description') is not None else '',
                        'pubDate': pub_date_str
                    }
                    articles.append(article)
    except ET.ParseError as e:
        print(f"Error parsing RSS content: {e}")
    return articles

def extract_text_from_html(html_content):
    """
    Extract plain text from HTML content.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text(separator=' ', strip=True)

def process_rss_feed(url, hours=24):
    """
    Process an RSS feed: fetch, parse, and extract full content for articles from the last specified hours.
    """
    content = fetch_rss(url)
    if content:
        articles = parse_rss(content, hours)
        for article in articles:
            article['summary'] = extract_text_from_html(article['description'])
            article['full_content'] = extract_article_all(article['link'])
        return articles
    return []