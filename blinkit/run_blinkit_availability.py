import asyncio
from datetime import datetime
import csv
import logging
import os
from utils.excel_reader import read_input_excel
from scrapers.blinkit import BlinkitScraper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Blinkit_Availability_Runner")

# Configuration
INPUT_FILE = "blinkit_input.xlsx"
OUTPUT_FILE = f"blinkit_availability_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

async def main():
    logger.info("Starting Blinkit Availability Scraper...")
    
    if not os.path.exists(INPUT_FILE):
        logger.error(f"Input file {INPUT_FILE} not found! Please create it with columns 'Pincode' and 'Product_Url'.")
        return

    # 1. Read Input
    data = read_input_excel(INPUT_FILE)
    if not data:
        logger.warning("No data found in input file.")
        return
        
    logger.info(f"Loaded {sum(len(u) for u in data.values())} URLs across {len(data)} pincodes.")
    
    # 2. Scrape
    results = []
    scraper = BlinkitScraper(headless=True)
    
    try:
        await scraper.start()
        
        for pincode, urls in data.items():
            logger.info(f"Processing Pincode: {pincode} ({len(urls)} URLs)")
            
            # Set location once per pincode
            try:
                await scraper.set_location(pincode)
            except Exception as e:
                logger.error(f"Failed to set location {pincode}: {e}")
                continue # Skip this pincode if location fails
            
            for url in urls:
                try:
                    res = await scraper.scrape_availability(url)
                    res["input_pincode"] = pincode
                    results.append(res)
                except Exception as e:
                    logger.error(f"Failed URL {url}: {e}")
                    
    except Exception as e:
        logger.error(f"Global scraping error: {e}", exc_info=True)
    finally:
        await scraper.stop()
        
    # 3. Save Output
    if results:
        fieldnames = results[0].keys()
        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        logger.info(f"✅ Saved {len(results)} rows to {OUTPUT_FILE}")
    else:
        logger.warning("No results to save.")

if __name__ == "__main__":
    asyncio.run(main())
