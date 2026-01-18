# Full Requirements Analysis - Gaps Identified

## Assortment Scraping

### Blinkit - Missing Fields ❌
**Requirement:** Category, Subcategory, Item Name, Brand, Mrp, Price, Weight, Delivery ETA, availability, inventory, **merchant_id**, **product_id**, **group_id**, **merchant_type**, timestamp, pincode_input, clicked_label

**Currently Missing:**
- ❌ `group_id` - NOT implemented
- ❌ `merchant_type` - NOT implemented

**Field Mapping Issues:**
- ✅ `product_id` → Implemented as `base_product_id`
- ✅ `merchant_id` → Implemented as `store_id` (need to verify if same)

---

### Zepto - Complete ✅
**Requirement:** Category, Subcategory, Item Name, Brand, Mrp, Price, Weight, Delivery ETA, availability, inventory, store_id, base_product_id, shelf_life_in_hours, timestamp, pincode_input, clicked_label

**Status:** All fields implemented ✅

---

### Instamart - Complete ✅  
**Requirement:** Similar to Zepto (figure out)

**Status:** All common fields implemented ✅

---

## Availability Scraping - NOT IMPLEMENTED ❌

### What's Required:
1. Read Excel file with:
   - Product URLs
   - Pincodes/addresses

2. For each product URL + pincode combination:
   - Navigate to product page
   - Extract detailed product information

### Blinkit Availability Fields Required:
- Timestamp ✅
- Pincode ✅
- Clicked_Label ✅
- Product_Name ✅
- Product_id ✅
- Mrp ✅
- Price ✅
- Weight ✅
- Shelf life ⚠️ Partial
- **Seller Name/Address ❌**
- **Manufacturer name and Address ❌**
- **Marketers name and address ❌**
- merchant_id ✅
- availability ✅
- **Number of alternative weights available ❌**
- **Number of alternative weights in stock ❌**
- Inventory ⚠️ Partial

### Current Implementation Status:
- ✅ Basic `scrape_availability` method exists
- ❌ NOT extracting all required fields
- ❌ Does NOT read from Excel file
- ❌ Does NOT handle multiple pincodes per product

---

## Summary of Gaps

### 1. Assortment - Minor Gaps
**Blinkit only:**
- Need to add `group_id` 
- Need to add `merchant_type`
- Verify `merchant_id` vs `store_id` naming

### 2. Availability - Major Gaps ⚠️
**All platforms need:**
- ❌ Excel file reading functionality
- ❌ Detailed product page scraping (seller/manufacturer/marketer info)
- ❌ Alternative weights detection
- ❌ Alternative weights stock status

---

## Recommended Action Plan

### Phase 1: Complete Assortment (Quick - 1 hour)
1. Add `group_id` to Blinkit
2. Add `merchant_type` to Blinkit
3. Standardize field names across all scrapers

### Phase 2: Implement Availability Scraping (4-6 hours)
1. Create Excel reader utility
2. Enhance `scrape_availability()` for each platform:
   - Extract seller/manufacturer/marketer information
   - Detect alternative weights
   - Get alternative weights stock status
3. Create availability scraping orchestrator
4. Output to Excel/CSV

---

## Questions for User

1. **Priority:** Should we complete assortment scraping first (2 small fields for Blinkit), or move to availability scraping?

2. **Availability Scope:** Do you have example Excel files with the expected format for product URLs and pincodes?

3. **Output Format:** For availability scraping, should output be Excel or CSV?

4. **Immediate Next Step:** 
   - Option A: Fix Zepto URL issue and regenerate CSVs with current 16 fields
   - Option B: Add the 2 missing Blinkit fields first
   - Option C: Start implementing full availability scraping

---

Generated: 2026-01-17 13:54
