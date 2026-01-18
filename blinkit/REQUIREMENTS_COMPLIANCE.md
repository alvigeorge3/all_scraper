# Requirements Compliance Analysis

## Assortment Scraping Requirements vs Current Implementation

### ✅ Currently Implemented Fields

| Required Field | Current Field | Status | Notes |
|----------------|---------------|--------|-------|
| Category | `category` | ✅ Implemented | Primary category name |
| Item Name | `name` | ✅ Implemented | Product name |
| Brand | `brand` | ✅ Implemented | Brand name |
| MRP | `mrp` | ✅ Implemented | Maximum retail price |
| Price | `price` | ✅ Implemented | Selling/discounted price |
| Weight/pack_size | `weight` | ✅ Implemented | Product weight/size |
| Delivery ETA (mins) | `eta` | ✅ Implemented | Delivery time in minutes |
| Availability | `availability` | ✅ Implemented | in_stock/out_of_stock |
| store_id | `store_id` | ✅ Implemented | Store/warehouse ID |
| Timestamp | `scraped_at` | ✅ Implemented | When data was scraped |

### ❌ Missing Required Fields

| Required Field | Status | Notes |
|----------------|--------|-------|
| **Subcategory** | ❌ MISSING | Primary sub category - NOT currently captured |
| **Inventory/available_quantity** | ❌ MISSING | Stock quantity - NOT currently captured |
| **base_product_id** | ❌ MISSING | Product ID - NOT currently captured |
| **shelf_life_in_hours** | ❌ MISSING | Product shelf life - NOT currently captured |
| **pincode_input** | ❌ MISSING | Input pincode used for query - NOT currently captured |
| **clicked_label** | ❌ MISSING | Category/subcategory label clicked - NOT currently captured |

### ➕ Additional Fields (Not Required but Implemented)

| Field | Purpose |
|-------|---------|
| `platform` | Identifies which platform (blinkit/zepto/instamart) |
| `image_url` | Product image URL (useful for UI/verification) |
| `product_url` | Direct link to product page (useful for availability checks) |

---

## Summary

**Compliance Score: 10/16 fields (62.5%)**

### What's Working:
- ✅ Basic product information (name, brand, price, MRP, weight)
- ✅ Availability status
- ✅ Store ID
- ✅ Delivery ETA
- ✅ Timestamp

### What's Missing:
- ❌ **Subcategory** - Need to extract subcategory from page/URL
- ❌ **Inventory quantity** - Need to extract from JSON (if available)
- ❌ **Product ID** - Need to extract from JSON data
- ❌ **Shelf life** - Need to extract from product details
- ❌ **Pincode input** - Easy to add (already available in scraper)
- ❌ **Clicked label** - Need to track which category was clicked

---

## Recommended Actions

### Priority 1: Update Data Model
Update `scrapers/models.py` to include all 16 required fields:
```python
class ProductItem(TypedDict):
    # Existing fields
    platform: str
    category: str
    name: str
    brand: str
    mrp: float
    price: float
    weight: str
    eta: str
    availability: str
    store_id: Optional[str]
    scraped_at: str
    image_url: str
    product_url: str
    
    # NEW required fields to add
    subcategory: str
    inventory: Optional[int]  # available_quantity
    base_product_id: Optional[str]
    shelf_life_in_hours: Optional[int]
    pincode_input: str
    clicked_label: str
```

### Priority 2: Update All Scrapers
Each scraper (Blinkit, Zepto, Instamart) needs to:
1. Extract subcategory from URL/page
2. Extract inventory/quantity from JSON
3. Extract product ID from JSON
4. Extract shelf life from product details (if available)
5. Pass pincode_input to scrape_assortment method
6. Track clicked_label (category breadcrumb)

### Priority 3: Update CSV Generation
Update `generate_csvs.py` to:
- Pass pincode to scrapers
- Export all new fields to CSV

---

## Field Extraction Feasibility

| Field | Blinkit | Zepto | Instamart | Notes |
|-------|---------|-------|-----------|-------|
| subcategory | ✅ Likely | ✅ Likely | ✅ Likely | Can extract from URL or breadcrumb |
| inventory | ⚠️ Maybe | ⚠️ Maybe | ⚠️ Maybe | May not be in JSON for all sites |
| base_product_id | ✅ Yes | ✅ Yes | ✅ Yes | Already in JSON data |
| shelf_life | ❌ Unlikely | ❌ Unlikely | ❌ Unlikely | Usually not available for fresh produce |
| pincode_input | ✅ Easy | ✅ Easy | ✅ Easy | Already available in scraper |
| clicked_label | ✅ Easy | ✅ Easy | ✅ Easy | Can construct from category URL |

---

Generated: 2026-01-17 13:46
