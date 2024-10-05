import json
import os
from datetime import datetime
from pdf_generator_latex import generate_pdf
from epub_generator import generate_epub  # Import the new EPUB generator
from parser import process_rss_feed
from upload_remarkable import generate_folder, upload_to_tablet, send_epubs_using_epub2rm, send_pdfs_using_pdf2rm, send_epub_email
import requests
import settings
from summarizer import summarize_article, format_summary_epub, format_summary
# from email_sender import send_email_with_attachment
import sys
import argparse
import subprocess

def ensure_correct_text(text):
    return text.replace(' ', '_')

def get_weather_data():
    api_key = settings.OPENWEATHER_API_KEY
    lat = settings.WEATHER_LAT
    lon = settings.WEATHER_LON
    
    if not all([api_key, lat, lon]):
        print("Weather API key or coordinates not set in settings.py.")
        return None

    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            today_data = [item for item in data['list'] if datetime.fromtimestamp(item['dt']).date() == datetime.now().date()]
            
            if today_data:
                temp_min = min(item['main']['temp_min'] for item in today_data)
                temp_max = max(item['main']['temp_max'] for item in today_data)
                rain_prob = max(item.get('pop', 0) for item in today_data)
                description = today_data[0]['weather'][0]['description'].capitalize()
                
                return {
                    'temp_min': round(temp_min),
                    'temp_max': round(temp_max),
                    'rain_prob': round(rain_prob * 100),  # Convert to percentage
                    'description': description
                }
            else:
                print("No forecast data available for today")
        else:
            print(f"Error fetching weather data: HTTP {response.status_code}")
    except requests.RequestException as e:
        print(f"Error fetching weather data: {e}")
    return None

def main(args):
    # Create output folder if it doesn't exist
    output_folder = "output"
    os.makedirs(output_folder, exist_ok=True)

    # Read sources from JSON file
    with open('sources.json', 'r') as f:
        sources = json.load(f)

    current_date = datetime.now().strftime('%Y%m%d')
    generated_files = []

    # Get weather data
    print('Getting weather data')
    weather_data = get_weather_data()

    # Generate files for each source
    for source_name, rss_url in sources.items():
        articles = process_rss_feed(rss_url, hours=24)
        print(f'Obtained news from {source_name}')
        if articles:
            if settings.ENABLE_NEWS_SUMMARY:
                for article in articles:
                    print(f"Summarizing article {article['title']}")
                    full_text = ' '.join([item[1] for item in article['full_content'] if item[0] == 'text'])
                    summary = summarize_article(full_text, model=settings.OLLAMA_MODEL)
                    if summary:
                        if args.format == 'epub':
                            formatted_summary = format_summary_epub(summary)
                        elif args.format == 'pdf':
                            formatted_summary = format_summary(summary)
                        else:
                            formatted_summary = summary
                        article['full_content'].insert(0, ('text', formatted_summary))

            output_filename = f"{source_name}-{current_date}"
            output_filename = ensure_correct_text(output_filename)
            output_path = os.path.join(output_folder, output_filename)
            
            if args.format == 'pdf':
                generate_pdf({source_name: articles}, output_path, weather_data, settings.font)
                generated_files.append(f"{output_path}.pdf")
            elif args.format == 'epub':
                generate_epub({source_name: articles}, output_path, weather_data, use_images=False)  # Some documents were too large, use_images=False always
                # generate_epub({source_name: articles}, output_path, weather_data, use_images=False if args.upload == 'email' else True)
                generated_files.append(f"{output_path}.epub")
            
            print(f'Generated {args.format.upper()} {output_filename}')
            print('-'*10)
        else:
            print(f"No articles found for {source_name} in the last 24 hours.")

    print(f'All {args.format.upper()}s generated')

    ### Upload files to ReMarkable tablet or send via email
    if args.upload == 'rmapi':  # deprecated
        # Create folder in ReMarkable tablet using rmapi
        remarkable_folder = f"/News/{current_date}"
        if generate_folder(current_date):
            # Upload files to ReMarkable tablet using rmapi
            for file in generated_files:
                print(f'Uploading {file}')
                upload_to_tablet(file, remarkable_folder)
        else:
            print(f"Failed to create folder in ReMarkable tablet. {args.format.upper()}s were not uploaded.")
    elif args.upload == 'pdf2rm' and args.format == 'pdf':
        # Define SSH mount command
        mount_command = f'echo "{settings.REMARKABLE_SSH_PASSWORD}" | sshfs root@{settings.REMARKABLE_SSH_HOST}:/ {settings.MOUNT_POINT} -o password_stdin'
        # Run SSH mount command
        subprocess.run(mount_command, shell=True, check=True)
        # Upload PDFs using pdf2rm script
        if send_pdfs_using_pdf2rm(generated_files):
            print("All PDFs processed and sent to ReMarkable tablet successfully")
        else:
            print("Failed to process and send PDFs using pdf2rm script")
        # Unmount ReMarkable tablet
        unmount_command = f'fusermount -u {settings.MOUNT_POINT}'
        subprocess.run(unmount_command, shell=True, check=True)
    elif args.upload == 'epub2rm' and args.format == 'epub':
        # Defbe SSH mount command
        mount_command = f'echo "{settings.REMARKABLE_SSH_PASSWORD}" | sshfs root@{settings.REMARKABLE_SSH_HOST}:/ {settings.MOUNT_POINT} -o password_stdin'
        # Run SSH mount command
        subprocess.run(mount_command, shell=True, check=True)
        # Upload EPUBs using epub2rm script
        if send_epubs_using_epub2rm(generated_files):
            print("All EPUBs processed and sent to ReMarkable tablet successfully")
        else:
            print("Failed to process and send EPUBs using epub2rm script")
        # Unmount ReMarkable tablet
        unmount_command = f'fusermount -u {settings.MOUNT_POINT}'
        subprocess.run(unmount_command, shell=True, check=True)
    elif args.upload == 'email':
        # Send files via email
        for file in generated_files:
            if send_epub_email(sender_email=settings.EMAIL_SENDER, sender_password=settings.EMAIL_PASSWORD, recipient_email=settings.EMAIL_RECEIVER, subject=f"News {current_date}", body="Here is the news you requested.", epub_path=file):
                print(f"Successfully sent {file} via email")
            else:
                print(f"Failed to send {file} via email")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate and upload news files to ReMarkable tablet or send via email")
    parser.add_argument("-f", "--format", choices=['pdf', 'epub'], default='pdf', help="File format to generate (pdf or epub)")
    parser.add_argument("-u", "--upload", choices=['rmapi', 'pdf2rm', 'epub2rm', 'email'], help="Upload method or email")
    args = parser.parse_args()

    if args.upload == 'pdf2rm' and args.format != 'pdf':
        print("Overwriting format to pdf to use pdf2rm upload method")
        args.format = 'pdf'
    elif args.upload == 'epub2rm' and args.format != 'epub':
        print("Overwriting format to epub to use epub2rm upload method")
        args.format = 'epub'
    elif args.upload == 'email' and args.format != 'epub':
        print("Overwriting format to epub to use email upload method")
        args.format = 'epub'

    print(f'Generating {args.format.upper()}s')
    if args.upload:
        if args.upload == 'email':
            print('Files will be sent via email')
        else:
            print(f'Upload method: {args.upload}')
    else:
        print('Files will be stored locally only')
    
    main(args)
