import asyncio
import logging
import csv
from datetime import datetime
from scrapers.instamart import InstamartScraper

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Instamart_Assortment_Runner")

# Configuration
PINCODES = ["560001"] # User requested pincode input list
# If TARGET_URL is the homepage, we crawl all categories. Otherwise we scrape the specific category.
TARGET_URL = "https://www.swiggy.com/instamart" 
# Example specific: "https://www.swiggy.com/instamart/category-listing?categoryName=Fresh%20Vegetables&custom_back=true&taxonomyType=CategoryListing&taxonomyId=1483"
OUTPUT_FILE = f"instamart_assortment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

async def main():
    logger.info("Starting Instamart Assortment Scraper...")
    scraper = InstamartScraper(headless=True)
    
    try:
        await scraper.start()
        
        all_results = []
        
        all_results = []
        
        for pincode in PINCODES:
            try:
                logger.info(f"Processing Pincode: {pincode}")
                await scraper.set_location(pincode)
                
                urls_to_scrape = []
                if "category-listing" in TARGET_URL or "collection" in TARGET_URL:
                    urls_to_scrape = [TARGET_URL]
                elif TARGET_URL == "https://www.swiggy.com/instamart" or TARGET_URL == "https://www.swiggy.com/instamart/":
                     logger.info("Target is homepage, discovering all categories...")
                     urls_to_scrape = await scraper.get_categories()
                     # If discovery fails, fallback to a sensible default or error?
                     if not urls_to_scrape:
                         logger.warning("No categories found on homepage. Using default/sample category.")
                         # Fallback/Sample
                         urls_to_scrape = ["https://www.swiggy.com/instamart/category-listing?categoryName=Fresh%20Vegetables&custom_back=true&taxonomyType=CategoryListing&taxonomyId=1483"]
                else:
                    urls_to_scrape = [TARGET_URL]

                logger.info(f"Will scrape {len(urls_to_scrape)} category URLs for pincode {pincode}")
                
                for cat_url in urls_to_scrape:
                    logger.info(f"Scraping URL: {cat_url}")
                    results = await scraper.scrape_assortment(cat_url, pincode=pincode)
                    
                    if results:
                        logger.info(f"Successfully scraped {len(results)} items")
                        all_results.extend(results)
                    else:
                        logger.warning(f"No data for {cat_url}")
                        
            except Exception as e:
                logger.error(f"Error for pincode {pincode}: {e}")
        
        if all_results:
            # Save to CSV
            fieldnames = all_results[0].keys()
            with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_results)
            
            logger.info(f"Saved total {len(all_results)} items to {OUTPUT_FILE}")
        else:
            logger.warning("No data collected.")
            
    except Exception as e:
        logger.error(f"Scraping failed: {e}", exc_info=True)
    finally:
        await scraper.stop()

if __name__ == "__main__":
    asyncio.run(main())
