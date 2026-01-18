import asyncio
import logging
import random
import os
from datetime import datetime
import pandas as pd
from scrapers.blinkit import BlinkitScraper

# Configuration
INPUT_FILE = "pin_codes_100.xlsx"
OUTPUT_FILE = f"blinkit_availability_parallel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
MAX_WORKERS = 4  # Number of parallel browsers

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Parallel_Runner")

async def worker(name: str, queue: asyncio.Queue, urls: list, results: list):
    """
    Worker pulling pincodes from queue and processing them.
    Each worker gets its own Scraper (Browser) instance.
    """
    logger.info(f"Worker {name} starting...")
    scraper = BlinkitScraper(headless=True) 
    
    try:
        await scraper.start()
        
        while True:
            try:
                pincode = queue.get_nowait()
            except asyncio.QueueEmpty:
                break
            
            logger.info(f"[{name}] Processing Pincode: {pincode}")
            
            try:
                # 1. Set Location
                await scraper.set_location(pincode)
                
                # 2. Scrape Data
                if urls:
                    for url in urls:
                        try:
                            # Random delay between products
                            await asyncio.sleep(random.uniform(1, 3))
                            
                            res = await scraper.scrape_availability(url)
                            res["input_pincode"] = pincode
                            results.append(res)
                            logger.info(f"[{name}] Scraped {url}")
                        except Exception as e:
                            logger.error(f"[{name}] Failed URL {url}: {e}")
                else:
                    # Just logging location success if no URLs
                    results.append({
                        "pincode_input": pincode,
                        "scraped_at": datetime.now().isoformat(),
                        "status": "Location Set Only (No URLs)"
                    })
                
            except Exception as e:
                logger.error(f"[{name}] Failed pincode {pincode}: {e}")
                
            queue.task_done()
            
            # Anti-ban break between tasks for this worker
            delay = random.uniform(5, 12)
            await asyncio.sleep(delay)
            
            # Occasional Long Break (Coffee P break per worker)
            if random.random() < 0.1: # 10% chance
                long_break = random.uniform(30, 60)
                logger.info(f"[{name}] Taking a short rest for {long_break:.0f}s...")
                await asyncio.sleep(long_break)
                
    except Exception as e:
        logger.error(f"[{name}] Crashed: {e}")
    finally:
        await scraper.stop()
        logger.info(f"Worker {name} finished.")

async def main():
    if not os.path.exists(INPUT_FILE):
        logger.error(f"Input file {INPUT_FILE} not found.")
        return

    # 1. Read and Clean Pincodes
    try:
        df = pd.read_excel(INPUT_FILE)
        raw_pincodes = df['Pincode'].dropna().astype(str).tolist()
        pincodes = []
        for p in raw_pincodes:
            clean_p = p.split(',')[0].strip().split('.')[0]
            if clean_p.isdigit() and len(clean_p) == 6:
                pincodes.append(clean_p)
        
        pincodes = sorted(list(set(pincodes)))
        logger.info(f"Loaded {len(pincodes)} unique pincodes to process with {MAX_WORKERS} workers.")
        
        # Extract URLs
        urls_to_check = []
        if 'Product_Url' in df.columns:
            urls_to_check = df['Product_Url'].dropna().unique().tolist()
    except Exception as e:
        logger.error(f"Failed to read input: {e}")
        return

    # 2. Setup Queue
    queue = asyncio.Queue()
    for p in pincodes:
        queue.put_nowait(p)

    # 3. Launch Workers
    results = []
    workers = []
    for i in range(MAX_WORKERS):
        w = asyncio.create_task(worker(f"W-{i+1}", queue, urls_to_check, results))
        workers.append(w)
        # Stagger start times slightly
        await asyncio.sleep(random.uniform(2, 5))

    # Wait for completion
    logger.info("All systems go. Scraping in progress...")
    await asyncio.gather(*workers)
    
    # 4. Save Output (CSV)
    if results:
        pd.DataFrame(results).to_csv(OUTPUT_FILE, index=False)
        logger.info(f"✅ Saved {len(results)} rows to {OUTPUT_FILE}")
    else:
        logger.warning("No results to save.")

if __name__ == "__main__":
    asyncio.run(main())
