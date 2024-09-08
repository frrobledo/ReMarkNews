import os
import shutil
import requests
from datetime import datetime
from parser import process_rss_feed
from urllib.parse import urlparse
from pathlib import Path
import re

def escape_latex(text):
    """
    Escape special LaTeX characters and remove problematic Unicode characters.
    """
    special_chars = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
        '\\': r'\textbackslash{}',
    }
    
    # First, escape the special LaTeX characters
    escaped_text = ''.join(special_chars.get(c, c) for c in text)
    
    # Remove or replace problematic Unicode characters
    escaped_text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\xFF]', '', escaped_text)
    
    # Replace other common Unicode characters
    escaped_text = escaped_text.replace(''', "'").replace(''', "'").replace('"', "``").replace('"', "''")
    escaped_text = escaped_text.replace('–', '--').replace('—', '---').replace('…', '...')
    
    return escaped_text

def download_image(url, output_dir):
    """
    Download an image from a URL and save it to the output directory.
    Returns the local path to the saved image.
    """
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        
        # Extract filename from URL
        filename = os.path.basename(urlparse(url).path)
        if not filename:
            filename = 'image.jpg'  # Default filename if none is found in URL
        
        # Ensure unique filename
        local_path = Path(output_dir) / filename
        counter = 1
        while local_path.exists():
            name, ext = os.path.splitext(filename)
            local_path = Path(output_dir) / f"{name}_{counter}{ext}"
            counter += 1
        
        with open(local_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        return str(local_path)
    except Exception as e:
        print(f"Error downloading image {url}: {e}")
        return None
    

def get_weather_data(api_key, lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            'temperature': round(data['main']['temp']),
            'description': data['weather'][0]['description'].capitalize(),
            'icon': data['weather'][0]['icon']
        }
    else:
        return None

def create_latex_document(articles_by_source, image_dir, weather_data):
    """
    Create the LaTeX document content.
    """
    latex_content = [
        r"\documentclass[18pt,a4paper,twocolumn]{article}",
        r"\usepackage[utf8]{inputenc}",
        r"\usepackage[T1]{fontenc}",
        r"\usepackage{graphicx}",
        r"\usepackage{hyperref}",
        r"\usepackage{url}",
        r"\usepackage[margin=1in]{geometry}",
        r"\usepackage{fancyhdr}",
        r"\usepackage{ragged2e}",
        r"\usepackage{tikz}",
        r"\usepackage[utf8]{inputenc}",  # Ensure UTF-8 input encoding
        r"\usepackage{fontspec}",  # For better Unicode support
        # r"\setmainfont{DejaVu Serif}",  # Use a font with good Unicode coverage
        r"\pagestyle{fancy}",
        r"\fancyhead{}",
        r"\fancyfoot{}",
        r"\fancyfoot[C]{\thepage}",
        r"\renewcommand{\headrulewidth}{0pt}",
        r"\renewcommand{\footrulewidth}{0.4pt}",
        r"\setlength{\columnsep}{1cm}",
        r"\setlength{\emergencystretch}{3em}",
        r"\tolerance=1000",
        r"\title{ReMarkNews}",
        fr"\date{{{datetime.now().strftime('%Y-%m-%d')}}}",
        r"\newcommand{\breakableurl}[1]{%",
        r"  \begingroup",
        r"    \fontsize{10}{12}\selectfont",
        r"    \RaggedRight",
        r"    \urlstyle{same}",
        r"    \expandafter\url\expandafter{#1}%",
        r"  \endgroup",
        r"}",
        r"\begin{document}",
        r"\fontsize{15}{17}\selectfont",
        r"\maketitle",
        
        # Weather widget
        r"\begin{tikzpicture}[remember picture,overlay]",
        r"\node[anchor=north east,xshift=-1cm,yshift=-1cm] at (current page.north east) {",
        r"\begin{minipage}{5cm}",
        r"\begin{center}",
        r"\textbf{Weather Widget}\\",
        r"Location: Madrid\\"
    ]

    if weather_data:
        latex_content.extend([
            fr"Min/Max Temp: {weather_data['temp_min']}/{weather_data['temp_max']}°C\\",
            fr"Rain Prob: {weather_data['rain_prob']}\%\\",
            fr"Forecast: {weather_data['description']}"
        ])
    else:
        latex_content.append(r"Weather data unavailable")
    
    latex_content.extend([
        r"\end{center}",
        r"\end{minipage}",
        r"};",
        r"\end{tikzpicture}",
        
        r"\tableofcontents",
        r"\newpage"
    ])


    for source, articles in articles_by_source.items():
        latex_content.extend([
            fr"\section{{{escape_latex(source)}}}"
        ])

        for article in articles:
            latex_content.extend([
                fr"\subsection{{{escape_latex(article['title'])}}}",
                fr"\textit{{Published: {escape_latex(article['pubDate'])}}}",
                r"",
                r"\begin{quote}",
                escape_latex(article['summary']),
                r"\end{quote}",
                r"\noindent\href{" + article['link'] + r"}{\breakableurl{" + escape_latex(article['link']) + r"}}",
                r"\vspace{0.5em}",
                r"",
            ])

            for item_type, item in article['full_content']:
                if item_type == 'text':
                    latex_content.append(escape_latex(item))
                    latex_content.append(r"")
                elif item_type == 'image':
                    local_image_path = download_image(item['url'], image_dir)
                    if local_image_path:
                        latex_content.extend([
                            r"\begin{figure}[htbp]",
                            r"\centering",
                            fr"\includegraphics[width=0.8\columnwidth]{{{local_image_path}}}",
                            fr"\caption{{{escape_latex(item.get('caption', '') or item.get('alt', ''))}}}",
                            r"\end{figure}",
                            r""
                        ])

            latex_content.append(r"\newpage")

    latex_content.append(r"\end{document}")

    return '\n'.join(latex_content)

def generate_pdf(articles_by_source, output_filename, weather_data):
    """
    Generate the PDF using LaTeX.
    """
    # Create images directory
    image_dir = "images"
    os.makedirs(image_dir, exist_ok=True)
    
    latex_content = create_latex_document(articles_by_source, image_dir, weather_data)
    
    # Write LaTeX content to a .tex file
    tex_filename = f"{output_filename.replace(' ', '_')}.tex"
    with open(tex_filename, 'w', encoding='utf-8') as tex_file:
        tex_file.write(latex_content)
    
    # Compile LaTeX to PDF
    os.system(f"xelatex -interaction=nonstopmode {tex_filename}")
    
    # Run twice to generate the table of contents
    os.system(f"xelatex -interaction=nonstopmode {tex_filename}")
    
    # Clean up auxiliary files
    for ext in ['.aux', '.log', '.out', '.toc']:
        if os.path.exists(f"{output_filename}{ext}"):
            os.remove(f"{output_filename}{ext}")
    
    # Remove the images directory
    shutil.rmtree(image_dir, ignore_errors=True)

    # Remove the .tex file
    # if os.path.exists(tex_filename):
    #     os.remove(tex_filename)
    
    print(f"PDF created successfully: {output_filename}.pdf")
    print("Temporary files and images have been cleaned up.")

if __name__ == "__main__":
    rss_sources = {
        "La Vanguardia": "https://www.lavanguardia.com/rss/home.xml",
        # Add more sources here
    }
    
    articles_by_source = {}
    for source_name, rss_url in rss_sources.items():
        articles = process_rss_feed(rss_url, hours=24)
        if articles:
            articles_by_source[source_name] = articles
    
    if articles_by_source:
        output_filename = f"daily_news_{datetime.now().strftime('%Y%m%d')}"
        generate_pdf(articles_by_source, output_filename)
    else:
        print("No articles found in the last 24 hours.")
