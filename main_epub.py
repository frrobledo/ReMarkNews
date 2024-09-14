import json
import os
from datetime import datetime
from epub_generator import generate_epub  # Import the new EPUB generator
from parser import process_rss_feed
from upload_remarkable import generate_folder, upload_to_tablet
import requests
import settings
from summarizer import summarize_article, format_summary_epub


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

def main():
    # Create output folder if it doesn't exist
    output_folder = "output"
    os.makedirs(output_folder, exist_ok=True)

    # Read sources from JSON file
    with open('sources.json', 'r') as f:
        sources = json.load(f)

    current_date = datetime.now().strftime('%Y%m%d')
    generated_epubs = []

    # Get weather data
    print('Getting weather data')
    weather_data = get_weather_data()

    # Generate EPUBs for each source
    for source_name, rss_url in sources.items():
        articles = process_rss_feed(rss_url, hours=24)
        print(f'Obtained news from {source_name}')
        if articles:
            if settings.ENABLE_NEWS_SUMMARY:
                for article in articles:
                    print(f'Summarizing article {article['title']}')
                    full_text = ' '.join([item[1] for item in article['full_content'] if item[0] == 'text'])
                    summary = summarize_article(full_text, model=settings.OLLAMA_MODEL)
                    if summary:
                        formatted_summary = format_summary_epub(summary)
                        article['full_content'].insert(0, ('text', formatted_summary))

            output_filename = f"{source_name}-{current_date}"
            output_filename = ensure_correct_text(output_filename)
            output_path = os.path.join(output_folder, output_filename)
            epub_path = generate_epub({source_name: articles}, output_path, weather_data)
            generated_epubs.append(epub_path)
            print(f'Generated EPUB {output_filename}')
            print('-'*10)
        else:
            print(f"No articles found for {source_name} in the last 24 hours.")

    print('All EPUBs generated')
    # Create folder in ReMarkable tablet
    remarkable_folder = f"/news/{current_date}/epub"
    if generate_folder(current_date):
        generate_folder("epub", f"news/{current_date}/")
        # Upload EPUBs to ReMarkable tablet
        for epub in generated_epubs:
            print(f'Uploading {epub}')
            upload_to_tablet(epub, remarkable_folder)
    else:
        print("Failed to create folder in ReMarkable tablet. EPUBs were not uploaded.")





if __name__ == "__main__":
    main()