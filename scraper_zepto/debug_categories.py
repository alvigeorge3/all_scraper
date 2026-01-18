import asyncio
import logging
from scrapers.zepto import ZeptoScraper

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    scraper = ZeptoScraper(headless=False)
    await scraper.start()
    try:
        await scraper.set_location("560001")
        
        # Wait for page to reload/update
        await scraper.page.wait_for_timeout(5000)
        
        # Extract all hrefs
        hrefs = await scraper.page.evaluate("""
            () => {
                return Array.from(document.querySelectorAll('a')).map(a => a.href)
            }
        """)
        
        print(f"Found {len(hrefs)} links")
        with open("debug_links.txt", "w", encoding="utf-8") as f:
            for href in hrefs:
                f.write(f"{href}\n")
                
        # Also dump HTML for good measure
        content = await scraper.page.content()
        with open("debug_categories.html", "w", encoding="utf-8") as f:
            f.write(content)

    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await scraper.stop()

if __name__ == "__main__":
    asyncio.run(main())
