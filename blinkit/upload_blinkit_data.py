import pandas as pd
import glob
import os
import logging
from database import db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Blinkit_Uploader")

def main():
    # 1. Find latest Blinkit CSV
    files = glob.glob("blinkit_*.csv")
    if not files:
        logger.error("No Blinkit CSV files found to upload.")
        return

    latest_file = max(files, key=os.path.getctime)
    logger.info(f"Read latest file: {latest_file}")
    
    # 2. Read Data
    try:
        df = pd.read_csv(latest_file)
        if df.empty:
            logger.warning("CSV is empty.")
            return
            
        logger.info(f"Loaded {len(df)} rows.")
        
        # 3. Upload
        logger.info("Starting upload to Supabase...")
        db.upsert_products(df, platform="blinkit")
        logger.info("Upload process completed.")
        
    except Exception as e:
        logger.error(f"Error processing file: {e}")

if __name__ == "__main__":
    main()
