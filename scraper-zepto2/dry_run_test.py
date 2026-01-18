"""Quick dry run to verify fields - scrapes just 2 categories."""
import asyncio
import csv
from scrapers.zepto import ZeptoScraper

async def main():
    scraper = ZeptoScraper(headless=True)
    all_products = []
    
    # Just 2 categories for quick test
    test_categories = [
        "https://www.zepto.com/cn/dairy-bread-eggs/butter/cid/4b938e02-7bde-4479-bc0a-2b54cb6bd5f5/scid/62b2b1eb-cd07-41b2-b567-cc878d2287fc",
        "https://www.zepto.com/cn/munchies/top-picks/cid/d2c2a144-43cd-43e5-b308-92628fa68596/scid/d648ea7c-18f0-4178-a202-4751811b086b",
    ]
    
    try:
        await scraper.start()
        await scraper.set_location("560001")
        
        for cat in test_categories:
            print(f"Scraping: {cat}")
            products = await scraper.scrape_assortment(cat, pincode="560001")
            all_products.extend(products)
            print(f"  -> Got {len(products)} products")
        
        # Save to CSV
        if all_products:
            with open("zepto_dry_run_v2.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=all_products[0].keys())
                writer.writeheader()
                writer.writerows(all_products)
            print(f"\n✓ Saved {len(all_products)} products to zepto_dry_run_sample.csv")
        
    finally:
        await scraper.stop()

if __name__ == "__main__":
    asyncio.run(main())
