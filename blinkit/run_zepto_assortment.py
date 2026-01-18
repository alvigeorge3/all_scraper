import asyncio
import logging
import csv
from datetime import datetime
from scrapers.zepto import ZeptoScraper

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Zepto_Assortment_Runner")

# Configuration
PINCODE = "560001"
# Using the corrected URL from previous steps
CATEGORY_URL = "https://www.zepto.com/cn/fruits-vegetables/fresh-vegetables/cid/64374cfe-d06f-4a01-898e-c07c46462c36/scid/b4827798-fcb6-4520-ba5b-0f2bd9bd7208"
OUTPUT_FILE = f"zepto_assortment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

async def main():
    logger.info("Starting Zepto Assortment Scraper...")
    scraper = ZeptoScraper(headless=True)
    
    try:
        await scraper.start()
        await scraper.set_location(PINCODE)
        
        logger.info(f"Scraping URL: {CATEGORY_URL}")
        results = await scraper.scrape_assortment(CATEGORY_URL, pincode=PINCODE)
        
        if results:
            logger.info(f"Successfully scraped {len(results)} items")
            
            # Save to CSV
            fieldnames = results[0].keys()
            with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
            
            logger.info(f"Saved data to {OUTPUT_FILE}")
        else:
            logger.warning("No data scraped.")
            
    except Exception as e:
        logger.error(f"Scraping failed: {e}", exc_info=True)
    finally:
        await scraper.stop()

if __name__ == "__main__":
    asyncio.run(main())
