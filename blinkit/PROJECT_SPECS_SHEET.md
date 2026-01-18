# 📋 Project Specifications & Progress Report

**Project Name:** Chrono-Nova E-commerce Scraper
**Date:** 2026-01-18
**Version:** 1.0 (Integration Phase)

---

## 1. 🎯 Project Objective
To develop a robust, automated scraping solution for three major Quick Commerce platforms in India: **Zepto**, **Blinkit**, and **Instamart**.
The system extracts real-time product data (Price, Availability, Inventory, Metadata) based on granular Pincode inputs.

---

## 2. 🏗️ High-Level Architecture
The project follows a modular "Micro-Runner" architecture to ensure isolation and reliability.

| Layer | Components | Description |
| :--- | :--- | :--- |
| **Data Acquisition** | `scrapers/` | Core classes using **Playwright** (Async) for browser automation. |
| **Orchestration** | `run_*.py` | 6 standalone scripts separating platforms and use-cases (Assortment vs. Availability). |
| **Storage** | `database.py` | Unified interface for **Supabase** (PostgreSQL) and local CSV fallback. |
| **Visualization** | `*_dashboard.py`| Interactive **Streamlit** apps for analytics and data inspection. |
| **Automation** | GitHub Actions | Cloud-native Cron jobs running every 6 hours (Serverless). |

---

## 3. 🛠️ Implemented Features

### A. Scraping Capabilities
| Feature | Zepto | Blinkit | Instamart |
| :--- | :---: | :---: | :---: |
| **Assortment Mode** | ✅ | ✅ | ✅ |
| **Availability Mode** | ✅ | ✅ | ✅ |
| **Pincode Injection** | ✅ | ✅ | ✅ |
| **JSON Extraction** | ✅ (Hybrid) | ✅ (Pure) | ✅ (JSON-LD) |
| **Anti-Bot Stealth** | ✅ (Custom Patch) | ✅ | ✅ |
| **Detailed Meta** | Seller, Mfr, Marketer | Seller, Mfr | Seller, Mfr |

### B. "Availability Mode" (Excel Driven)
A specialized feature where the system reads an Input Excel file (`Pincode`, `Product_Url`) and iterates through specific products to track stock levels and price changes.
*   **Input**: `zepto_input.xlsx`, etc.
*   **Logic**: Groups URLs by Pincode to minimize location-setting overhead (1 setup per N products).
*   **Output**: Detailed CSVs + Cloud Sync.

### C. Anti-Bot Engineering
Implemented a "Stealth Patch" in `scrapers/base.py` to bypass Cloudflare/403 errors:
1.  **Flag Removal**: `--disable-blink-features=AutomationControlled`
2.  **Fingerprint Masking**: `navigator.webdriver = undefined`
3.  **User-Agent**: Rotated modern Chrome definitions.

---

## 4. ☁️ Deployment & DevOps

### Online Automation (GitHub Actions)
*   **Zero-Infrastructure**: Runs entirely on GitHub's free runners.
*   **Schedule**: Configured for 6-hour intervals (CRON `0 */6 * * *`).
*   **Workflows**:
    *   `.github/workflows/zepto_cron.yml`
    *   `.github/workflows/blinkit_cron.yml`
*   **Secrets Management**: Uses GitHub Secrets for Supabase credentials.

### Data Dashboard
*   **Stack**: Streamlit + Plotly + Pandas.
*   **Features**:
    *   Live connection to Supabase.
    *   Local CSV fallback (Robustness).
    *   Price Distribution Charts & Out-of-Stock Metrics.
    *   Direct links to product pages.

---

## 5. 📂 Key Deliverables (File Manifest)

### Core Code
*   `scrapers/base.py`: The engine (Browser management, Stealth).
*   `scrapers/zepto.py`: Zepto logic (JSON + DOM Fallback).
*   `scrapers/blinkit.py`: Blinkit logic (API interception).
*   `scrapers/instamart.py`: Instamart logic.

### Runners (Entry Points)
*   `run_zepto_availability.py`
*   `run_blinkit_availability.py`
*   `upload_zepto_data.py`: Sync script.
*   `upload_blinkit_data.py`: Sync script.

### Documentation
*   `ONLINE_AUTOMATION_GUIDE.md`: **Master guide** for cloud setup.
*   `ZEPTO_CLIENT_DEMO_RUNBOOK.md`: Step-by-step demo script.
*   `DOCKER_GITHUB_GUIDE.md`: Containerization docs.

---

## 6. 🚦 Traceability Matrix

| Requirement | Implementation Status | Notes |
| :--- | :--- | :--- |
| **Scrape 3 Platforms** | 🟡 Partial | Zepto/Blinkit Perfect. Instamart logic exists but location UI is flaky. |
| **Input Format** | ✅ Complete | Excel Reader (`utils/excel_reader.py`) works perfectly. |
| **Data Fields** | ✅ Complete | Added Manufacturer, Inventory, Variant counts. |
| **Automation** | ✅ Complete | GitHub Actions Pipeline verified. |
| **Client Demo** | ✅ Complete | Dashboards and Data Grids ready. |

---

## 7. ⏭️ Next Steps
1.  **Monitor Online Runs**: Watch GitHub Actions for stability over 24h.
2.  **Instamart Tuning**: Adjust timeout/selectors for Instamart location setting if needed.
3.  **Scale**: Add more products to `*_input.xlsx` files in the repo.
