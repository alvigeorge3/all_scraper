import asyncio
import logging
import random
import os
import csv
from datetime import datetime
import pandas as pd
from scrapers.blinkit import BlinkitScraper
import time

# Configuration
OUTPUT_FILE = f"blinkit_perf_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
MAX_WORKERS = 2 # 1 worker per pincode for this test

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Perf_Tester")

# Hardcoded test pincodes
TEST_PINCODES = ["560001", "110001"] 

async def writer_task(queue: asyncio.Queue, filename: str):
    file_initialized = False
    total_count = 0
    
    while True:
        products = await queue.get()
        if products is None:
            queue.task_done()
            break
            
        valid_products = [p for p in products if isinstance(p, dict)]
        
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
    return total_count

async def worker(name: str, pin_queue: asyncio.Queue, result_queue: asyncio.Queue):
    logger.info(f"Worker {name} starting...")
    scraper = BlinkitScraper(headless=True) # Headless for speed
    
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
                categories = await scraper.get_all_categories()
                logger.info(f"[{name}] Found {len(categories)} categories")
                
                # 3. Parallel Category Scraping (Multi-Tab)
                # Using the optimized method
                products = await scraper.scrape_categories_parallel(list(categories), pincode=pincode, concurrency=5)
                
                if products:
                    await result_queue.put(products)
                
            except Exception as e:
                logger.error(f"[{name}] Failed processing {pincode}: {e}")
                
            pin_queue.task_done()
                
    except Exception as e:
        logger.error(f"[{name}] Crashed: {e}")
    finally:
        await scraper.stop()
        logger.info(f"Worker {name} retired.")

async def main():
    start_time = time.time()
    
    # Setup Queues
    pin_queue = asyncio.Queue()
    result_queue = asyncio.Queue()
    
    for p in TEST_PINCODES:
        pin_queue.put_nowait(p)

    # Launch Writer
    writer = asyncio.create_task(writer_task(result_queue, OUTPUT_FILE))

    # Launch Workers
    workers = []
    for i in range(MAX_WORKERS):
        w = asyncio.create_task(worker(f"W-{i+1}", pin_queue, result_queue))
        workers.append(w)

    # Wait for workers
    await asyncio.gather(*workers)
    
    # Signal writer
    await result_queue.put(None)
    total_products = await writer
    
    end_time = time.time()
    duration = end_time - start_time
    minutes = duration / 60
    
    logger.info(f"🏁 Test Complete in {duration:.2f}s ({minutes:.2f}m)")
    logger.info(f"📦 Total Products: {total_products}")
    logger.info(f"⚡ Speed: {total_products / minutes if minutes > 0 else 0:.2f} products/min")

    # Save Metrics
    metrics = {
        "Metric": [
            "Total Pincodes", "Total Products", "Total Time (Seconds)",
            "Total Time (Minutes)", "Avg Time per Pincode (s)", "Speed (Products/Min)", 
            "Architecture"
        ],
        "Value": [
            len(TEST_PINCODES), total_products, f"{duration:.2f}",
            f"{minutes:.2f}", f"{duration / len(TEST_PINCODES):.2f}",
            f"{total_products / minutes if minutes > 0 else 0:.2f}", 
            "Hyper-Threaded (Multi-Tab)"
        ]
    }
    perf_df = pd.DataFrame(metrics)
    perf_file = f"performance_metrics_TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    perf_df.to_excel(perf_file, index=False)
    logger.info(f"📊 Report saved: {perf_file}")

if __name__ == "__main__":
    asyncio.run(main())
