import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from datetime import datetime
import os
import requests
from io import BytesIO
from PIL import Image
import hashlib
import tempfile
import shutil

def download_image(url, temp_dir):
    """Download image from URL and save to a temporary directory."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Generate a unique filename
        image_hash = hashlib.md5(response.content).hexdigest()
        image_ext = os.path.splitext(url)[1]
        if not image_ext:
            image_ext = '.jpg'  # Default to .jpg if no extension is found
        image_filename = f"image_{image_hash}{image_ext}"
        
        # Save the image to the temporary directory
        temp_path = os.path.join(temp_dir, image_filename)
        with open(temp_path, 'wb') as f:
            f.write(response.content)
        print('Downloaded image:', image_filename)

        return image_filename
    except requests.RequestException as e:
        print(f"Error downloading image {url}: {e}")
        return None

def create_chapter(title, content, file_name):
    """Create an EPUB chapter from HTML content."""
    chapter = epub.EpubHtml(title=title, file_name=file_name, lang='en')
    chapter.content = f'<h1>{title}</h1>\n{content}'
    return chapter

def generate_epub(articles_by_source, output_path, weather_data):
    """Generate an EPUB file from the articles and weather data."""
    book = epub.EpubBook()

    # Create a temporary directory for images
    with tempfile.TemporaryDirectory() as temp_dir:
        # Set metadata
        book.set_identifier(f'ReMarkNews-{datetime.now().strftime("%Y%m%d")}')
        book.set_title('ReMarkNews')
        book.set_language('en')
        book.add_author('ReMarkNews Generator')

        # Create chapters
        chapters = []
        toc = []

        # Add weather information
        if weather_data:
            weather_html = f"""
            <p>Location: Madrid</p>
            <p>Min/Max Temp: {weather_data['temp_min']}/{weather_data['temp_max']}°C</p>
            <p>Rain Probability: {weather_data['rain_prob']}%</p>
            <p>Forecast: {weather_data['description']}</p>
            """
            weather_chapter = create_chapter('Weather', weather_html, 'weather.xhtml')
            book.add_item(weather_chapter)
            chapters.append(weather_chapter)
            toc.append(epub.Link('weather.xhtml', 'Weather', 'weather'))

        for source, articles in articles_by_source.items():
            source_toc = []
            source_html = f"<h1>{source}</h1>"
            for index, article in enumerate(articles):
                article_id = f"{source.lower().replace(' ', '_')}_{index}"
                article_file_name = f"{article_id}.xhtml"
                article_html = f"<h2>{article['title']}</h2>"
                article_html += f"<p><i>Published: {article['pubDate']}</i></p>"
                
                for item_type, item in article['full_content']:
                    if item_type == 'text':
                        # Split the text into paragraphs and wrap each in <p> tags
                        paragraphs = item.split('\n\n')  # Assuming paragraphs are separated by blank lines
                        for paragraph in paragraphs:
                            article_html += f"<p>{paragraph.strip()}</p>"
                    elif item_type == 'image':
                        image_filename = download_image(item['url'], temp_dir)
                        if image_filename:
                            # Add image to the book
                            book_image = epub.EpubImage()
                            book_image.file_name = f"images/{image_filename}"
                            _, image_ext = os.path.splitext(image_filename)
                            book_image.media_type = f"image/{image_ext[1:]}"
                            with open(os.path.join(temp_dir, image_filename), 'rb') as img_file:
                                book_image.content = img_file.read()
                            book.add_item(book_image)
                            
                            # Add image to the HTML content
                            article_html += f'<p><img src="images/{image_filename}" alt="{item['alt']}"/></p>'
                            if item.get('caption'):
                                article_html += f"<p><i>{item['caption']}</i></p>"
                        else:
                            article_html += f"<p>[Image could not be downloaded: {item['alt']}]</p>"

                article_chapter = create_chapter(article['title'], article_html, article_file_name)
                book.add_item(article_chapter)
                chapters.append(article_chapter)
                source_toc.append(epub.Link(article_file_name, article['title'], article_id))

            toc.append((epub.Section(source), source_toc))

        # Add chapters to the book
        for chapter in chapters:
            book.add_item(chapter)

        # Define Table of Contents
        book.toc = toc

        # Add default NCX and Nav file
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # Define CSS style
        style = '''
        body { font-family: Arial, sans-serif; }
        h1 { color: #333; }
        h2 { color: #666; }
        img { max-width: 100%; height: auto; }
        '''
        nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
        book.add_item(nav_css)

        # Set the spine of the book
        book.spine = ['nav'] + chapters

        # Write EPUB file
        epub_filename = f"{output_path}.epub"
        epub.write_epub(epub_filename, book, {})

        print(f"EPUB created successfully: {epub_filename}")

    return epub_filename