# ReMarkNews

ReMarkNews is a Python application that generates daily news digests in PDF or EPUB format, optionally summarizes articles using AI, and sends them to your reMarkable tablet or email.

## Features

- Fetches news articles from RSS feeds
- Generates PDF or EPUB files with article content and images
- Optionally summarizes articles using AI (Ollama)
- Includes weather information
- Sends generated files to reMarkable tablet or email

## Prerequisites

- Python 3.7+
- LaTeX distribution (for PDF generation)
- Ollama (optional, for AI summaries)
- reMarkable tablet (optional)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/frrobledo/ReMarkNews
   cd ReMarkNews
   ```

2. Install required Python packages:
   ```
   pip install -r requirements.txt
   ```

3. This project requires a LaTeX distribution with XeLaTeX for PDF compilation.

4. (Optional) Install [Ollama](https://ollama.com/) if you want to use AI summaries.

## Configuration

### OpenWeather API

1. Sign up for a free account at [OpenWeatherMap](https://openweathermap.org/).
2. Get your API key from the dashboard.
3. Update `settings.py` with your API key and desired location:

   ```python
   OPENWEATHER_API_KEY = "your_api_key_here"
   WEATHER_LAT = 40.4168  # Example: Madrid
   WEATHER_LON = -3.7038  # Example: Madrid
   ```

### News Sources

Edit `sources.json` to add or modify news sources:

```json
{
  "Source Name": "https://example.com/rss-feed-url",
  "Another Source": "https://another-example.com/rss-feed-url"
}
```

### Email Settings (for sending EPUBs via email)

Update `settings.py` with your email credentials:

```python
EMAIL_SENDER = "your_email@gmail.com"
EMAIL_RECEIVER = "recipient@example.com"
EMAIL_PASSWORD = "your_app_password"
```

Note: For Gmail, you'll need to use an App Password instead of your regular password.

### reMarkable Tablet Setup

The old reMarkable transfer API is deprecated due to changes in the cloud API. Now, SSH method is required:

1. Enable SSH on your reMarkable tablet:
   - Go to Settings > Help > Copyrights and licenses > General information > SSH
   - Toggle "Enable SSH" to ON
   - Note down the IP address and password shown

2. Update `settings.py` with your reMarkable tablet's information:

   ```python
   REMARKABLE_SSH_HOST = "192.168.1.xxx"  # Your tablet's IP address
   REMARKABLE_SSH_PASSWORD = "xxxxxxxxxx"  # Your tablet's password
   MOUNT_POINT = "/path/to/mount/point/"  # Where you want to mount the tablet
   ```

3. Ensure you have `sshfs` installed on your system:
   ```
   sudo apt-get install sshfs  # For Ubuntu/Debian
   ```

## Usage

Run the main script with desired options:

```
python main.py -f [pdf|epub] -u [rmapi|pdf2rm|epub2rm|email]
```

- `-f` or `--format`: Choose between `pdf` or `epub` (default: pdf)
- `-u` or `--upload`: Choose the upload method (default: stores them locally)
  - `rmapi`: Use rmapi (deprecated)
  - `pdf2rm`: Use pdf2rm script for PDFs
  - `epub2rm`: Use epub2rm script for EPUBs
  - `email`: Send via email

Example:
```
python main.py -f epub -u email
```

This will generate EPUB files and send them via email.

## Additional Settings

You can modify other settings in `settings.py`:

- `ENABLE_NEWS_SUMMARY`: Set to `True` to enable AI summaries
- `OLLAMA_MODEL`: Specify the Ollama model for summaries
- `font`: Choose a font for PDF generation

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
