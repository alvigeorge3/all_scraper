# 🤖 Zepto Automation Guide: "Set It & Forget It"

This guide explains how to automate the Zepto scraping and uploading process so it runs continuously without manual intervention.

## ✅ Overview of Automation
We have created a master script: **`automate_zepto.py`**. 

This script acts as a "Bot" that:
1.  **Runs the Availability Scraper** (`run_zepto_availability.py`).
2.  **Checks for Success**.
3.  **Runs the Cloud Uploader** (`upload_zepto_data.py`).
4.  **Waits for 60 minutes** (configurable).
5.  **Repeats** forever.

---

## 🚀 Option 1: Simple Python Loop (Recommended for Demo)

This method is easiest for showing the client. It keeps a terminal window open running the bot.

**Steps:**
1.  **Install Schedule Library**:
    ```bash
    pip install schedule
    ```
2.  **Run the Bot**:
    ```bash
    python automate_zepto.py
    ```
3.  **Observe**:
    - The bot will run immediately once.
    - It will print logs: `🚀 Starting Zepto Automation Pipeline...`
    - After finishing, it will say: `🏁 Pipeline completed. Waiting for next schedule...`
    - It will run again automatically after 1 hour.

---

## 📅 Option 2: Windows Task Scheduler (For Production)

This method runs the script in the background, even if you close the terminal.

1.  **Open Task Scheduler** (Search in Start Menu).
2.  **Create Basic Task**: Name it "Zepto Scraper Bot".
3.  **Trigger**: Select "Daily" or "One time" (and repeat every 1 hour in advanced settings).
4.  **Action**: "Start a program".
    - **Program/script**: `python` (Path to your python.exe, e.g., `C:\Python39\python.exe`)
    - **Add arguments**: `automate_zepto.py`
    - **Start in**: `C:\Users\...\chrono-nova\` (Full path to your project folder).
5.  **Finish**.

---

## 🛠️ Configuration
To change the frequency (e.g., run every 30 mins), edit `automate_zepto.py`:

```python
# Change 60 to 30
schedule.every(30).minutes.do(run_pipeline)
```

---
*Generated: 2026-01-17*
