
import asyncio
import logging
import json
from scrapers.zepto import ZeptoScraper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Debug_API")

async def main():
    scraper = ZeptoScraper(headless=True)
    await scraper.start()
    
    try:
        await scraper.set_location("560001")
        cats = await scraper.get_all_categories()
        if not cats: return

        target_cat = cats[0]
        print(f"Scraping category: {target_cat}")
        
        async def api_debug(response):
            if "json" in response.headers.get("content-type", ""):
                try:
                    data = await response.json()
                    
                    # Heuristic: Check for product-like keys
                    is_product_data = False
                    keys = []
                    if isinstance(data, dict):
                        keys = list(data.keys())
                        if "products" in data or "items" in data:
                            is_product_data = True
                        # Deep check
                        str_dump = json.dumps(data)
                        if "availableQuantity" in str_dump:
                             is_product_data = True
                             print(f"!!! FOUND availableQuantity in {response.url} !!!")
                    
                    print(f"Captured JSON: {response.url} | Keys: {keys[:5]}...")
                    
                    if is_product_data:
                         fname = f"api_dump_{len(json.dumps(data))}.json"
                         with open(fname, "w", encoding="utf-8") as f:
                            json.dump(data, f, indent=2)
                         print(f"Saved candidate product data to {fname}")

                except Exception as e:
                    pass

        scraper.page.on("response", api_debug)
        
        # Go to a specific category that definitely has products
        # Using a known URL or the first one found
        print(f"Navigating to: {target_cat}")
        await scraper.page.goto(target_cat)
        await asyncio.sleep(20) # Wait for all loads
        
    finally:
        await scraper.stop()

if __name__ == "__main__":
    asyncio.run(main())
