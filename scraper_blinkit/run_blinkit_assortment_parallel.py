import asyncio
import logging
import random
import os
import csv
from datetime import datetime
import pandas as pd
from scrapers.blinkit import BlinkitScraper

# Configuration
INPUT_FILE = "pin_codes.xlsx"
OUTPUT_FILE = f"blinkit_assortment_parallel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
MAX_WORKERS = 6  # Reduced from 12 to prevent MemoryError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Parallel_Assortment_Runner")

# We will write to one file, so we need a lock if multiple workers write concurrently
# Or better: each worker returns data and main thread writes.
# Given memory constraints for huge datasets, let's have each worker write to its own temp file or use a thread-safe queue.
# Simple approach: Workers put results into a thread-safe Async Queue, separate Writer task saves them.

async def writer_task(queue: asyncio.Queue, filename: str):
    """Listens for data batches and appends to CSV."""
    file_initialized = False
    total_count = 0
    
    while True:
        try:
            batch = await queue.get()
            if batch is None: # Poison pill
                queue.task_done()
                break
                
            # Filter dummy status messages (dictionaries with only status)
            valid_products = [p for p in batch if 'price' in p or 'mrp' in p]
            
            if valid_products:
                mode = 'a' if file_initialized else 'w'
                with open(filename, mode, newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=valid_products[0].keys())
                    if not file_initialized:
                        writer.writeheader()
                        file_initialized = True
                    writer.writerows(valid_products)
                count = len(valid_products)
                total_count += count
                logger.info(f"💾 Saved {count} products. Total: {total_count}")
            
            queue.task_done()
        except Exception as e:
            logger.error(f"Writer task error: {e}")
            
    return total_count

async def worker(name: str, pin_queue: asyncio.Queue, result_queue: asyncio.Queue):
    """
    Worker:
    1. Gets Pincode
    2. Scrapes *All* Categories for that pincode
    3. Pushes data to Result Queue
    """
    logger.info(f"Worker {name} starting...")
    scraper = BlinkitScraper(headless=True)
    
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
                
                # Limit categories for speed if testing (Check if we want ALL or Top 5)
                # User asked for equivalent of 'assortment' functionality which is usually ALL.
                # But for 100 pincodes * 20 categories, that's huge. 
                # We will process them all but with checks.
                
                # 3. Parallel Category Scraping (Multi-Tab)
                logger.info(f"[{name}] Scraping {len(categories)} categories with parallel tabs...")
                
                # We can batch categories if needed, but the method handles semaphore
                # However, for 6 workers * 4 tabs = 24 concurrent tabs total. Safe.
                products = await scraper.scrape_categories_parallel(list(categories), pincode=pincode, concurrency=4)
                
                if products:
                    await result_queue.put(products)
                    logger.info(f"[{name}] Pincode {pincode} complete. Scraped {len(products)} total items.")
                
                # No need for per-category loop delay anymore
                
                
            except Exception as e:
                logger.error(f"[{name}] Failed processing {pincode}: {e}")
                
            pin_queue.task_done()
            
            # Anti-ban break
            delay = random.uniform(10, 20)
            logger.info(f"[{name}] Use finished {pincode}. Cooling down for {delay:.0f}s...")
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

    import time
    start_time = time.time()
    
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
    
    for i in range(actual_workers):
        w = asyncio.create_task(worker(f"W-{i+1}", pin_queue, result_queue))
        workers.append(w)
        await asyncio.sleep(random.uniform(2, 5))

    # Wait for workers
    await asyncio.gather(*workers)
    
    # Signal writer to stop
    await result_queue.put(None)
    total_products = await writer
    
    end_time = time.time()
    duration_seconds = end_time - start_time
    duration_minutes = duration_seconds / 60
    
    logger.info(f"All done! Output saved to: {OUTPUT_FILE}")
    
    # --- Performance Reporting ---
    try:
        metrics = {
            "Metric": [
                "Total Pincodes Processed",
                "Total Products Scraped",
                "Total Time (Seconds)",
                "Total Time (Minutes)",
                "Average Time per Pincode (s)",
                "Scraping Speed (Products/Min)",
                "Output File"
            ],
            "Value": [
                len(pincodes),
                total_products,
                f"{duration_seconds:.2f}",
                f"{duration_minutes:.2f}",
                f"{duration_seconds / len(pincodes) if pincodes else 0:.2f}",
                f"{total_products / duration_minutes if duration_minutes > 0 else 0:.2f}",
                OUTPUT_FILE
            ]
        }
        
        perf_df = pd.DataFrame(metrics)
        perf_file = f"performance_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        perf_df.to_excel(perf_file, index=False)
        logger.info(f"📊 Performance report saved to: {perf_file}")
        
    except Exception as e:
        logger.error(f"Failed to save performance report: {e}")

if __name__ == "__main__":
    asyncio.run(main())
