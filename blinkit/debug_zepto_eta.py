
import asyncio
import logging
from scrapers.zepto import ZeptoScraper

logging.basicConfig(level=logging.INFO)

async def test_zepto():
    scraper = ZeptoScraper(headless=True)
    try:
        await scraper.start()
        
        print("Scraper started")
        
        # Test Location Setting
        # Zepto often needs a specific pincode or address search query.
        # 560001 (Bangalore) is usually supported.
        await scraper.set_location("560001")
        print(f"Post-Set-Location ETA: {scraper.delivery_eta}")
        
        # Test Assortment Scraping
        # Using a stable category URL for fruits/vegetables
        url = "https://www.zepto.com/cn/fresh-vegetables/cid/d0758371-2947-4ae3-9df6-9d33fdc814d4" 
        # Note: If this URL is 404, the scraper should handle smart nav or return empty.
        # Let's try to scrape it.
        
        data = await scraper.scrape_assortment(url)
        print(f"Scraped {len(data)} items")
        
        if data:
            print(f"First Item: {data[0]['name']} | Price: {data[0]['price']} | ETA: {data[0]['eta']}")
            
    finally:
        await scraper.stop()

if __name__ == "__main__":
    asyncio.run(test_zepto())
