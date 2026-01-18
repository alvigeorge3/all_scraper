import asyncio
import logging
import argparse
import csv
from datetime import datetime
from scrapers.zepto import ZeptoScraper

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Zepto_Assortment_Runner")

async def main():
    parser = argparse.ArgumentParser(description='Scrape Zepto assortment for a single pincode')
    parser.add_argument('--pincode', type=str, default='560001', help='Pincode to scrape (default: 560001)')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    args = parser.parse_args()
    
    pincode = args.pincode
    output_file = f"zepto_assortment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    logger.info(f"Starting Zepto assortment scraper for pincode: {pincode}")
    
    scraper = ZeptoScraper(headless=args.headless)
    all_products = []
    
    try:
        await scraper.start()
        logger.info("Browser started successfully")
        
        # Set location
        await scraper.set_location(pincode)
        logger.info(f"Location set to {pincode}")
        
        # Get all categories
        await asyncio.sleep(2)
        categories = await scraper.get_all_categories()
        logger.info(f"Found {len(categories)} categories to scrape")
        
        if not categories:
            logger.warning("No categories found. This might indicate a problem with category extraction.")
            # Try scraping the homepage itself as a fallback
            logger.info("Attempting to scrape homepage as fallback...")
            products = await scraper.scrape_assortment(scraper.base_url, pincode=pincode)
            all_products.extend(products)
        else:
            # Scrape each category
            for i, cat_url in enumerate(categories, 1):
                try:
                    logger.info(f"[{i}/{len(categories)}] Scraping category: {cat_url}")
                    products = await scraper.scrape_assortment(cat_url, pincode=pincode)
                    
                    if products:
                        all_products.extend(products)
                        logger.info(f"  ✓ Extracted {len(products)} products")
                    else:
                        logger.warning(f"  ⚠ No products found in {cat_url}")
                    
                    # Delay between categories to avoid rate limiting
                    await scraper.human_delay(2, 4)
                    
                except Exception as e:
                    logger.error(f"  ✗ Failed to scrape {cat_url}: {e}")
                    continue
        
        # Save to CSV
        if all_products:
            logger.info(f"Saving {len(all_products)} products to {output_file}")
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=all_products[0].keys())
                writer.writeheader()
                writer.writerows(all_products)
            
            logger.info(f"✓ Successfully saved data to {output_file}")
        else:
            logger.warning("No products were scraped. Please check the logs for errors.")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        await scraper.stop()
        logger.info("Scraper stopped")

if __name__ == "__main__":
    asyncio.run(main())
