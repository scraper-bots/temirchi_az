# Temirci.az Web Scraper

An asynchronous web scraper for temirci.az that extracts service listings with contact information.

## Features

- **Asynchronous scraping** using `asyncio` and `aiohttp` for fast performance
- **Automatic category detection** - discovers all service categories from the homepage
- **Pagination handling** - automatically scrapes all pages for each category
- **Phone number extraction** - extracts contact numbers from WhatsApp and tel: links
- **Comprehensive data extraction**:
  - Ad ID
  - Category
  - Title
  - Phone number
  - City
  - Price
  - Description
  - Views
  - Date posted
  - Image URL
  - Listing URL
- **Export formats**: JSON and CSV
- **Error handling** with retry logic and exponential backoff
- **Rate limiting** to avoid overwhelming the server
- **Logging** for monitoring progress

## Installation

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the scraper:

```bash
python scraper.py
```

The scraper will:
1. Fetch all service categories from the homepage
2. For each category, determine the number of pages
3. Extract all listing URLs from each page
4. Scrape detailed information from each listing
5. Save results to `temirci_listings.json` and `temirci_listings.csv`

## Output

The scraper generates two files:

### `temirci_listings.json`
JSON file containing all scraped listings with full details.

### `temirci_listings.csv`
CSV file with the same data, suitable for Excel or data analysis tools.

## Sample Output

```json
{
  "ad_id": "5765",
  "category": "Təmir və Tikinti",
  "title": "Elektrik xidməti",
  "phone": "+994707044477",
  "city": "Bakı",
  "price": "20 AZN",
  "description": "Farid Elektrik sizə hər növ elektrik montaj...",
  "views": "695",
  "date_posted": "2021-03-04 12:55",
  "image_url": "https://www.temirci.az/image/elan/...",
  "listing_url": "https://www.temirci.az/ads/5765.html",
  "scraped_at": "2025-11-11T10:30:45.123456"
}
```

## Configuration

You can customize the scraper by modifying parameters in `scraper.py`:

```python
scraper = TemirciScraper(
    base_url='https://www.temirci.az',
    max_concurrent=10  # Maximum concurrent requests
)
```

### Parameters:
- `base_url`: The base URL of the website
- `max_concurrent`: Maximum number of concurrent requests (default: 10)

## Rate Limiting

The scraper includes built-in rate limiting:
- 0.5 second delay between requests
- Semaphore limiting concurrent connections
- Exponential backoff on failures

## Error Handling

- Automatic retry on failed requests (up to 3 attempts)
- Graceful handling of missing data
- Comprehensive logging of errors and progress

## Categories Scraped

The scraper automatically detects and scrapes all categories including:
- IT-Kompyuter
- Təmir və Tikinti
- Məişət Avadanlıqları və Elektrotexnika
- Ticarət Avadanlıqlarının
- Avtomobil təmiri
- Nəqliyyat və Texnika
- Mebel və İnteryer
- Reklam və Dizayn
- Təmizlik
- Gözəllik və Sağlamlıq
- Tekstil və Geyim
- Digər

## Requirements

- Python 3.7+
- aiohttp
- beautifulsoup4
- lxml

## Notes

- The scraper respects rate limits to avoid overwhelming the server
- Scraping may take some time depending on the number of listings
- Ensure you have permission to scrape the website
- Check the website's robots.txt and terms of service before use

## License

This project is for educational purposes only.
