# 🚀 Zepto Dashboard Deployment Guide

This guide covers how to deploy the Zepto Scraper & Dashboard using **Supabase** (Database) and **Streamlit** (Frontend).

## 1️⃣ Supabase Setup (Database)

1.  **Create a Supabase Project**: Go to [supabase.com](https://supabase.com) and create a new project.
2.  **Run SQL Schema**:
    *   Go to the **SQL Editor** in your Supabase dashboard.
    *   Open `setup_supabase.sql` from this project.
    *   Copy the content and run it to create the `products` table.
3.  **Get Credentials**:
    *   Go to **Project Settings** -> **API**.
    *   Copy the `Project URL` and `anon public` Key.

## 2️⃣ Local Configuration

1.  **Update `.env`**:
    Create or update your `.env` file in the project root:
    ```ini
    SUPABASE_URL="your_project_url"
    SUPABASE_KEY="your_anon_public_key"
    ```

## 3️⃣ Sync Data

Upload your locally scraped CSV data to Supabase using the helper script:

```bash
python upload_zepto_data.py
```
*   *Expected Output*: `Successfully uploaded X records to Supabase.`

## 4️⃣ Run Dashboard Locally

Start the Streamlit app. It will now try to fetch data from Supabase first, falling back to CSV if needed.

```bash
streamlit run zepto_dashboard.py
```

## 5️⃣ Deploy to Streamlit Cloud (Optional)

1.  Push this code to a GitHub repository.
2.  Go to [share.streamlit.io](https://share.streamlit.io) and connect your repo.
3.  Select `zepto_dashboard.py` as the main file.
4.  **Important**: In **Advanced Settings**, add your secrets:
    ```toml
    SUPABASE_URL = "your_project_url"
    SUPABASE_KEY = "your_anon_public_key"
    ```
5.  Click **Deploy**! 🎈
