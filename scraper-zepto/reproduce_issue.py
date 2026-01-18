
import asyncio
import logging
from scrapers.zepto import ZeptoScraper

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Reproduction")

async def main():
    scraper = ZeptoScraper(headless=True)
    try:
        await scraper.start()
        
        # 1. Set Location
        pincode = "560001"
        logger.info(f"Setting location to {pincode}...")
        await scraper.set_location(pincode)
        
        # 2. Scrape Assortment
        # Use a generic category that should have items
        url = "https://www.zepto.com/cn/fruits-vegetables/cid/0b0c0343-a496-474e-b23d-354719cdb23d" # Adjusted generic URL if needed, but let's try the one from code/logic
        # Actually proper Zepto URL for Fresh Vegetables:
        url = "https://www.zepto.com/cn/fresh-vegetables/cid/354719cd-b23d-4c54-a74e-0b0c0343a496"
        
        logger.info(f"Scraping {url}...")
        items = await scraper.scrape_assortment(url, pincode=pincode)
        
        logger.info(f"Scraped {len(items)} items.")
        if items:
            logger.info(f"First Item: {items[0]}")
            
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await scraper.stop()

if __name__ == "__main__":
    asyncio.run(main())
