import asyncio
import logging
import os
import sys

# Add current directory to path to allow imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from run_blinkit_assortment_parallel import run_scraping
from upload_blinkit_data import process_upload

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("pipeline.log", encoding='utf-8')
    ]
)
logger = logging.getLogger("Pipeline_Orchestrator")

async def main():
    input_file = "pin_codes.xlsx"
    
    if not os.path.exists(input_file):
        logger.error(f"Input file '{input_file}' not found. Please ensure it exists.")
        return

    logger.info("🚀 Starting End-to-End Pipeline...")
    logger.info(f"Target Input: {input_file}")

    # Step 1: Run Scraping
    logger.info("--- Step 1: Scraping Data ---")
    output_csv = await run_scraping(input_file=input_file, max_workers=6)
    
    if not output_csv or not os.path.exists(output_csv):
        logger.error("Scraping failed or produced no output file. Aborting upload.")
        return

    logger.info(f"Scraping completed. CSV ready at: {output_csv}")

    # Step 2: Upload Data
    logger.info("--- Step 2: Uploading Data to Supabase ---")
    success = process_upload(output_csv, table_name="blinkit_products")
    
    if success:
        logger.info("✅ Pipeline completed successfully!")
    else:
        logger.error("❌ Stats Upload failed.")

if __name__ == "__main__":

    try:
        if sys.platform == 'win32':
             asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        asyncio.run(main())

    except KeyboardInterrupt:
        logger.info("Pipeline stopped by user.")
    except Exception as e:
        logger.error(f"Pipeline crashed: {e}")
