import asyncio
import logging
from scrapers.zepto import ZeptoScraper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Zepto_URL_Test")

async def test_zepto_url():
    scraper = ZeptoScraper(headless=False)  # visible browser to see what's happening
    try:
        await scraper.start()
        await scraper.set_location("560001")
        
        # The URL provided by user
        url = "https://www.zepto.com/cn/fruits-vegetables/fresh-vegetables/cid/64374cfe-d06f-4a01-898e-c07c46462c36/scid/b4827798-fcb6-4520-ba5b-0f2bd9bd7208"
        
        logger.info(f"Testing URL: {url}")
        logger.info("Navigating and scraping...")
        
        products = await scraper.scrape_assortment(url, pincode="560001")
        
        logger.info(f"\n{'='*70}")
        logger.info(f"Total products scraped: {len(products)}")
        logger.info(f"{'='*70}\n")
        
        if products:
            logger.info("First 10 products:")
            for i, p in enumerate(products[:10], 1):
                logger.info(f"{i}. {p['name']} - {p['category']} - Price: ₹{p['price']}")
            
            # Check if these look like vegetables or detergents
            product_names = [p['name'].lower() for p in products[:10]]
            
            vegetable_keywords = ['potato', 'tomato', 'onion', 'carrot', 'cabbage', 'spinach', 'beans', 'peas', 'broccoli', 'cauliflower', 'capsicum', 'cucumber', 'brinjal', 'lady finger', 'radish']
            detergent_keywords = ['detergent', 'liquid', 'powder', 'cleaner', 'soap', 'wash', 'surf', 'ariel', 'tide']
            
            veg_count = sum(1 for name in product_names if any(kw in name for kw in vegetable_keywords))
            det_count = sum(1 for name in product_names if any(kw in name for kw in detergent_keywords))
            
            logger.info(f"\n{'='*70}")
            logger.info(f"Analysis:")
            logger.info(f"  Vegetable-like products: {veg_count}/10")
            logger.info(f"  Detergent-like products: {det_count}/10")
            
            if veg_count > det_count:
                logger.info(f"✅ LOOKS LIKE VEGETABLES!")
            else:
                logger.info(f"❌ LOOKS LIKE WRONG CATEGORY (detergents/other)")
            logger.info(f"{'='*70}\n")
        
        # Keep browser open to inspect
        logger.info("Keeping browser open for 15 seconds...")
        await scraper.page.wait_for_timeout(15000)
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
    finally:
        await scraper.stop()

if __name__ == "__main__":
    asyncio.run(test_zepto_url())
