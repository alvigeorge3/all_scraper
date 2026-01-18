import asyncio
import logging
import random
import os
import csv
from datetime import datetime
from typing import List, Dict
import pandas as pd
from scrapers.zepto import ZeptoScraper

# Configuration
INPUT_FILE = "zepto_assortment_input.xlsx"
OUTPUT_FILE = f"zepto_assortment_parallel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
MAX_WORKERS = 4  # Scale this based on CPU/RAM. Zepto is heavier than Blinkit due to network intercept? Actually maybe lighter on DOM.

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Zepto_Parallel_Runner")

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
            valid_products = [p for p in batch if p.get('name')]
            
            if valid_products:
                mode = 'a' if file_initialized else 'w'
                # Check for file existence to handle restarts/partial writes better if needed, 
                # but 'w' for first batch is standard for new run.
                
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

async def worker(name: str, pin_queue: asyncio.Queue, result_queue: asyncio.Queue, input_data: Dict[str, List[str]]):
    """
    Worker:
    1. Gets Pincode
    2. Scrapes Assigned Categories for that pincode
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
            urls = input_data.get(pincode, [])
            
            if not urls:
                logger.warning(f"[{name}] No URLs for {pincode}, skipping.")
                pin_queue.task_done()
                continue

            try:
                # 1. Set Location
                await scraper.set_location(pincode)
                
                # 2. Iterate URLs for this pincode
                for i, url in enumerate(urls):
                    try:
                        logger.info(f"[{name}] Scraping {url} ({i+1}/{len(urls)})...")
                        products = await scraper.scrape_assortment(url, pincode=pincode)
                        
                        if products:
                            # Push to writer
                            await result_queue.put(products)
                        
                        # Short delay between categories to be human-like
                        await scraper.random_sleep(2, 5)
                        
                    except Exception as e:
                        logger.error(f"[{name}] Failed URL {url}: {e}")
                
            except Exception as e:
                logger.error(f"[{name}] Failed processing {pincode}: {e}")
                
            pin_queue.task_done()
            
            # Anti-ban break between pincodes
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
    from utils.excel_reader import read_input_excel
    data = read_input_excel(INPUT_FILE) # Returns Dict[pincode, List[urls]]
    
    if not data:
        logger.error("No data found in input file.")
        return
        
    pincodes = list(data.keys())
    logger.info(f"Loaded {len(pincodes)} unique pincodes with {sum(len(u) for u in data.values())} URLs.")

    # 2. Setup Queues
    pin_queue = asyncio.Queue()
    result_queue = asyncio.Queue()
    
    for p in pincodes:
        pin_queue.put_nowait(p)

    # 3. Launch Writer
    writer = asyncio.create_task(writer_task(result_queue, OUTPUT_FILE))

    # 4. Launch Workers
    workers = []
    # If list is small, don't spin up too many workers
    actual_workers = min(MAX_WORKERS, len(pincodes))
    
    logger.info(f"Spinning up {actual_workers} workers...")
    for i in range(actual_workers):
        w = asyncio.create_task(worker(f"W-{i+1}", pin_queue, result_queue, data))
        workers.append(w)
        # Stagger starts slightly to avoid hammering CPU/Net on browser launch
        await asyncio.sleep(2) 

    # Wait for workers
    await asyncio.gather(*workers)
    
    # Signal writer to stop
    await result_queue.put(None)
    await writer
    
    logger.info(f"All done! Output saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
