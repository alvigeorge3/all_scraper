# ⚡ Zepto Scraper

This module contains a high-performance scraper for Zepto, capable of fetching product assortment, prices, availability, and metadata for any pincode.

## 🚀 Key Features
*   **Assortment Scraping**: Fetches all categories and products for a given location.
*   **Availability Checking**: Checks stock status for specific product URLs.
*   **Parallel Execution**: Run multiple browser instances to scrape bulk pincodes fast.
*   **Flight Data Extraction**: Uses deep regex to extract hidden metadata (Inventory, Shelf Life) directly from Zepto's server responses.
*   **Dashboard**: A Streamlit-based UI to control scrapers and visualize data.

## 🛠️ Setup

1.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Environment Variables**
    Create a `.env` file in this directory with your Supabase credentials:
    ```env
    SUPABASE_URL=your_url
    SUPABASE_KEY=your_key
    ```
    *(Optional: Only needed if you want to upload data to the cloud database)*

## 🏃‍♂️ How to Run

### 1. Single Pincode Run (Visible Browser)
Scrape all products for a single location. Good for testing.

```bash
python run_zepto.py --pincode 560001
```
*   **Output**: `zepto_products_560001.csv`
*   **Note**: Edit `run_zepto.py` and set `headless=True` to hide the browser.

### 2. Bulk/Parallel Run
Scrape multiple pincodes simultaneously using a worker queue.

1.  Edit `pin_codes.xlsx` and add your target pincodes in the `Pincode` column.
2.  Run the script:
    ```bash
    python run_zepto_assortment_parallel.py
    ```
*   **Output**: `zepto_assortment_parallel_YYYYMMDD_....csv`

### 3. Dashboard (GUI)
Run the interactive dashboard to control scrapers and view metrics.

```bash
streamlit run dashboard/app_zepto.py
```
*   Access at: `http://localhost:8501`

## 📂 File Structure
*   `scrapers/zepto.py`: Core scraper logic (Playwright + Regex).
*   `run_zepto.py`: Script for single pincode execution.
*   `run_zepto_assortment_parallel.py`: Script for bulk parallel execution.
*   `dashboard/app_zepto.py`: Streamlit visualization app.
