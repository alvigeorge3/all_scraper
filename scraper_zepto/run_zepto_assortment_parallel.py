
import asyncio
import logging
import random
import os
import csv
from datetime import datetime
import pandas as pd
from scrapers.zepto import ZeptoScraper

# Configuration
INPUT_FILE = "pin_codes.xlsx"
OUTPUT_FILE = f"zepto_assortment_parallel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
MAX_WORKERS = 4 

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Zepto_Assortment_Runner")

async def writer_task(queue: asyncio.Queue, filename: str):
    """Listens for data batches and appends to CSV."""
    file_initialized = False
    
    while True:
        try:
            batch = await queue.get()
            if batch is None: # Poison pill
                queue.task_done()
                break
                
            # Filter valid products
            valid_products = [p for p in batch if isinstance(p, dict) and ('Price' in p or 'Item Name' in p)]
            
            if valid_products:
                mode = 'a' if file_initialized else 'w'
                with open(filename, mode, newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=valid_products[0].keys())
                    if not file_initialized:
                        writer.writeheader()
                        file_initialized = True
                    writer.writerows(valid_products)
                logger.info(f"💾 Saved {len(valid_products)} products to CSV.")
            
            queue.task_done()
        except Exception as e:
            logger.error(f"Writer task error: {e}")

async def worker(name: str, pin_queue: asyncio.Queue, result_queue: asyncio.Queue):
    """
    Worker:
    1. Gets Pincode
    2. Scrapes *All* Categories for that pincode
    3. Pushes data to Result Queue
    """
    logger.info(f"Worker {name} starting...")
    scraper = ZeptoScraper(headless=True)
    
    try:
        await scraper.start()
        
        while True:
            try:
                pincode = pin_queue.get_nowait()
            except asyncio.QueueEmpty:
                break
            
            logger.info(f"[{name}] Starting Pincode: {pincode}")
            
            try:
                # 1. Set Location
                await scraper.set_location(pincode)
                
                # 2. Get Categories
                await asyncio.sleep(2)
                categories = await scraper.get_all_categories()
                logger.info(f"[{name}] Found {len(categories)} categories to scrape for {pincode}")
                
                # Scrape all categories
                for cat_url in categories:
                    try:
                        logger.info(f"[{name}] Scraping {cat_url}...")
                        products = await scraper.scrape_assortment(cat_url, pincode=pincode)
                        
                        if products:
                            # Push to writer
                            await result_queue.put(products)
                        
                        # Short delay between categories
                        await scraper.human_delay(2, 4)
                        
                    except Exception as e:
                        logger.error(f"[{name}] Failed category {cat_url}: {e}")
                
            except Exception as e:
                logger.error(f"[{name}] Failed processing {pincode}: {e}")
                
            pin_queue.task_done()
            
            # Anti-ban break
            delay = random.uniform(5, 10)
            logger.info(f"[{name}] Finished {pincode}. Cooling down for {delay:.0f}s...")
            await asyncio.sleep(delay)
                
    except Exception as e:
        logger.error(f"[{name}] Crashed: {e}")
    finally:
        await scraper.stop()
        logger.info(f"Worker {name} retired.")

async def main():
    if not os.path.exists(INPUT_FILE):
        logger.error(f"Input file {INPUT_FILE} not found.")
        return

    # 1. Read Inputs
    try:
        df = pd.read_excel(INPUT_FILE)
        # Handle 'Pincode' or 'pincode' case insensitive
        col = next((c for c in df.columns if c.lower() == 'pincode'), None)
        if not col:
            logger.error("Input file must have 'Pincode' column")
            return
            
        raw_pincodes = df[col].dropna().astype(str).tolist()
        pincodes = []
        for p in raw_pincodes:
            # Handle multiple pincodes in one cell (comma separated)
            parts = [x.strip() for x in p.split(',')]
            for part in parts:
                clean_p = part.split('.')[0].strip()
                if clean_p.isdigit() and len(clean_p) == 6:
                    pincodes.append(clean_p)
        
        pincodes = sorted(list(set(pincodes)))
        logger.info(f"Loaded {len(pincodes)} unique pincodes.")
    except Exception as e:
        logger.error(f"Failed to read input: {e}")
        return

    # 2. Setup Queues
    pin_queue = asyncio.Queue()
    result_queue = asyncio.Queue()
    
    for p in pincodes:
        pin_queue.put_nowait(p)

    # 3. Launch Writer
    writer = asyncio.create_task(writer_task(result_queue, OUTPUT_FILE))

    # 4. Launch Workers
    workers = []
    actual_workers = min(MAX_WORKERS, len(pincodes))
    
    for i in range(actual_workers):
        w = asyncio.create_task(worker(f"W-{i+1}", pin_queue, result_queue))
        workers.append(w)
        await asyncio.sleep(random.uniform(2, 5))

    # Wait for workers
    await asyncio.gather(*workers)
    
    # Signal writer to stop
    await result_queue.put(None)
    await writer
    
    logger.info(f"All done! Output saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
