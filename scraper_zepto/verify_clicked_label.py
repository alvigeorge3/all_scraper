import asyncio
import logging
from scrapers.zepto import ZeptoScraper

logging.basicConfig(level=logging.INFO)

async def main():
    scraper = ZeptoScraper(headless=True) # Headless=True for speed, change if debugging UI
    try:
        await scraper.start()
        # Set location to a known pincode
        pincode = "560001"
        await scraper.set_location(pincode)
        
        # Verify clicked_location_label
        print(f"Captured Clicked Label: '{scraper.clicked_location_label}'")
        
        if scraper.clicked_location_label and scraper.clicked_location_label != "N/A":
            print("[SUCCESS] Clicked label was captured.")
        else:
            print("[FAILURE] Clicked label is N/A or empty.")
            
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        await scraper.stop()

if __name__ == "__main__":
    asyncio.run(main())
