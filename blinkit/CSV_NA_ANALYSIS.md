# CSV N/A Issues - Root Cause Analysis

## Summary
The N/A values in the CSV files are caused by different issues for each platform.

---

## Blinkit CSV - ETA showing N/A

### Status: ✅ **ETA Extraction Works, but inconsistent**

**Test Results:**
- Standalone test: Successfully extracted "19 minutes"
- CSV generation: Showed N/A

**Root Cause:**
The ETA extraction code exists and works (lines 73-88 in `blinkit.py`), but it may fail silently in some runs due to:
1. Timing issues (element not visible yet)
2. Page load variations
3. The regex pattern not matching the exact text format

**Current Extraction Code:**
```python
eta_el = await self.page.query_selector("div[class*='LocationBar__Title']")
if eta_el:
    text = await eta_el.inner_text()
    match = re.search(r'(\d+\s*minutes?|mins?)', text, re.IGNORECASE)
```

**Recommendation:**
- Add more robust waiting/retry logic
- Add fallback selectors
- Log warnings when ETA is not found

---

## Zepto CSV - Multiple N/A values + Wrong Products

### Status: ❌ **Critical Issues**

**Problems Found:**
1. **Scraping Wrong Category** - Getting detergents, hair care, pulses instead of vegetables
2. **All prices are 0.0**
3. **All weights are N/A**
4. **All ETAs are N/A**
5. **All image URLs are N/A**
6. **Store IDs are empty**

**Test Results:**
- Products scraped: "Top Load Detergent Powder", "Front Load Liquid Detergent", "Floor Cleaners", etc.
- All data fields showing 0.0 or N/A

**Root Causes:**

###  1. URL Issue
The URL in `generate_csvs.py` might be:
- Redirecting to a different category
- Invalid/outdated category ID
- Zepto changed their URL structure

Current URL:
```
https://www.zepto.com/cn/fruits-vegetables/fresh-vegetables/cid/64374cfe-d06f-4a01-898e-c07c46462c36/scid/b4827798-fcb6-4520-ba5b-0f2bd9bd7208
```

### 2. JSON Structure Changed
The JSON fields being extracted don't exist or have different names:
- `sellingPrice` → not found (returns 0)
- `mrp` → not found (returns 0)
- `weight` / `unitSize` → not found (returns N/A)
- `images` → not found or wrong structure (returns N/A)

### 3. ETA Not Visible
The selector `[data-testid="delivery-time"]` is not visible after location setting.

**Extracted JSON appears to be category/subcategory metadata, not actual products.**

---

## Recommended Fixes

### For Blinkit:
1. ✅ Code is good, just needs stability improvements
2. Add retry logic for ETA extraction
3. Consider multiple selector fallbacks

### For Zepto (Urgent):
1. **Find correct vegetables category URL**
   - Manually navigate to vegetables page
   - Copy the correct URL
2. **Debug JSON structure**
   - Examine actual JSON on the page
   - Update field names in the scraper
3. **Fix ETA selector or use alternative**
   - Find working ETA element after location is set
4. **Verify products are actual items, not categories**

---

## Next Steps
1. Get correct Zepto vegetables URL
2. Inspect Zepto page JSON to find correct field names
3. Update `generate_csvs.py` with correct URL
4. Re-run CSV generation

---

Generated: 2026-01-17
