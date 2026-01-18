import asyncio
import logging
from scrapers.zepto import ZeptoScraper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Verifier")

async def test_human_movement():
    scraper = ZeptoScraper(headless=False) # Headless=False to see it if possible, or just to test logic
    try:
        await scraper.start()
        await scraper.page.goto("https://example.com")
        
        # Test human click on a simple element
        # example.com has a link "More information..."
        logger.info("Testing human_click on 'More information...' link")
        await scraper.human_click("text=More information")
        
        logger.info("Click successful. Waiting a bit.")
        await asyncio.sleep(2)
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
    finally:
        await scraper.stop()
        logger.info("Test finished.")

if __name__ == "__main__":
    asyncio.run(test_human_movement())
