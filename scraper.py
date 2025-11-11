import asyncio
import aiohttp
from bs4 import BeautifulSoup
import json
import csv
import re
from urllib.parse import urljoin, urlparse, parse_qs
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TemirciScraper:
    def __init__(self, base_url='https://www.temirci.az', max_concurrent=10):
        self.base_url = base_url
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.all_listings = []

    async def fetch(self, session, url, retries=3):
        """Fetch a URL with retry logic and rate limiting"""
        async with self.semaphore:
            for attempt in range(retries):
                try:
                    await asyncio.sleep(0.5)  # Rate limiting
                    async with session.get(url, timeout=30) as response:
                        if response.status == 200:
                            return await response.text()
                        else:
                            logger.warning(f"Status {response.status} for {url}")
                except Exception as e:
                    logger.error(f"Attempt {attempt + 1}/{retries} failed for {url}: {e}")
                    if attempt < retries - 1:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        return None
            return None

    def extract_phone_from_whatsapp(self, whatsapp_url):
        """Extract phone number from WhatsApp URL"""
        try:
            # Example: https://api.whatsapp.com/send/?phone=+994707044477&text=...
            match = re.search(r'phone=([+\d]+)', whatsapp_url)
            if match:
                return match.group(1)
        except Exception as e:
            logger.error(f"Error extracting phone: {e}")
        return None

    def extract_phone_from_tel(self, tel_url):
        """Extract phone from tel: link"""
        try:
            # Example: tel:(070) 704-4477
            phone = tel_url.replace('tel:', '').strip()
            return phone
        except Exception as e:
            logger.error(f"Error extracting tel: {e}")
        return None

    async def get_categories(self, session):
        """Extract all service categories from the homepage"""
        logger.info("Fetching categories...")
        html = await self.fetch(session, self.base_url)
        if not html:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        categories = []

        # Find all category links
        category_container = soup.find('div', class_='service_category')
        if category_container:
            category_links = category_container.find_all('a', class_='services')
            for link in category_links:
                category_url = urljoin(self.base_url, link.get('href'))
                category_name = link.text.strip()
                categories.append({
                    'name': category_name,
                    'url': category_url
                })
                logger.info(f"Found category: {category_name}")

        return categories

    async def get_total_pages(self, session, category_url):
        """Determine the total number of pages for a category"""
        html = await self.fetch(session, category_url)
        if not html:
            return 1

        soup = BeautifulSoup(html, 'html.parser')
        pagination = soup.find('ul', class_='pagination')

        if pagination:
            page_links = pagination.find_all('a')
            page_numbers = []
            for link in page_links:
                try:
                    # Extract page number from URL or text
                    text = link.text.strip()
                    if text.isdigit():
                        page_numbers.append(int(text))
                except:
                    continue

            return max(page_numbers) if page_numbers else 1

        return 1

    async def get_listing_urls_from_page(self, session, page_url):
        """Extract all listing URLs from a category page"""
        html = await self.fetch(session, page_url)
        if not html:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        listing_urls = []

        # Find all gallery items (listings)
        galleries = soup.find_all('a', class_='gallery')
        for gallery in galleries:
            listing_url = gallery.get('href')
            if listing_url:
                full_url = urljoin(self.base_url, listing_url)
                listing_urls.append(full_url)

        logger.info(f"Found {len(listing_urls)} listings on {page_url}")
        return listing_urls

    async def scrape_listing_detail(self, session, listing_url, category_name):
        """Scrape detailed information from a single listing page"""
        html = await self.fetch(session, listing_url)
        if not html:
            return None

        soup = BeautifulSoup(html, 'html.parser')

        try:
            # Extract ad ID from URL
            ad_id_match = re.search(r'/ads/(\d+)\.html', listing_url)
            ad_id = ad_id_match.group(1) if ad_id_match else None

            # Extract title from og:title meta tag or h1
            title = None
            og_title = soup.find('meta', property='og:title')
            if og_title:
                title = og_title.get('content')
            if not title:
                h1 = soup.find('h1')
                if h1:
                    title = h1.text.strip()

            # Extract phone number from WhatsApp link
            phone = None
            whatsapp_link = soup.find('a', href=re.compile(r'whatsapp\.com'))
            if whatsapp_link:
                phone = self.extract_phone_from_whatsapp(whatsapp_link.get('href'))

            # If no WhatsApp, try tel: link
            if not phone:
                tel_link = soup.find('a', href=re.compile(r'^tel:'))
                if tel_link:
                    phone = self.extract_phone_from_tel(tel_link.get('href'))

            # Extract city
            city = None
            city_elem = soup.find('div', class_='city')
            if city_elem:
                city_text = city_elem.find('b')
                if city_text:
                    city = city_text.text.strip()

            # Extract description
            description = None
            text_elem = soup.find('div', class_='text')
            if text_elem:
                description = text_elem.get_text(strip=True, separator='\n')

            # Extract price
            price = None
            price_elem = soup.find('div', class_='gallery-price')
            if price_elem:
                price_val = price_elem.find('span', class_='price-val')
                price_cur = price_elem.find('span', class_='price-cur')
                if price_val and price_cur:
                    price = f"{price_val.text.strip()} {price_cur.text.strip()}"

            # Extract views, date, etc. from info section
            views = None
            date_posted = None

            info_section = soup.find('div', class_='info')
            if info_section:
                views_elem = info_section.find('p', class_='views')
                if views_elem:
                    views_b = views_elem.find('b')
                    if views_b:
                        views = views_b.text.strip()

                date_elem = info_section.find('p', class_='date')
                if date_elem:
                    date_b = date_elem.find('b')
                    if date_b:
                        date_posted = date_b.text.strip()

            # Extract image URL
            image_url = None
            og_image = soup.find('meta', property='og:image')
            if og_image:
                image_url = og_image.get('content')

            listing_data = {
                'ad_id': ad_id,
                'category': category_name,
                'title': title,
                'phone': phone,
                'city': city,
                'price': price,
                'description': description,
                'views': views,
                'date_posted': date_posted,
                'image_url': image_url,
                'listing_url': listing_url,
                'scraped_at': datetime.now().isoformat()
            }

            logger.info(f"Scraped listing {ad_id}: {title}")
            return listing_data

        except Exception as e:
            logger.error(f"Error scraping {listing_url}: {e}")
            return None

    async def scrape_category(self, session, category):
        """Scrape all listings from a category"""
        category_name = category['name']
        category_url = category['url']

        logger.info(f"Processing category: {category_name}")

        # Get total pages
        total_pages = await self.get_total_pages(session, category_url)
        logger.info(f"Category '{category_name}' has {total_pages} pages")

        # Generate all page URLs
        base_category_url = category_url.replace('.html', '')
        page_urls = []
        for page_num in range(1, total_pages + 1):
            if page_num == 1:
                page_urls.append(category_url)
            else:
                page_urls.append(f"{base_category_url}/{page_num}.html")

        # Get all listing URLs from all pages
        all_listing_urls = []
        tasks = [self.get_listing_urls_from_page(session, page_url) for page_url in page_urls]
        results = await asyncio.gather(*tasks)

        for listing_urls in results:
            all_listing_urls.extend(listing_urls)

        logger.info(f"Total listings found in '{category_name}': {len(all_listing_urls)}")

        # Scrape each listing
        tasks = [self.scrape_listing_detail(session, url, category_name) for url in all_listing_urls]
        listing_data = await asyncio.gather(*tasks)

        # Filter out None results
        listing_data = [data for data in listing_data if data is not None]

        return listing_data

    async def scrape_all(self):
        """Main scraping function"""
        async with aiohttp.ClientSession() as session:
            # Get all categories
            categories = await self.get_categories(session)
            logger.info(f"Found {len(categories)} categories")

            # Scrape all categories
            for category in categories:
                category_listings = await self.scrape_category(session, category)
                self.all_listings.extend(category_listings)
                logger.info(f"Total listings scraped so far: {len(self.all_listings)}")

        return self.all_listings

    def save_to_json(self, filename='temirci_listings.json'):
        """Save scraped data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.all_listings, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved {len(self.all_listings)} listings to {filename}")

    def save_to_csv(self, filename='temirci_listings.csv'):
        """Save scraped data to CSV file"""
        if not self.all_listings:
            logger.warning("No listings to save")
            return

        keys = self.all_listings[0].keys()
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(self.all_listings)
        logger.info(f"Saved {len(self.all_listings)} listings to {filename}")


async def main():
    scraper = TemirciScraper(max_concurrent=10)

    logger.info("Starting scraper...")
    await scraper.scrape_all()

    logger.info(f"Scraping complete! Total listings: {len(scraper.all_listings)}")

    # Save to both JSON and CSV
    scraper.save_to_json()
    scraper.save_to_csv()

    # Print sample data
    if scraper.all_listings:
        logger.info("\nSample listing:")
        logger.info(json.dumps(scraper.all_listings[0], ensure_ascii=False, indent=2))


if __name__ == '__main__':
    asyncio.run(main())
