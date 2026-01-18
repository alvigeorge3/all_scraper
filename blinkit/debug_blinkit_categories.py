
import asyncio
from scrapers.blinkit import BlinkitScraper
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DebugCategories")

async def main():
    scraper = BlinkitScraper(headless=True)
    try:
        await scraper.start()
        await scraper.set_location("560001") # Categories often depend on location
        
        logger.info("Navigating to homepage...")
        await scraper.page.goto("https://blinkit.com/", wait_until="domcontentloaded")
        await scraper.page.wait_for_timeout(5000)
        
        # Try to find category links
        # Strategy 1: Look for 'pa' links (Category pages usually have /cn/ or /c/ structure, but Blinkit uses /cn/)
        # Actually Blinkit desktop site often lists categories in a sidebar or grid.
        
        logger.info("Extracting links...")
        links = await scraper.page.evaluate('''() => {
            return Array.from(document.querySelectorAll('a')).map(a => a.href)
        }''')
        
        category_links = set()
        for link in links:
            if "/cn/" in link:
                category_links.add(link)
                
        logger.info(f"Found {len(category_links)} potential category links:")
        for l in list(category_links)[:10]:
            logger.info(l)
            
        # Try specific selector for "Shop by category"
        # Usually img alts or text
        
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await scraper.stop()

if __name__ == "__main__":
    asyncio.run(main())
