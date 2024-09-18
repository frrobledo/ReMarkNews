# ReMarkNews

This project generates a daily news summary PDF from various RSS feeds and uploads it to a ReMarkable tablet. It includes weather information for a specified location.

## Disclaimer
Due to changes in the Remarkable Cloud API, direct upload to the Remarkable tablet is not possible. By default, this feature has been disabled. To enable it, use flag `--upload`
```
python main.py --upload
python main_epub.py --upload
```

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/frrobledo/ReMarkNews.git
   cd ReMarkNews
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Install LaTeX and XeLaTeX:
   - This project requires a LaTeX distribution with XeLaTeX for PDF compilation.
   - For Ubuntu/Debian:
     ```
     sudo apt-get install texlive-xetex
     ```
   - For macOS (using Homebrew):
     ```
     brew install --cask mactex
     ```
   - For Windows, install MiKTeX or TeX Live, which include XeLaTeX.

5. Set up OpenWeatherMap API:
   - Sign up for a free account at [OpenWeatherMap](https://openweathermap.org/)
   - Get your API key from the dashboard
   - Copy `settings.py.example` to `settings.py`
   - Update `settings.py` with your API key and desired coordinates:
     ```python
     OPENWEATHER_API_KEY = "your_api_key_here"
     WEATHER_LAT = 40.4168  # Example: Madrid
     WEATHER_LON = -3.7038  # Example: Madrid
     ```

6. Install and set up rmapi:
   - Follow the installation instructions at [rmapi GitHub repository](https://github.com/juruen/rmapi)
   - Run `rmapi` and follow the prompts to connect to your ReMarkable tablet

## Project Structure

- `main.py`: Main script to run the news summary generation and upload process. Generates PDF files
- `main_epub.py`: Main script to run the news summary generation and upload process. Generates epub files
- `parser.py`: Contains functions to fetch and parse RSS feeds
- `scrapper.py`: Extracts full article content and images from web pages
- `pdf_generator_latex.py`: Generates PDF using LaTeX (XeLaTeX)
- `upload_remarkable.py`: Handles uploading files to ReMarkable tablet
- `sources.json`: Contains RSS feed URLs for different news sources
- `settings.py`: Configuration file for OpenWeatherMap API

## Usage

1. Update `sources.json` with your desired RSS feeds.

2. Run the main script:
   ```
   python main.py
   ```

   This will:
   - Fetch articles from the specified RSS feeds
   - Generate a PDF with the news summary and weather information using XeLaTeX
   - Upload the PDF to your ReMarkable tablet

## Customization

- Modify `sources.json` to add or remove news sources
- Adjust the time range for fetched articles in `main.py` (default is 24 hours)
- Customize the PDF layout and styling in `pdf_generator_latex.py`

## Dependencies

Main dependencies include:
- `requests`: For making HTTP requests
- `beautifulsoup4`: For parsing HTML content
- `Pillow`: For image processing
- XeLaTeX: For PDF compilation

For a complete list of Python dependencies, see `requirements.txt`.

## Notes

- This project uses XeLaTeX for PDF generation. Ensure you have a LaTeX distribution with XeLaTeX installed on your system.
- The project uses `rmapi` for uploading to ReMarkable. Make sure it's properly set up and authenticated.
- In the future, both `main.py` and `main_epub.py` files will be merged and desired output will be selected with a flag (default will be epub).

## Troubleshooting

- If you encounter issues with PDF generation:
  - Check that XeLaTeX is installed and accessible from the command line
  - Run `xelatex --version` to verify the installation
  - If using Windows, ensure the LaTeX installation directory is in your system's PATH
- For upload problems, ensure `rmapi` is correctly installed and authenticated with your ReMarkable account

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
