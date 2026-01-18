
import pandas as pd
import asyncio
import os
import glob
import subprocess
import sys
import logging
from datetime import datetime

# Set basic logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("DryRun")

def setup_availability_input():
    """Creates a sample input file for availability scraping."""
    logger.info("Setting up blinkit_input.xlsx...")
    data = [
        {"Pincode": "560001", "Product_Url": "https://blinkit.com/prn/amul-buffalo-a2-milk/prid/547185"},
        {"Pincode": "560001", "Product_Url": "https://blinkit.com/prn/amul-taaza-toned-milk/prid/19512"}
    ]
    df = pd.DataFrame(data)
    df.to_excel("blinkit_input.xlsx", index=False)
    logger.info("Created blinkit_input.xlsx with 2 sample URLs.")

def run_script(script_name, args=[]):
    """Runs a python script as a subprocess."""
    logger.info(f"Running {script_name}...")
    cmd = [sys.executable, script_name] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"Error running {script_name}: {result.stderr}")
    else:
        logger.info(f"{script_name} completed.")
        # logger.info(result.stdout) # Uncomment for debug

def get_latest_file(pattern):
    """Returns the latest file matching the pattern."""
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getctime)

def main():
    # 1. Setup Input
    setup_availability_input()

    # 2. Run Assortment Scraper (Milk Category)
    logger.info("--- Starting Assortment Dry Run ---")
    run_script("run_blinkit_assortment.py", ["--pincode", "560001", "--url", "https://blinkit.com/cn/milk/cid/14/922", "--headless"])

    # 3. Run Availability Scraper
    logger.info("--- Starting Availability Dry Run ---")
    run_script("run_blinkit_availability.py")

    # 4. Convert to Excel
    logger.info("--- Generating Excel Report ---")
    
    assortment_csv = get_latest_file("blinkit_assortment_*.csv")
    availability_csv = get_latest_file("blinkit_availability_*.csv")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_excel = f"Blinkit_Dry_Run_{timestamp}.xlsx"
    
    with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
        if assortment_csv:
            df_assort = pd.read_csv(assortment_csv)
            df_assort.to_excel(writer, sheet_name="Assortment", index=False)
            logger.info(f"Added Assortment data ({len(df_assort)} rows)")
        else:
            logger.warning("No Assortment CSV found.")
            
        if availability_csv:
            df_avail = pd.read_csv(availability_csv)
            df_avail.to_excel(writer, sheet_name="Availability", index=False)
            logger.info(f"Added Availability data ({len(df_avail)} rows)")
        else:
            logger.warning("No Availability CSV found.")

    logger.info(f"✅ Dry Run Complete. Output: {output_excel}")

if __name__ == "__main__":
    main()
