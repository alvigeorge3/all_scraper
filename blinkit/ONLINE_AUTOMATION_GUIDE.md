# ☁️ Online Automation Guide: GitHub Actions

You asked for **Online Automated Deployment**. This guide explains how to use **GitHub Actions** to run your scraper completely in the cloud for **FREE**, without using your own computer or Docker.

## ✅ How It Works
1.  **Code Hosting**: You upload this project to GitHub.
2.  **Scheduling**: GitHub runs your scraper every 6 hours automatically.
3.  **Storage**: The data is sent to Supabase.
4.  **Visuals**: Your Streamlit Dashboard (hosted on Streamlit Cloud) shows the data.

---

## 🚀 Step 1: Push Code to GitHub

1.  **Create a New Repository** on [github.com](https://github.com/new). Name it `zepto-scraper`.
2.  **Upload Files**:
    *   If you have Git installed:
        ```bash
        git init
        git add .
        git commit -m "Initial commit"
        git branch -M main
        git remote add origin https://github.com/YOUR_USERNAME/zepto-scraper.git
        git push -u origin main
        ```
    *   **Manual Upload**: You can also drag-and-drop files on the GitHub website, but make sure to include:
        *   `run_zepto_availability.py`
        *   `upload_zepto_data.py`
        *   `database.py` (Crucial! Handles DB connections)
        *   `requirements.txt`
        *   `zepto_input.xlsx` (Crucial for Zepto)
        *   `blinkit_input.xlsx` (Crucial for Blinkit)
        *   `.github/workflows/zepto_cron.yml` (This is the automation brain)
        *   `.github/workflows/blinkit_cron.yml` (Blinkit automation)
        *   `scrapers/` folder
        *   `utils/` folder

## 🔑 Step 2: Configure "Secrets" (Critical)

GitHub needs your Supabase passwords to upload data.

1.  Go to your Repository on GitHub.
2.  Click **Settings** (Top right tab).
3.  In the left sidebar, click **Secrets and variables** > **Actions**.
4.  Click **New repository secret**.
5.  Add these two secrets (copy from your `.env` file):
    *   **Name**: `SUPABASE_URL`
        *   **Value**: `https://your-project.supabase.co`
    *   **Name**: `SUPABASE_KEY`
        *   **Value**: `your-long-anon-key`

## 🟢 Step 3: Turn It On

1.  Go to the **Actions** tab in your repository.
2.  You should see "Zepto Scraper Cron" on the left.
3.  Click it.
4.  You might see a button saying "I understand my workflows, go ahead and enable them". Click it.
5.  **Test Run**: Click **Run workflow** (Blue button on the right) -> **Run workflow**.

## 🎯 Result
*   The scraper will now run **automatically every 6 hours**.
*   It handles everything: installing browsers, scraping, and uploading.
*   You don't need to keep your laptop open!

---
*Generated: 2026-01-17*
