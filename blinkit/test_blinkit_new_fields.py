import asyncio
import logging
from scrapers.blinkit import BlinkitScraper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Blinkit_New_Fields_Test")

async def test_blinkit_new_fields():
    scraper = BlinkitScraper(headless=True)
    try:
        await scraper.start()
        await scraper.set_location("560001")
        
        url = "https://blinkit.com/cn/vegetables-fruits/vegetables/cid/1487/1489"
        products = await scraper.scrape_assortment(url, pincode="560001")
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Total products scraped: {len(products)}")
        logger.info(f"{'='*60}")
        
        if products:
            logger.info("\nFirst product with NEW FIELDS:")
            p = products[0]
            logger.info(f"Name: {p['name']}")
            logger.info(f"Base Product ID: {p.get('base_product_id', 'N/A')}")
            logger.info(f"🆕 Group ID: {p.get('group_id', 'N/A')}")
            logger.info(f"🆕 Merchant Type: {p.get('merchant_type', 'N/A')}")
            logger.info(f"Store ID: {p.get('store_id', 'N/A')}")
            logger.info(f"Inventory: {p.get('inventory', 'N/A')}")
            logger.info(f"Shelf Life (hours): {p.get('shelf_life_in_hours', 'N/A')}")
            
            # Check how many products have the new fields populated
            with_group_id = sum(1 for p in products if p.get('group_id'))
            with_merchant_type = sum(1 for p in products if p.get('merchant_type'))
            
            logger.info(f"\n{'='*60}")
            logger.info(f"Field Population Stats:")
            logger.info(f"{'='*60}")
            logger.info(f"Products with group_id: {with_group_id}/{len(products)}")
            logger.info(f"Products with merchant_type: {with_merchant_type}/{len(products)}")
            
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
    finally:
        await scraper.stop()

if __name__ == "__main__":
    asyncio.run(test_blinkit_new_fields())
