# Zepto Scraper Specifications
## Overview
This document serves as the technical specification for the Zepto Assortment and Availability Scraper. The scraper is designed to navigate the Zepto website (and potentially others with similar architecture) to extract product data based on pincode and category inputs.

## Data Requirement Mapping
The following table maps the user requirements to the implemented data model (`ProductItem` in `models.py`).

| User Requirement Field | Implemented Field | Data Type | Notes |
|------------------------|-------------------|-----------|-------|
| Category | `category` | `str` | Extracted from URL path or valid JSON data |
| Subcategory | `subcategory` | `str` | Extracted from URL path |
| Item Name | `name` | `str` | Product Title |
| Brand | `brand` | `str` | Brand Name |
| Mrp | `mrp` | `float` | Maximum Retail Price |
| Price or discountsellingrpice | `price` | `float` | Current Selling Price |
| Weight/pack_size | `weight` | `str` | Unit size (e.g., "500 g") |
| Delivery ETA | `eta` | `str` | e.g., "10 mins" |
| Availability (in_stock/out_of_stock) | `availability` | `str` | "In Stock" or "Out of Stock" |
| Inventory/available_quantity | `inventory` | `Optional[int]` | Raw stock count if exposed |
| Store ID | `store_id` | `Optional[str]` | Backend Store Identifier |
| Base Product ID | `base_product_id` | `Optional[str]` | Unique Product UUID |
| Shelf Life | `shelf_life_in_hours` | `Optional[int]` | Converted to hours if available |
| Timestamp | `scraped_at` | `str` | Time of scrape (YYYY-MM-DD HH:MM:SS) |
| Pincode Input | `pincode_input` | `str` | Pincode used for context |
| Clicked Label | `clicked_label` | `str` | Breadcrumb or Navigation path |

## Component Architecture

### 1. ZeptoScraper (`scrapers/zepto.py`)
the core class handling browser interactions.
- **`set_location(pincode: str)`**: Handles the location modal, inputs pincode, selects the first suggestion, and waits for the location context to update (ETA visible).
- **`scrape_assortment(category_url: str)`**: Navigates to a category page, inspects the DOM and JSON hydration data (using `__NEXT_DATA__` or similar patterns) to extract a list of products. Using JSON extraction ensures high reliability and access to hidden fields like `store_id` and `inventory`.
- **`scrape_availability(product_url: str)`**: Navigates to a specific product page to get detailed availability status, useful for checking stock on specific items.

### 2. Data Models (`scrapers/models.py`)
TypedDicts ensuring extraction consistency across different scrapers (Zepto, Blinkit, etc.).
- `ProductItem`: For assortment lists.
- `AvailabilityResult`: For targeted availability checks.

### 3. Runners
- **`run_zepto_availability.py`**: Reads `zepto_input.xlsx` (Pincodes & URLs) and runs `scrape_availability`.
- **(Proposed) `run_zepto_assortment.py`**: Will take Pincodes and Category URLs to run `scrape_assortment`.

## Strategy
1. **Hybrid Extraction**: The scraper prioritizes extracting data from the JSON objects embedded in the page HTML (Next.js hydration state) as it contains cleaner data types (floats, ints, UUIDs) than parsing the DOM.
2. **Resilient Location Setting**: Handles various states of the "Select Location" modal, including fallbacks for different UI variations.
3. **Smart Navigation**: Can recover from 404s or redirects if a deep link is invalid for a specific pincode (e.g., items not available in that city).

## Input Specifications
- **Pincode List**: A list of 6-digit valid pincodes (e.g., `560001`).
- **Target URLs**: 
    - For **Assortment**: Category URLs (e.g., `https://www.zepto.com/cn/fresh-vegetables/...`)
    - For **Availability**: Product URLs (e.g., `https://www.zepto.com/pn/onion-red...`)
