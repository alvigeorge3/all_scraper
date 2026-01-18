# 🟣 Zepto: End-to-End Client Demo Runbook

This runbook outlines the exact steps to deploy, run, and present the Zepto data solution to your client.

## 📋 Prerequisites
Ensure you have the following ready:
1.  **Supabase Account**: [supabase.com](https://supabase.com) (Project created).
2.  **Streamlit Cloud Account** (Optional, for web hosting): [share.streamlit.io](https://share.streamlit.io).
3.  **Python Environment**: Dependencies installed (`pip install -r requirements.txt`).

---

## 🚀 Step 1: Database Setup (One-Time)

**Goal**: Prepare the cloud database to store scraped products.

1.  Log in to your **Supabase Dashboard**.
2.  Go to the **SQL Editor**.
3.  Open `setup_supabase.sql` from your project folder.
4.  Copy and paste the SQL code into the editor and click **Run**.
5.  Go to **Project Settings -> API** and copy:
    *   `Project URL`
    *   `anon public` Key
6.  Update your local `.env` file:
    ```ini
    SUPABASE_URL="https://your-project.supabase.co"
    SUPABASE_KEY="your-anon-key"
    ```

---

## 🕷️ Step 2: Generate Data (Scraping)

**Goal**: Scrape live data from Zepto to show real-time capabilities.

### Option A: Assortment Scraping (Category Crawl)
Run this to scrape a full category (e.g., Vegetables):
```bash
python run_zepto_assortment.py
```
*   **Output**: `zepto_data.csv`

### Option B: Availability Scraping (Input List)
Run this to scrape specific products from `zepto_input.xlsx`:
```bash
python run_zepto_availability.py
```
*   **Output**: `zepto_availability_YYYYMMDD_...csv`

---

## ☁️ Step 3: Sync to Cloud

**Goal**: Upload the local CSV data to your Supabase cloud database.

Run the uploader script (it automatically picks the latest CSV):
```bash
python upload_zepto_data.py
```
*   **Verify**: You should see a success message: `Successfully uploaded X records to Supabase.`

---

## 📊 Step 4: Visual Analytics (The "Wow" Factor)

**Goal**: Show the client the interactive dashboard.

Run the dashboard locally:
```bash
streamlit run zepto_dashboard.py
```

**Walkthrough for Client:**
1.  **Overview Metrics**: Show "Total Products" and "Avg Price" at the top.
2.  **Analytics Tab**: Show the "Price Distribution" histogram (pricing strategy insights).
3.  **Data Grid Tab**:
    *   Show the **Images**: Proves data quality.
    *   Show **Discount %**: Competitive intelligence.
    *   Click a **Link**: Show it opens the actual live product page.

---

## 🌐 Step 5: Web Deployment (Optional)

To satisfy "Deploy" requirement fully:
1.  Push this code to GitHub.
2.  Login to **Streamlit Cloud**.
3.  Deploy `zepto_dashboard.py`.
4.  Add your `SUPABASE_URL` and `SUPABASE_KEY` to the Streamlit Secret settings.
5.  **Share the URL** with your client!

---
*Generated: 2026-01-17*
