# Blinkit Scraper - Tracking Specifications & Logic Mapping

## 1. Objective
To scrape Blinkit (formerly Grofers) for **Assortment** (Categories) and **Availability** (Specific SKUs) across different **Pincodes**.

## 2. Input Specifications

### A. Assortment Mode (`run_blinkit_assortment.py`)
| Input | Source | Description |
| :--- | :--- | :--- |
| **Pincode** | CLI Argument `--pincode` | The target location code (e.g., `560001`). Required to fetch location-specific inventory. |
| **Website Link** | CLI Argument `--url` | The starting category URL. If not provided or homepage, the scraper auto-discovers *all* categories. |

### B. Availability Mode (`run_blinkit_availability.py`)
| Input | Source | Description |
| :--- | :--- | :--- |
| **Pincode List** | `blinkit_input.xlsx` | The Excel file must contain `Pincode` column. The script iterates through unique pincodes found here. |
| **Product URLs** | `blinkit_input.xlsx` | The Excel file must contain `Product_Url` column. These specific items are checked for the corresponding pincode. |

## 3. Data Fields Tracking Matrix

This matrix maps the user's required fields to the actual implementation in `scrapers/blinkit.py`.

| Required Field | Field in Code | Source Logic (Simplified) |
| :--- | :--- | :--- |
| **Category** | `category` | Extracted from URL path (e.g., `/cn/vegetables-fruits/...`). |
| **Subcategory** | `subcategory` | Extracted from URL path segment 2. |
| **Item Name** | `name` | JSON `product_name` or `display_name` |
| **Brand** | `brand` | JSON `brand` field. |
| **Mrp** | `mrp` | JSON `mrp` (float). |
| **Price** | `price` | JSON `price` (float). |
| **Weight** | `weight` | JSON `unit` or `quantity_info`. |
| **Delivery ETA** | `eta` | Captured from the Location Bar text ("12 minutes") after setting pincode. |
| **Availability** | `availability` | Logic: `In Stock` if inventory > 0 else `Out of Stock`. |
| **Inventory** | `inventory` | JSON `inventory` (integer count). |
| **Merchant ID** | `store_id` | JSON `merchant_id`. |
| **Product ID** | `product_id` | JSON `product_id`. |
| **Group ID** | `group_id` | JSON `group_id` (variants grouping). |
| **Merchant Type** | `merchant_type` | JSON `merchant_type`. |
| **Timestamp** | `scraped_at` | System time at scraping moment. |
| **Pincode Input** | `pincode_input`| The value passed to the function/CLI. |
| **Clicked Label** | `clicked_label`| `Category > Subcategory` string. |

## 4. Technical Logic Explanation

### Location Setting Strategy
To ensure accurate data for `pin560001`:
1.  **Trigger**: The scraper clicks the location bar (typically "Delivery in..." or location icon).
2.  **Input**: Types `560001` into the modal search box.
3.  **Selection**: Waits for the suggestion list to populate and clicks the result matching the text `560001`.
4.  **Verification**: Scrapes the resulting "Delivery ETA" to confirm location context is active.

### Data Extraction Strategy
**Hybrid Approach (JSON + DOM)**:
- The scraper primarily intercepts the **Next.js Hydration JSON** embedded in the HTML `div#__NEXT_DATA__`.
- **Benfits**: This provides raw, structured data (IDs, exact prices, inventory counts) that is often hidden or harder to parse from the visible UI.
- **Failover**: If JSON is missing, it falls back to reading visible text (DOM) for critical fields like Name and Price.
