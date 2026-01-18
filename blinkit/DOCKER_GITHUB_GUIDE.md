# 🐳 Docker & GitHub Actions Automation Guide

This guide explains how to containerize the application and set up automated scheduled runs using GitHub Actions.

## 📦 Part 1: Docker
Docker allows you to package the scraper and all its dependencies (Python, Playwright, Browsers) into a single image that runs anywhere.

### 1. Build the Image
Open a terminal in the project folder:
```bash
docker build -t zepto-scraper .
```

### 2. Run the Container
To run the default automation loop (runs scraper -> uploader -> waits 60m):
```bash
docker run -d --name zepto-bot -e SUPABASE_URL="your_url" -e SUPABASE_KEY="your_key" zepto-scraper
```

To run a specific script once (e.g., just the scraper):
```bash
docker run --rm -e SUPABASE_URL="..." -e SUPABASE_KEY="..." zepto-scraper python run_zepto_availability.py
```

---

## ☁️ Part 2: GitHub Actions (Cron)
We have enabled a workflow file: `.github/workflows/zepto_cron.yml`.
This workflow runs **Every 6 Hours** automatically on GitHub's servers (free tier available).

### 1. Push Code to GitHub
Initialize a repo and push your code:
```bash
git init
git add .
git commit -m "Setup Zepto Scraper"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### 2. Configure Secrets (Critical!)
For the scraper to talk to Supabase, you must save your keys as "Secrets" in GitHub (do not commit them to code!).

1.  Go to your GitHub Repository page.
2.  Click **Settings** > **Secrets and variables** > **Actions**.
3.  Click **New repository secret**.
4.  Add:
    *   Name: `SUPABASE_URL` | Value: `your_supabase_url`
    *   Name: `SUPABASE_KEY` | Value: `your_supabase_anon_key`

### 3. Verify
1.  Go to the **Actions** tab in your repo.
2.  You should see "Zepto Scraper Cron" listed.
3.  You can manually trigger it by clicking "Run workflow" to test.
4.  Otherwise, it will run automatically on the schedule defined in the `.yml` file (`0 */6 * * *`).

---
*Generated: 2026-01-17*
