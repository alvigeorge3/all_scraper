import asyncio
import logging
from scrapers.instamart import InstamartScraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Test_Instamart")

async def main():
    scraper = InstamartScraper(headless=True)
    try:
        await scraper.start()
        await scraper.set_location("560001")
        
        # Test 1: Category Discovery
        categories = await scraper.get_categories()
        logger.info(f"Discovered {len(categories)} categories")
        if categories:
            logger.info(f"Sample category: {categories[0]}")
            
            # Test 2: Scrape one category
            logger.info("Scraping first category...")
            results = await scraper.scrape_assortment(categories[0], pincode="560001")
            
            if results:
                logger.info(f"Scraped {len(results)} products")
                logger.info(f"Sample Product: {results[0]}")
            else:
                logger.warning("No products scraped from sample category.")
        else:
            logger.error("No categories found! Homepage crawl might be failing.")
            
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
    finally:
        await scraper.stop()

if __name__ == "__main__":
    asyncio.run(main())
