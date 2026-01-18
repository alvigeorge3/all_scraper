import asyncio
import logging
from scrapers.zepto import ZeptoScraper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Zepto_URL_Finder")

async def find_vegetables_url():
    """Navigate organically to vegetables and find the correct URL"""
    scraper = ZeptoScraper(headless=False)  # Visible browser
    try:
        await scraper.start()
        await scraper.set_location("560001")
        
        # Navigate to homepage
        logger.info("Navigating to Zepto homepage...")
        await scraper.page.goto("https://www.zepto.com", wait_until='domcontentloaded')
        await scraper.page.wait_for_timeout(3000)
        
        logger.info("Page loaded. Looking for 'Vegetables' category...")
        
        # Try to find and click vegetables
        vegetables_found = False
        selectors_to_try = [
            "text='Vegetables' >> visible=true",
            "text='Fresh Vegetables' >> visible=true",
            "a:has-text('Vegetables'):visible",
            "[href*='vegetable']:visible",
            "[href*='fresh-vegetable']:visible"
        ]
        
        for selector in selectors_to_try:
            try:
                logger.info(f"Trying selector: {selector}")
                if await scraper.page.is_visible(selector, timeout=2000):
                    logger.info(f"✅ Found vegetables with: {selector}")
                    await scraper.page.click(selector)
                    vegetables_found = True
                    break
            except Exception as e:
                logger.debug(f"Selector {selector} failed: {e}")
                continue
        
        if not vegetables_found:
            logger.warning("Could not find vegetables link automatically. Trying Search...")
            try:
                # Search for "Vegetables"
                search_input = "input[placeholder*='Search']"
                await scraper.page.wait_for_selector(search_input, timeout=5000)
                await scraper.page.fill(search_input, "Vegetables")
                await scraper.page.press(search_input, "Enter")
                await scraper.page.wait_for_timeout(5000)
                
                # Click on a category result if it appears, or just look for URL change
                # Zepto search usually shows products. We want category.
                # Check for "View all" next to relevant category or look at URL
                logger.info("Search performed. Checking URL...")
            except Exception as e:
                logger.warning(f"Search fallback failed: {e}")
                
            logger.info("Waiting 30 seconds for you to MANUALLY navigate to Vegetables if needed...")
            await scraper.page.wait_for_timeout(30000)
        else:
            await scraper.page.wait_for_timeout(5000)
        
        # Get the URL
        current_url = scraper.page.url
        logger.info(f"\n{'='*70}")
        logger.info(f"🎯 CURRENT URL: {current_url}")
        logger.info(f"{'='*70}\n")
        
        # Take a screenshot to verify what we see
        await scraper.page.screenshot(path="zepto_vegetables_page.png")
        
        # Try scraping to see if we get vegetables
        logger.info("Testing if this URL gives vegetables...")
        # Clean the URL to remove tracking params if possible or just use as is
        products = await scraper.scrape_assortment(current_url, pincode="560001")
        
        logger.info(f"\nScraped {len(products)} products")
        if products:
            logger.info("\nFirst 5 products:")
            for i, p in enumerate(products[:5], 1):
                logger.info(f"{i}. {p['name']} - {p['category']}")
        
        # Keep browser open for inspection
        logger.info("\n⏰ Keeping browser open for 20 seconds for inspection...")
        await scraper.page.wait_for_timeout(20000)
        
        return current_url
        
    except Exception as e:
        logger.error(f"Failed: {e}", exc_info=True)
        return None
    finally:
        await scraper.stop()

if __name__ == "__main__":
    url = asyncio.run(find_vegetables_url())
    if url:
        print(f"\n{'='*70}")
        print(f"✅ USE THIS URL IN generate_csvs.py:")
        print(f"{'='*70}")
        print(url)
        print(f"{'='*70}\n")
