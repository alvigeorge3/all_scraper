
import asyncio
import logging
import json
from scrapers.zepto import ZeptoScraper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Debug_HTML")

async def main():
    scraper = ZeptoScraper(headless=True)
    await scraper.start()
    
    try:
        await scraper.set_location("560001")
        cats = await scraper.get_all_categories()
        if not cats: return
        target_cat = cats[0]
        print(f"Navigating to: {target_cat}")
        
        await scraper.page.goto(target_cat)
        await asyncio.sleep(10)
        
        # 1. Capture Full HTML
        content = await scraper.page.content()
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Saved page_source.html ({len(content)} chars)")
        
        # 2. Extract __NEXT_DATA__
        try:
             data = await scraper.page.evaluate('''() => {
                const el = document.getElementById("__NEXT_DATA__");
                return el ? el.innerText : null;
             }''')
             if data:
                 with open("next_data.json", "w", encoding="utf-8") as f:
                     f.write(data)
                 print(f"Saved next_data.json ({len(data)} chars)")
             else:
                 print("No __NEXT_DATA__ found")
        except Exception as e:
            print(f"Error extracting NEXT_DATA: {e}")

    finally:
        await scraper.stop()

if __name__ == "__main__":
    asyncio.run(main())
