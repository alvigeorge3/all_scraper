import asyncio
import logging
import csv
from datetime import datetime
from scrapers.zepto import ZeptoScraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Quick_Test")

async def main():
    scraper = ZeptoScraper(headless=True)
    
    try:
        await scraper.start()
        
        # Set location
        logger.info("Setting location to 560001")
        await scraper.set_location("560001")
        
        # Try a simple category - Fruits & Vegetables which is usually available
        category_url = "https://www.zepto.com/cn/fresh-vegetables"
        logger.info(f"Scraping {category_url}")
        
        products = await scraper.scrape_assortment(category_url, pincode="560001")
        
        logger.info(f"Got {len(products)} products")
        
        if products:
            filename = f"zepto_sample_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=products[0].keys())
                writer.writeheader()
                writer.writerows(products[:10])  # Write first 10 for quick review
            logger.info(f"Saved first 10 products to {filename}")
        else:
            logger.warning("No products scraped")
            
    finally:
        await scraper.stop()

if __name__ == "__main__":
    asyncio.run(main())
