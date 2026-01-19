import asyncio
import csv
import argparse
import os
import logging
from database import Database

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Blinkit_Uploader")

def clean_csv_keys(row: dict) -> dict:
    """
    Cleans CSV row keys to match Supabase schema if necessary.
    Converts numeric strings to proper types.
    """
    cleaned = dict(row)
    
    # Type conversion
    numeric_fields = ['price', 'mrp', 'inventory', 'variant_count', 'variant_in_stock_count', 'shelf_life_in_hours']
    for key in numeric_fields:
        if key in cleaned:
            val = cleaned[key]
            if val is None or val == "":
                cleaned[key] = None
            else:
                try:
                    if key in ['price', 'mrp']:
                        cleaned[key] = float(val)
                    else:
                        cleaned[key] = int(float(val))
                except:
                    cleaned[key] = None
    
    # Map fields
    if "product_url" in cleaned:
        cleaned["url"] = cleaned.pop("product_url")
        
    # Allowed columns (matching required schema)
    allowed_cols = {
        "product_id", "name", "price", "mrp", "availability", 
        "inventory", "category", "subcategory", "brand", 
        "store_id", "scraped_at", "pincode_input", "url",
        "weight", "eta", "group_id", "merchant_type", 
        "clicked_label", "base_product_id", "shelf_life_in_hours"
    }
    
    return {k: v for k, v in cleaned.items() if k in allowed_cols}


def process_upload(file_path: str, table_name: str = "blinkit_products") -> bool:
    """
    Reads a CSV file and uploads it to Supabase.
    Returns True if fully successful (or partially successful), False if fatal error.
    """
    if not os.path.exists(file_path):
        logger.error(f"File {file_path} does not exist.")
        return False

    db = Database()
    if not db.client:
        logger.error("Database connection failed. Check .env file.")
        return False

    records = []
    logger.info(f"Reading {file_path}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(clean_csv_keys(row))
                
        if not records:
            logger.warning("No records found in CSV.")
            return True # Not an error, just empty

        # Upload in batches of 100
        batch_size = 100
        total_batches = (len(records) + batch_size - 1) // batch_size
        
        logger.info(f"Found {len(records)} records. Uploading in {total_batches} batches...")
        
        for i in range(total_batches):
            batch = records[i*batch_size : (i+1)*batch_size]
            success = db.save_products(batch, table_name=table_name)
            if success:
                logger.info(f"Batch {i+1}/{total_batches} uploaded.")
            else:
                logger.error(f"Batch {i+1}/{total_batches} failed.")
                
        logger.info("Upload process completed.")
        return True
        
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Upload Blinkit CSV Data to Supabase")
    parser.add_argument("file", type=str, help="Path to the CSV file to upload")
    parser.add_argument("--table", type=str, default="blinkit_products", help="Target Supabase table name")
    args = parser.parse_args()

    process_upload(args.file, args.table)

if __name__ == "__main__":
    main()

