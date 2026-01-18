
import asyncio
import logging
from scrapers.instamart import InstamartScraper

logging.basicConfig(level=logging.INFO)

async def test_instamart():
    scraper = InstamartScraper(headless=True)
    try:
        await scraper.start()
        
        # Instamart location setting
        await scraper.set_location("560001")
        print(f"Post-Set-Location ETA: {scraper.delivery_eta}")
        
        # Test Assortment Scraping
        # Category: Fresh Vegetables
        url = "https://www.swiggy.com/instamart/category-listing?categoryName=Fresh%20Vegetables&custom_back=true&taxonomyType=CategoryListing&taxonomyId=1483"
        
        data = await scraper.scrape_assortment(url)
        print(f"Scraped {len(data)} items")
        
        if data:
            print(f"First Item: {data[0]['name']} | Price: {data[0]['price']} | ETA: {data[0]['eta']}")
            
    finally:
        await scraper.stop()

if __name__ == "__main__":
    asyncio.run(test_instamart())
