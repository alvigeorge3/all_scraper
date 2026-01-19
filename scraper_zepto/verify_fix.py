
import asyncio
import logging
from scrapers.zepto import ZeptoScraper

# Setup logging
logging.basicConfig(level=logging.INFO)

async def main():
    scraper = ZeptoScraper(headless=True)
    await scraper.start()
    
    pincode = "560001"
    await scraper.set_location(pincode)
    
    # Test Category: Munchies (Chips)
    url = "https://www.zepto.com/cn/munchies/chips-crisps/cid/d2c2a144-43cd-43e5-b308-92628fa68596"
    
    print(f"Scraping {url}...")
    products = await scraper.scrape_assortment_fast(url, pincode)
    
    print(f"Found {len(products)} products")
    
    if products:
        print("\n--- Sample Product ---")
        p = products[0]
        for k, v in p.items():
            print(f"{k}: {v}")
            
        # Check for N/A
        na_fields = [k for k, v in p.items() if v == "N/A" or v is None]
        if na_fields:
            print(f"\nWARNING: Fields with N/A: {na_fields}")
        else:
            print("\nSUCCESS: No N/A fields in sample!")
            
        # Check Price specifically
        if p['Price'] == "N/A" or p['Price'] is None:
             print("FAILURE: Price is missing")
        else:
             print(f"Verified Price: {p['Price']}")
             
    await scraper.stop()

if __name__ == "__main__":
    asyncio.run(main())
