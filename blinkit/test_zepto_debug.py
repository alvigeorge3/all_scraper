import asyncio
import logging
from scrapers.zepto import ZeptoScraper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Zepto_Debug")

async def test_zepto_scraping():
    scraper = ZeptoScraper(headless=False)  # Run with visible browser to see what's happening
    try:
        await scraper.start()
        await scraper.set_location("560001")
        
        # Try the URL from generate_csvs.py (updated)
        url = "https://www.zepto.com/cn/fresh-vegetables/fresh-vegetables/cid/64374cfe-d06f-4a01-898e-c07c46462c36/scid/b4827798-fcb6-4520-ba5b-0f2bd9bd7208"
        logger.info(f"Navigating to: {url}")
        
        products = await scraper.scrape_assortment(url)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Total products scraped: {len(products)}")
        logger.info(f"{'='*60}")
        
        if products:
            logger.info("\nFirst 5 products:")
            for i, p in enumerate(products[:5], 1):
                logger.info(f"\n{i}. {p['name']}")
                logger.info(f"   Brand: {p['brand']}")
                logger.info(f"   Price: {p['price']}, MRP: {p['mrp']}")
                logger.info(f"   Weight: {p['weight']}")
                logger.info(f"   ETA: {p['eta']}")
                logger.info(f"   Image: {p['image_url'][:80] if p['image_url'] != 'N/A' else 'N/A'}")
        
        # Wait so we can see the page
        await scraper.page.wait_for_timeout(5000)
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
    finally:
        await scraper.stop()

if __name__ == "__main__":
    asyncio.run(test_zepto_scraping())
