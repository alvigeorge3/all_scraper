import subprocess
import time
import logging
import schedule
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("zepto_automation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Zepto_Auto_Bot")

def run_pipeline():
    logger.info("🚀 Starting Zepto Automation Pipeline...")
    
    # Step 1: Run Scraper
    logger.info("Step 1: Running Scraper...")
    try:
        # Using availability runner as it's the most targeted
        result = subprocess.run(["python", "run_zepto_availability.py"], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("✅ Scraper finished successfully.")
            logger.info(result.stdout)
        else:
            logger.error(f"❌ Scraper failed:\n{result.stderr}")
            return # Stop if scraper fails
    except Exception as e:
        logger.error(f"Failed to execute scraper: {e}")
        return

    # Step 2: Upload to Cloud
    logger.info("Step 2: Uploading to Supabase...")
    try:
        result = subprocess.run(["python", "upload_zepto_data.py"], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("✅ Upload finished successfully.")
            logger.info(result.stdout)
        else:
            logger.error(f"❌ Upload failed:\n{result.stderr}")
    except Exception as e:
        logger.error(f"Failed to execute uploader: {e}")

    logger.info("🏁 Pipeline completed. Waiting for next schedule...")

def main():
    logger.info("Bot started. Scheduling scraping job every 1 hour.")
    
    # Run immediately once
    run_pipeline()
    
    # Schedule every 60 minutes
    schedule.every(60).minutes.do(run_pipeline)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    # Ensure dependencies are installed: pip install schedule
    try:
        import schedule
    except ImportError:
        logger.error("Module 'schedule' not found. Please run: pip install schedule")
        exit(1)
        
    main()
