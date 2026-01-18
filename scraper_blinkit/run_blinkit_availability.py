import asyncio
from datetime import datetime
import csv
import logging
import os
import random  # Added
import pandas as pd # Explicit import
from utils.excel_reader import read_input_excel
from scrapers.blinkit import BlinkitScraper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Blinkit_Availability_Runner")

# Configuration
INPUT_FILE = "pin_codes_100.xlsx"  # Updated input file
OUTPUT_FILE = f"blinkit_availability_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

async def main():
    logger.info("Starting Blinkit Availability Scraper (Humanized 100-Pin Mode)...")
    
    # 1. Read Input Pincodes
    # Fallback to simple pandas read if excel_reader structure is too rigid
    import pandas as pd
    try:
        df = pd.read_excel(INPUT_FILE)
        if 'Pincode' not in df.columns:
            logger.error("Input file must have 'Pincode' column")
            return
            
        # Clean Pincodes: Handle ints, strings, and comma-separated values
        raw_pincodes = df['Pincode'].dropna().astype(str).tolist()
        pincodes = []
        for p in raw_pincodes:
            # Take first pincode if comma separated (e.g. "560001, 560002")
            clean_p = p.split(',')[0].strip().split('.')[0] # split('.') handles 560001.0
            if clean_p.isdigit() and len(clean_p) == 6:
                pincodes.append(clean_p)
                
        pincodes = sorted(list(set(pincodes))) # Unique & Sorted
        logger.info(f"Loaded {len(pincodes)} unique clean pincodes.")
    except Exception as e:
        logger.error(f"Failed to read input file: {e}")
        return

    # Check for URL column, defaulting to a test set if missing
    urls_to_check = []
    if 'Product_Url' in df.columns:
        urls_to_check = df['Product_Url'].dropna().unique().tolist()
    else:
        logger.warning("No 'Product_Url' column found. Checking Assortment/Category mode is safer for broad checks.")
        # Minimal Fallback: Just set location and check homepage or a dummy category to verify availability
        # For availability mode, we strictly need URLs.
        pass

    # 2. Scrape with Batching
    results = []
    scraper = BlinkitScraper(headless=True) # Recommended False for visual debug, True for bulk
    
    try:
        await scraper.start()
        
        for i, pincode in enumerate(pincodes):
            # Batching / Coffee Break Logic
            if i > 0 and i % 15 == 0:
                rest_time = random.uniform(45, 90)
                logger.info(f"☕ COFFEE BREAK: Pausing for {rest_time:.0f}s to avoid bot detection...")
                await asyncio.sleep(rest_time)

            logger.info(f"[{i+1}/{len(pincodes)}] Processing Pincode: {pincode}")
            
            try:
                await scraper.set_location(pincode)
                
                # If we have specific product URLs to check for *every* pincode:
                if urls_to_check:
                    for url in urls_to_check:
                        res = await scraper.scrape_availability(url)
                        res["input_pincode"] = pincode
                        results.append(res)
                        await scraper.human_delay(1, 3) 
                else: 
                     # If just verifying pincode works/assortment
                     pass
                     
            except Exception as e:
                logger.error(f"Failed to process {pincode}: {e}")
                
            # Random delay between pincodes
            await scraper.human_delay(3, 8)
                    
    except Exception as e:
        logger.error(f"Global scraping error: {e}", exc_info=True)
                    
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
