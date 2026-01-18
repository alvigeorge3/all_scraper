import asyncio
import logging
from scrapers.zepto import ZeptoScraper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Zepto_Navigate")

async def navigate_to_vegetables():
    """Navigate to vegetables category organically instead of using deep link"""
    scraper = ZeptoScraper(headless=False)
    try:
        await scraper.start()
        await scraper.set_location("560001")
        
        # Navigate to homepage
        logger.info("Navigating to Zepto homepage...")
        await scraper.page.goto("https://www.zepto.com", wait_until='domcontentloaded')
        await scraper.page.wait_for_timeout(3000)
        
        # Look for vegetables category link
        logger.info("Looking for vegetables category...")
        
        # Try clicking on a vegetables link/button
        selectors_to_try = [
            "text='Vegetables'",
            "text='Fresh Vegetables'",
            "a:has-text('Vegetables')",
            "[href*='vegetables']",
            "[href*='fresh-vegetables']"
        ]
        
        for selector in selectors_to_try:
            try:
                if await scraper.page.is_visible(selector, timeout=2000):
                    logger.info(f"Found vegetables link with selector: {selector}")
                    await scraper.page.click(selector)
                    await scraper.page.wait_for_timeout(3000)
                    break
            except:
                continue
        
        # Get current URL
        current_url = scraper.page.url
        logger.info(f"\n{'='*60}")
        logger.info(f"Current URL after navigation: {current_url}")
        logger.info(f"{'='*60}\n")
        
        # Try scraping
        products = await scraper.scrape_assortment(current_url)
        
        logger.info(f"Total products: {len(products)}")
        if products:
            logger.info("\nFirst 3 products:")
            for i, p in enumerate(products[:3], 1):
                logger.info(f"{i}. {p['name']} - Price: {p['price']}, Weight: {p['weight']}")
        
        # Keep browser open
        logger.info("\nBrowser will stay open for 10 seconds so you can see the page...")
        await scraper.page.wait_for_timeout(10000)
        
    except Exception as e:
        logger.error(f"Failed: {e}", exc_info=True)
    finally:
        await scraper.stop()

if __name__ == "__main__":
    asyncio.run(navigate_to_vegetables())
