from database import Database
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestDB")

def test_connection():
    logger.info("Testing Supabase connection...")
    db = Database()
    if db.client:
        try:
            # Try to fetch 1 record to ensure table exists and permissions are right
            data = db.fetch_products(limit=1)
            logger.info("Connection Successful! Table exists.")
            logger.info(f"Fetched {len(data)} records.")
        except Exception as e:
            logger.error(f"Connection failed during fetch: {e}")
    else:
        logger.error("Client initialization failed.")

if __name__ == "__main__":
    test_connection()
