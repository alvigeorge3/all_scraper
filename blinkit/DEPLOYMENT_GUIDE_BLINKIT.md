# 🚀 Blinkit Dashboard Deployment Guide

This guide covers how to deploy the Blinkit Scraper & Dashboard using **Supabase** (Database) and **Streamlit** (Frontend).

## 1️⃣ Supabase Setup

*(Reuse the same Supabase project as Zepto)*

1.  **Ensure Table Exists**:
    Run `setup_supabase.sql` if you haven't already (it handles both platforms).
2.  **Verify .env**:
    Ensure your `.env` contains:
    ```ini
    SUPABASE_URL="your_project_url"
    SUPABASE_KEY="your_anon_public_key"
    ```

## 2️⃣ Sync Data

Upload your locally scraped Blinkit CSV data to Supabase using the helper script:

```bash
python upload_blinkit_data.py
```
*   *Expected Output*: `Successfully uploaded X records to Supabase.`

## 3️⃣ Run Dashboard Locally

Start the Streamlit app. It will fetch data from Supabase first.

```bash
streamlit run blinkit_dashboard.py
```

## 4️⃣ Deploy to Streamlit Cloud

1.  Push code to GitHub.
2.  Go to [share.streamlit.io](https://share.streamlit.io).
3.  Deploy `blinkit_dashboard.py`.
4.  Add secrets (`SUPABASE_URL`, `SUPABASE_KEY`) in the Streamlit Cloud dashboard settings.
