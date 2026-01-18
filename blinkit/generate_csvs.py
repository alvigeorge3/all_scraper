
import asyncio
import csv
import logging
import os
from typing import List, Dict

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("CSV_Generator")

from scrapers.blinkit import BlinkitScraper
from scrapers.zepto import ZeptoScraper
from scrapers.instamart import InstamartScraper
from scrapers.models import ProductItem

# Configuration
PINCODE = "560001"
# Category URLs (using "Vegetables" or similar for consistency)
URLS = {
    "blinkit": "https://blinkit.com/cn/vegetables-fruits/vegetables/cid/1487/1489",
    "zepto": "https://www.zepto.com/cn/fruits-vegetables/fresh-vegetables/cid/64374cfe-d06f-4a01-898e-c07c46462c36/scid/b4827798-fcb6-4520-ba5b-0f2bd9bd7208",
    "instamart": "https://www.swiggy.com/instamart/category-listing?categoryName=Fresh%20Vegetables&custom_back=true&taxonomyType=CategoryListing&taxonomyId=1483"
}

def save_to_csv(filename: str, data: List[ProductItem]):
    if not data:
        logger.warning(f"No data to save for {filename}")
        return

    keys = data[0].keys()
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
        logger.info(f"Successfully saved {len(data)} items to {filename}")
    except Exception as e:
        logger.error(f"Failed to save {filename}: {e}")

async def run_scraper(name: str, scraper_cls, url: str):
    logger.info(f"Starting {name} scraper...")
    scraper = scraper_cls(headless=True)
    results = []
    try:
        await scraper.start()
        await scraper.set_location(PINCODE)
        results = await scraper.scrape_assortment(url, pincode=PINCODE)
    except Exception as e:
        logger.error(f"Error running {name} scraper: {e}")
    finally:
        await scraper.stop()
    
    return results

async def main():
    # Run sequentially to avoid resource issues
    
    # 1. Blinkit
    blinkit_data = await run_scraper("Blinkit", BlinkitScraper, URLS["blinkit"])
    save_to_csv("blinkit_data.csv", blinkit_data)

    # 2. Zepto
    zepto_data = await run_scraper("Zepto", ZeptoScraper, URLS["zepto"])
    save_to_csv("zepto_data.csv", zepto_data)

    # 3. Instamart
    instamart_data = await run_scraper("Instamart", InstamartScraper, URLS["instamart"])
    save_to_csv("instamart_data.csv", instamart_data)

if __name__ == "__main__":
    asyncio.run(main())
