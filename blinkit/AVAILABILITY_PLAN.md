# Availability Scraping & Separation Plan

## ❌ Current Status: Partially Fulfilled

### 1. Assortment Scraping (Category Pages)
- **Status:** ✅ **Fulfilled** (Logic-wise)
- **Code:** `scrapers/blinkit.py`, `scrapers/zepto.py`, `scrapers/instamart.py`
- **Output:** Extracts all 18 required fields.
- **Pending:** Instamart location execution (timeout issue).

### 2. Availability Scraping (Product Pages)
- **Status:** ❌ **Not Started** (Major Gap)
- **Requirement:** Read Excel with URLs/Pincodes, scrape detailed fields.
- **Missing Fields:**
  - Seller Name & Address
  - Manufacturer Name & Address
  - Marketer Name & Address
  - Number of alternative weights available
  - Number of alternative weights in stock

### 3. "Separate Application" Requirement
- **Status:** ⚠️ **Needs Restructuring**
- **Current:** Single `generate_csvs.py` runs everything.
- **New Approach:** Create distinct entry points for each platform and mode.

---

## 🚀 Implementation Plan

### Phase 1: Separate Applications (Refactoring)
Create dedicated runner scripts for each platform to ensure they can operate independently as requested.

| Platform | Assortment Script | Availability Script |
|----------|-------------------|---------------------|
| **Blinkit** | `run_blinkit_assortment.py` | `run_blinkit_availability.py` |
| **Zepto** | `run_zepto_assortment.py` | `run_zepto_availability.py` |
| **Instamart** | `run_instamart_assortment.py` | `run_instamart_availability.py` |

### Phase 2: Availability Logic (New Features)

#### Step 1: Excel Input Reader
- Create `utils/excel_reader.py`
- Input Format: columns `[pincode, product_url]`
- Logic: Group by Pincode to minimize location setting calls.

#### Step 2: Product Page Scrapers
Update `scrape_availability` in each scraper to extract detailed metadata:

**Blinkit Fields to Add:**
- `seller_details` (Name/Address)
- `manufacturer_details`
- `marketer_details`
- `alternative_weights_info` (Count total, Count in-stock)

**Zepto Fields to Add:**
- `key_features` (often contains manufacturer info)
- `product_details`
- `variants` (Alternative weights)

**Instamart Fields to Add:**
- `manufacturer_info`
- `product_details`
- `variants`

#### Step 3: Output Generation
- Save results to `[platform]_availability_[timestamp].csv` automatically.

---

## ⏱️ Estimated Timeline
1. **Refactoring Runners:** 30 mins
2. **Excel Reader:** 30 mins
3. **Blinkit Availability Logic:** 1 hour
4. **Zepto Availability Logic:** 1 hour
5. **Instamart Availability Logic:** 1 hour

**Total:** ~4-5 hours

---

Generated: 2026-01-17 14:38
