
import asyncio
from scrapers.blinkit import BlinkitScraper
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestAvailability")

async def main():
    scraper = BlinkitScraper(headless=True)
    try:
        await scraper.start()
        await scraper.set_location("560001")
        
        url = "https://blinkit.com/prn/amul-buffalo-a2-milk/prid/547185"
        logger.info(f"Testing availability for: {url}")
        
        result = await scraper.scrape_availability(url)
        logger.info("Result:")
        for k, v in result.items():
            logger.info(f"{k}: {v}")
            
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await scraper.stop()

if __name__ == "__main__":
    asyncio.run(main())
