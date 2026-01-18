import asyncio
import logging
from scrapers.instamart import InstamartScraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Instamart_Test")

async def test_instamart():
    scraper = InstamartScraper(headless=True) # Run headless to reproduce
    try:
        await scraper.start()
        await scraper.set_location("560001")
        products = await scraper.scrape_assortment("https://www.swiggy.com/instamart/category-listing?categoryName=Fresh%20Vegetables&custom_back=true&taxonomyType=CategoryListing&taxonomyId=1483")
        logger.info(f"Scraped {len(products)} products.")
    except Exception as e:
        logger.error(f"Test failed: {e}")
    finally:
        await scraper.stop()

if __name__ == "__main__":
    asyncio.run(test_instamart())
