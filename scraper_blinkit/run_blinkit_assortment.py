import asyncio
import logging
import csv
import argparse
import os
from datetime import datetime
from scrapers.blinkit import BlinkitScraper

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Blinkit_Assortment_Runner")

async def main():
    parser = argparse.ArgumentParser(description="Blinkit Assortment Scraper")
    parser.add_argument("--pincode", type=str, default="560001", help="Pincode to set location")
    parser.add_argument("--url", type=str, default="https://blinkit.com/", help="URL to scrape. If homepage, scrapes all categories.")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode", default=True)
    parser.add_argument("--no-headless", action="store_false", dest="headless", help="Run with browser UI")
    args = parser.parse_args()

    OUTPUT_FILE = f"blinkit_assortment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    logger.info(f"Starting Scraper with Pincode: {args.pincode}, URL: {args.url}")
    
    scraper = BlinkitScraper(headless=args.headless)
    
    try:
        await scraper.start()
        await scraper.set_location(args.pincode)
        
        target_urls = []
        if args.url == "https://blinkit.com/" or args.url.rstrip('/') == "https://blinkit.com":
            logger.info("Homepage URL provided. Initiating full site crawl...")
            target_urls = await scraper.get_all_categories()
        else:
            target_urls = [args.url]
            
        logger.info(f"Targeting {len(target_urls)} category URLs")
        
        # Open CSV immediately to write incrementally
        file_initialized = False
        
        for i, url in enumerate(target_urls):
            logger.info(f"[{i+1}/{len(target_urls)}] Processing: {url}")
            try:
                data = await scraper.scrape_assortment(url, pincode=args.pincode)
                if data:
                    
                    # Incremental Write
                    mode = 'a' if file_initialized else 'w'
                    with open(OUTPUT_FILE, mode, newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=data[0].keys())
                        if not file_initialized:
                            writer.writeheader()
                            file_initialized = True
                        writer.writerows(data)
                    
                    logger.info(f"  -> Extracted {len(data)} items. Saved to {OUTPUT_FILE}")
                else:
                    logger.warning(f"  -> No data from {url}")
            except Exception as e:
                logger.error(f"Failed to scrape {url}: {e}")
                
            # Nice delay strictly applied
            await asyncio.sleep(2)
            
    except Exception as e:
        logger.error(f"Fatal Error: {e}", exc_info=True)
    finally:
        await scraper.stop()
        logger.info("Scraping finished.")

if __name__ == "__main__":
    asyncio.run(main())
