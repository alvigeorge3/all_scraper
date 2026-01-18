import asyncio
import logging
from scrapers.blinkit import BlinkitScraper
from scrapers.zepto import ZeptoScraper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ETA_Test")

async def test_blinkit_eta():
    logger.info("=" * 50)
    logger.info("Testing Blinkit ETA Extraction")
    logger.info("=" * 50)
    scraper = BlinkitScraper(headless=True)
    try:
        await scraper.start()
        logger.info(f"Initial ETA: {scraper.delivery_eta}")
        await scraper.set_location("560001")
        logger.info(f"Final ETA after set_location: {scraper.delivery_eta}")
    except Exception as e:
        logger.error(f"Blinkit test failed: {e}")
    finally:
        await scraper.stop()
    return scraper.delivery_eta

async def test_zepto_eta():
    logger.info("=" * 50)
    logger.info("Testing Zepto ETA Extraction")
    logger.info("=" * 50)
    scraper = ZeptoScraper(headless=True)
    try:
        await scraper.start()
        logger.info(f"Initial ETA: {scraper.delivery_eta}")
        await scraper.set_location("560001")
        logger.info(f"Final ETA after set_location: {scraper.delivery_eta}")
    except Exception as e:
        logger.error(f"Zepto test failed: {e}")
    finally:
        await scraper.stop()
    return scraper.delivery_eta

async def main():
    blinkit_eta = await test_blinkit_eta()
    zepto_eta = await test_zepto_eta()
    
    print("\n" + "=" * 50)
    print("RESULTS:")
    print("=" * 50)
    print(f"Blinkit ETA: {blinkit_eta}")
    print(f"Zepto ETA: {zepto_eta}")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
