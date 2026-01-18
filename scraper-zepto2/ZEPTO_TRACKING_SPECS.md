# Zepto Scraper - Tracking Specifications & Logic Mapping

## 1. Objective
To scrape Zepto for **Assortment** (all categories/products) across different **Pincodes**.

## 2. Input Specifications

### Assortment Mode (`run_zepto_assortment.py`)
| Input | Source | Description |
| :--- | :--- | :--- |
| **Pincode** | CLI Argument `--pincode` | The target location code (e.g., `560001`). Required to fetch location-specific inventory. |
| **Website Link** | Base URL `https://www.zepto.com/` | The scraper auto-discovers *all* categories from the homepage. |

### Parallel Mode (`run_zepto_assortment_parallel.py`)
| Input | Source | Description |
| :--- | :--- | :--- |
| **Pincode List** | `pin_codes.xlsx` | Excel file with `Pincode` column. Script processes all unique pincodes in parallel. |

## 3. Data Fields Tracking Matrix

This matrix maps the required fields to the actual implementation in `scrapers/zepto.py`.

| Required Field | Field in Code | Source Logic (Simplified) |
| :--- | :--- | :--- |
| **Category** | `category` | Extracted from URL path (e.g., `/category/fruits-vegetables`). Converted to title case. |
| **Subcategory** | `subcategory` | Extracted from URL path segment 2. |
| **Item Name** | `name` | JSON: `name`, `product_name`, `title`, or `display_name` |
| **Brand** | `brand` | JSON: `brand` or `brand_name` field. |
| **Mrp** | `mrp` | JSON: `mrp`, `original_price`, or `list_price` (float). |
| **Price** | `price` | JSON: `price`, `selling_price`, or `discounted_price` (float). |
| **Weight** | `weight` | JSON: `weight`, `pack_size`, `unit`, or `size`. |
| **Delivery ETA** | `eta` | Extracted from page after setting pincode (regex search for "X minutes"). |
| **Availability** | `availability` | Logic: `Out of Stock` if `is_sold_out`, `out_of_stock`, or `inventory == 0`, else `In Stock`. |
| **Inventory** | `inventory` | JSON: `inventory`, `available_quantity`, `stock`, or `quantity` (integer). |
| **Store ID** | `store_id` | JSON: `store_id` or `merchant_id`. |
| **Base Product ID** | `base_product_id` | JSON: `id`, `product_id`, `_id`, or `base_product_id`. |
| **Product ID** | `product_id` | Same as base_product_id (for explicit requirement). |
| **Group ID** | `group_id` | JSON: `group_id` or `variant_group_id` (variants grouping). |
| **Merchant Type** | `merchant_type` | JSON: `merchant_type` or `seller_type`. |
| **Shelf Life** | `shelf_life_in_hours` | JSON: `shelf_life_in_hours`, `shelf_life_hours`, or `shelf_life`. |
| **Timestamp** | `scraped_at` | System time at scraping moment (YYYY-MM-DD HH:MM:SS format). |
| **Pincode Input** | `pincode_input`| The value passed to the function/CLI. |
| **Clicked Label** | `clicked_label`| `Category > Subcategory` string. |
| **Product URL** | `product_url` | JSON: `url` or `product_url`, or constructed from product name and ID. |
| **Image URL** | `image_url` | JSON: `image_url`, `image`, `thumbnail`, or `photo`. |

## 4. Technical Logic Explanation

### Location Setting Strategy
To ensure accurate data for the target pincode:

1. **Navigate**: Go to `https://www.zepto.com/`
2. **Trigger Modal**: Click location selector (tries multiple selectors):
   - Text: "Enter your delivery location", "Select location"
   - Buttons/inputs with "location", "pincode" keywords
   - Input fields with type="search"
3. **Input Pincode**: Type the 6-digit pincode into the search field
4. **Select Result**: Click suggestion from dropdown that matches pincode
5. **Extract ETA**: After location is set, extract delivery time from page (regex: `\d+\s*(?:minutes?|mins?)`)

**Selectors Used** (tries in order):
- Input: `[placeholder*='pincode']`, `[placeholder*='location']`, `input[type='search']`
- Suggestion: `div:has-text('{pincode}')`, `li:has-text('{pincode}')`, first suggestion

### Category Discovery Strategy

1. **Parse Homepage**: After setting location, extract all links from the page
2. **Filter Categories**: Look for URLs containing:
   - `/category/`
   - `/c/`
   - `/store/`
   - `/products/`
3. **Exclude**: Filter out cart, account, orders, profile pages
4. **Return**: Unique list of category URLs

**JavaScript Used**:
```javascript
Array.from(document.querySelectorAll('a'))
    .map(a => a.href)
    .filter(href => 
        href.includes('/category/') || 
        href.includes('/c/') ||
        href.includes('/store/') ||
        href.includes('/products/')
    )
```

### Data Extraction Strategy

**Hybrid Approach (JSON + DOM)**:

**Primary Method: Next.js Hydration JSON**
- Extract `window.__NEXT_DATA__` state object
- Recursively search for product objects containing:
  - ID field (`id`, `product_id`, `_id`)
  - Name field (`name`, `product_name`, `title`)
  - Price field (`price`, `selling_price`, `mrp`)
- This provides structured, complete data

**Fallback Method: Regex JSON Parsing**
- Search page content for JSON patterns
- Pattern: `{"id": ... "name": ... "price": ...}`
- Use `JSONDecoder` to parse found objects

**Benefits**:
- More reliable than DOM scraping
- Access to hidden fields (IDs, inventory, metadata)
- Faster execution
- Less brittle to UI changes

### Anti-Bot Measures

Implemented in `base.py`:

**Browser Launch Arguments**:
```python
--disable-blink-features=AutomationControlled
--disable-infobars
--no-sandbox
--disable-dev-shm-usage
```

**JavaScript Injection**:
```javascript
navigator.webdriver = undefined
```

**Human-Like Behaviors**:
- Random delays: 1-3 seconds between actions
- Mouse scrolling: Random scroll distances
- Natural typing: 50-200ms per character
- Cooling periods: 10-20s between pincodes

### Resource Blocking

For performance optimization:
```python
# Block images, media, fonts
if route.request.resource_type in ["image", "media", "font"]:
    await route.abort()
```

This reduces bandwidth and speeds up page loads.

## 5. Parallel Execution Architecture

**Producer-Consumer Pattern**:

```
Pincode Queue ➔ Worker 1 ➔ Result Queue ➔ Writer Task
             ➔ Worker 2 ➔             ➔
             ➔ Worker 3 ➔             ➔
             ➔ Worker 4 ➔             ➔
```

**Flow**:
1. **Producer**: Main thread loads pincodes from Excel and queues them
2. **Workers** (4 parallel): Each worker:
   - Dequeues a pincode
   - Creates dedicated browser instance
   - Sets location
   - Scrapes all categories
   - Pushes results to result queue
   - Waits 10-20s (anti-ban cooldown)
3. **Writer**: Dedicated async task writes batches to CSV

**Benefits**:
- 4x speed improvement
- Isolation: One worker crash doesn't affect others
- Efficient resource use

## 6. Output Format

**CSV Structure**:
- Filename: `zepto_assortment_YYYYMMDD_HHMMSS.csv`
- Encoding: UTF-8
- Headers: All field names from ProductItem model
- One row per product

**Sample Row**:
```csv
platform,category,subcategory,name,brand,price,mrp,weight,eta,availability,inventory,pincode_input,...
zepto,Fruits Vegetables,Fresh Fruits,Apple Shimla,Fresho,120.0,150.0,1 kg,10 minutes,In Stock,45,560001,...
```

## 7. Error Handling

**Location Setting Failures**:
- Tries multiple selector patterns
- Falls back to pressing Enter if no suggestion found
- Logs warnings but continues execution

**Category Scraping Failures**:
- Individual category failures logged but don't stop execution
- If no categories found, tries scraping homepage as fallback

**Product Extraction Failures**:
- Skips products with missing name or price
- Logs warnings for incomplete products
- Continues processing remaining products

## 8. Performance Metrics

**Expected Speed** (per worker):
- Location setting: 5-10 seconds
- Category discovery: 3-5 seconds
- Per category scraping: 5-15 seconds
- Products per minute: 100-200

**Resource Usage**:
- CPU: Moderate (4 browsers)
- RAM: ~2GB for 4 workers
- Network: ~100-500 KB/s per worker

## 9. Troubleshooting Guide

| Issue | Possible Cause | Solution |
|-------|---------------|----------|
| No categories found | Selectors changed | Update category link patterns in `get_all_categories()` |
| No products extracted | JSON structure changed | Update recursive search logic in `scrape_assortment()` |
| Location not set | Modal selectors changed | Update location trigger selectors in `set_location()` |
| 403/Bot detection | Too aggressive scraping | Increase delays, reduce workers |
| Incomplete data | Missing JSON fields | Add fallback field names in extraction logic |

## 10. Maintenance Notes

**When Zepto updates their website**:
1. Run scraper in non-headless mode: `--headless` flag removed
2. Observe which step fails (location, categories, products)
3. Inspect page source to find new selectors/JSON structure
4. Update corresponding method in `scrapers/zepto.py`
5. Test with single pincode before running parallel
