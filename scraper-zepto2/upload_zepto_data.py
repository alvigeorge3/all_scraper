import argparse
import logging
import pandas as pd
from database import Database

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Upload_Zepto_Data")

BATCH_SIZE = 1000  # Upload in batches to avoid timeouts

def main():
    parser = argparse.ArgumentParser(description='Upload Zepto CSV data to Supabase')
    parser.add_argument('--file', type=str, required=True, help='Path to CSV file to upload')
    parser.add_argument('--table', type=str, default='zepto_products', help='Supabase table name (default: zepto_products)')
    args = parser.parse_args()
    
    csv_file = args.file
    table_name = args.table
    
    logger.info(f"Reading CSV file: {csv_file}")
    
    try:
        # Read CSV
        df = pd.read_csv(csv_file)
        logger.info(f"Loaded {len(df)} records from CSV")
        
        # Convert to list of dictionaries
        records = df.to_dict('records')
        
        # Initialize database
        db = Database()
        if not db.client:
            logger.error("Failed to initialize Supabase client. Check your .env file.")
            return
        
        # Upload in batches
        total = len(records)
        uploaded = 0
        
        for i in range(0, total, BATCH_SIZE):
            batch = records[i:i+BATCH_SIZE]
            logger.info(f"Uploading batch {i//BATCH_SIZE + 1} ({len(batch)} records)...")
            
            success = db.save_products(batch, table_name=table_name)
            
            if success:
                uploaded += len(batch)
                logger.info(f"  ✓ Progress: {uploaded}/{total} records uploaded")
            else:
                logger.error(f"  ✗ Failed to upload batch {i//BATCH_SIZE + 1}")
        
        logger.info(f"Upload complete! {uploaded}/{total} records successfully uploaded to {table_name}")
        
    except FileNotFoundError:
        logger.error(f"File not found: {csv_file}")
    except Exception as e:
        logger.error(f"Error during upload: {e}", exc_info=True)

if __name__ == "__main__":
    main()
