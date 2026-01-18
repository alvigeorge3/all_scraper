
import asyncio
import time
import logging
from typing import List
from .base import BaseScraper
from .models import ProductItem, AvailabilityResult
from playwright.async_api import TimeoutError
import re

logger = logging.getLogger(__name__)

class ZeptoScraper(BaseScraper):
    def __init__(self, headless=False):
        super().__init__(headless)
        self.base_url = "https://www.zepto.com/"
        self.delivery_eta = "N/A"

    async def set_location(self, pincode: str):
        logger.info(f"Setting location to {pincode}")
        try:
            # Increase timeout for initial load
            await self.page.goto(self.base_url, timeout=60000, wait_until='domcontentloaded')
            
            # 1. Trigger Location Modal
            logger.info("Clicking location trigger...")
            try:
                # Use strict text match which is visible in screenshot
                # Force click in case it's covered or needs force
                # Use strict text match which is visible in screenshot
                await self.human_click("text=Select Location")
            except:
                logger.warning("Could not find 'text=Select Location', trying generic header location")
                # Fallback to looking for a header element that looks like a location selector
                await self.page.click("header [class*='location'], header button[aria-label*='location']", timeout=5000)

            # Wait for modal to open (smart wait)
            await self.page.wait_for_selector("input[placeholder='Search a new address']", state="visible", timeout=5000)

            # 2. Type Pincode
            logger.info("Typing pincode...")
            search_input_selector = "input[placeholder='Search a new address']"
            await self.page.wait_for_selector(search_input_selector, state="visible", timeout=10000)
            await self.page.click(search_input_selector)
            # Clear input just in case
            await self.page.fill(search_input_selector, "")
            await self.page.fill(search_input_selector, "")
            # Reduce type delay for speed -> Now human
            await self.human_type(search_input_selector, pincode)
            
            # 3. Wait for suggestions and select
            logger.info("Waiting for suggestions...")
            suggestion_selector = "div[data-testid='address-search-item']"
            try:
                await self.page.wait_for_selector(suggestion_selector, timeout=10000)
                
                suggestions = await self.page.query_selector_all(suggestion_selector)
                if suggestions:
                    logger.info(f"Found {len(suggestions)} suggestions, clicking first...")
                    await self.random_sleep(0.5, 1.0)
                    await suggestions[0].click()
                else:
                    logger.warning("No suggestions found with testid, looking for generic results")
                    await self.page.click("div[class*='prediction-container'] > div:first-child")
            except Exception as e:
                logger.error(f"Error selecting suggestion: {e}")
                # Try confirm button if it exists (sometimes flow differs)
                try: 
                    confirm_btn_selector = "button:has-text('Confirm')"
                    await self.page.wait_for_selector(confirm_btn_selector, timeout=2000)
                    await self.page.click(confirm_btn_selector)
                except: pass

            # Replace fixed wait with checking for location update in header or eta element
            try:
                # Wait for the location text to NOT be "Select Location" or similar, or wait for ETA
                # Simplest check: wait for ETA element which appears after location is set
                logger.info("Waiting for location update/ETA element...")
                await self.page.wait_for_selector('[data-testid="delivery-time"], header', timeout=10000)
                await self.page.wait_for_timeout(2000) # stabilizing wait
            except:
                logger.warning("Timeout waiting for location update indicators.")
            
            # 4. Extract ETA
            try:
                # Use robust testid selector found in analysis
                eta_selector = '[data-testid="delivery-time"]'
                eta_text = "N/A"
                
                try:
                    # Wait explicitly for visibility
                    await self.page.wait_for_selector(eta_selector, state='visible', timeout=5000)
                    eta_text = await self.page.inner_text(eta_selector)
                except:
                    logger.warning(f"ETA selector {eta_selector} not visible, trying generic header scan...")
                    # Fallback to header text scan
                    try:
                        header_element = await self.page.query_selector("header")
                        if header_element:
                            eta_text = await header_element.inner_text()
                    except: pass

                # Extract minutes from text
                match = re.search(r'(\d+\s*mins?)', eta_text, re.IGNORECASE)
                if match:
                    self.delivery_eta = match.group(1).lower()
                    logger.info(f"Captured Zepto ETA: {self.delivery_eta}")
                else:
                    logger.warning(f"Could not parse ETA from text: '{eta_text}'")
                    
            except Exception as e:
                logger.warning(f"Could not capture Zepto ETA: {e}")

            logger.info("Location set successfully")
            
        except Exception as e:
            logger.error(f"Error setting location: {e}")
            try:
                await self.page.screenshot(path="error_screenshot_location_zepto.png")
            except:
                pass

    async def scrape_assortment(self, category_url: str, pincode: str = "N/A") -> List[ProductItem]:
        logger.info(f"Scraping assortment from {category_url}")
        results: List[ProductItem] = []
        # Smart Navigation & 404 Handling
        try:
            # Check for 404 or if we are just on homepage (failed deep link)
            content = await self.page.content()
            is_404 = "made an egg-sit" in content or "page you’re looking for" in content
            
            # Normalize URLs for comparison
            current_url = self.page.url.rstrip('/')
            base_url_clean = self.base_url.rstrip('/')
            
            # If 404 or if we requested a deep link but are at base_url (redirected)
            is_redirected_home = (current_url == base_url_clean) and (category_url.rstrip('/') != base_url_clean)

            if is_404 or is_redirected_home:
                logger.warning(f"Direct link failed (404: {is_404}, Redirect: {is_redirected_home}). Attempting Smart Navigation Fallback...")
                
                # Derive keyword from URL, e.g. "fruits-vegetables"
                parts = [p for p in category_url.split('/') if len(p) > 3 and '-' in p and 'zepto' not in p]
                keyword = parts[0] if parts else "fruits"
                logger.info(f"Looking for category link matching '{keyword}'...")

                try:
                    # tailored selector for zepto nav/icons
                    link_selector = f"a[href*='{keyword}']"
                    await self.page.click(link_selector, timeout=5000)
                    await self.page.wait_for_timeout(3000) # Wait for nav
                    logger.info(f"Navigated to {self.page.url}")
                except Exception as e:
                    logger.error(f"Smart Navigation failed: {e}")
                    return []
        except Exception as e:
             logger.warning(f"Error in smart navigation check: {e}")

        # Continue with scraping (now presumably on the right page)
        
        try:
            # 1. Network Interception Strategy
            logger.info("Setting up Network Interception...")
            json_products_map = {}
            
            async def handle_response(response):
                try:
                    if "application/json" in response.headers.get("content-type", ""):
                        # Filter relevant APIs (exclude analytics, etc.)
                        url = response.url
                        if "google" in url or "segment" in url:
                            return
                            
                        try:
                            data = await response.json()
                            logger.info(f"Captured JSON from {url}")
                            
                            # Recursive search in API response
                            def extract_products(obj):
                                if isinstance(obj, dict):
                                    if obj.get('id') and obj.get('name') and (obj.get('mrp') or obj.get('sellingPrice') or obj.get('discountedSellingPrice')):
                                        json_products_map[obj.get('name')] = obj
                                    
                                    for key, value in obj.items():
                                        extract_products(value)
                                elif isinstance(obj, list):
                                    for item in obj:
                                        extract_products(item)

                            extract_products(data)
                        except:
                            pass
                except:
                    pass

            self.page.on("response", handle_response)

            # Reload/Navigate to trigger requests
            # If we are already on the page (from smart nav), we might need to reload or scroll
            # But smart nav happens BEFORE this block usually.
            # Ideally we should attach listener BEFORE navigation.
            # In current flow: set_location -> scrape_assortment (navigates).
            
            # Since we used Smart Navigation inside scrape_assortment *before* this block?
            # No, Smart Nav is at top of function.
            # We need to RELOAD or Scroll to capture data if we missed the initial load.
            
            logger.info("Reloading page to capture network traffic...")
            await self.page.reload(wait_until='networkidle')
            await self.smooth_scroll()
            await self.random_sleep(2.0, 4.0)
            
            self.page.remove_listener("response", handle_response)
            
            logger.info(f"Extracted {len(json_products_map)} unique rich products from Network")
            

            
            # DEBUG: Print first RICH item and save to file
            if len(json_products_map) > 0:
                first_key = list(json_products_map.keys())[0]
                first_item = json_products_map[first_key]
                logger.info(f"DEBUG RICH JSON for '{first_key}': {first_item}")
                try:
                    import json
                    with open('debug_product_dump.json', 'w') as f:
                        json.dump(first_item, f, indent=2)
                    logger.info("Saved first product JSON to debug_product_dump.json")
                except Exception as e:
                    logger.error(f"Failed to dump debug JSON: {e}")

            # 2. Fallback to Regex (keep as backup)
            if not json_products_map:
                try:
                    import json
                    start_pattern = re.compile(r'\{"id":"[a-f0-9\-]{36}"')
                    normalized_content = content.replace(r'\"', '"').replace(r'\\', '\\')
                    decoder = json.JSONDecoder()
                    
                    for match in start_pattern.finditer(normalized_content):
                        try:
                            p_data, _ = decoder.raw_decode(normalized_content, match.start())
                            if isinstance(p_data, dict) and p_data.get('id') and p_data.get('name'):
                                if p_data.get('mrp') or p_data.get('sellingPrice'):
                                    json_products_map[p_data.get('name')] = p_data
                        except: continue
                except Exception as re_e:
                    logger.warning(f"Regex fallback failed: {re_e}")

            logger.info(f"Total unique products found: {len(json_products_map)}")

            # Extract category and subcategory from URL
            # URL format: https://www.zepto.com/cn/fresh-vegetables/fresh-vegetables/cid/.../scid/...
            category = "N/A"
            subcategory = "N/A"
            try:
                parts = category_url.split('/cn/')
                if len(parts) > 1:
                    path_parts = parts[1].split('/cid/')[0].split('/')
                    if len(path_parts) >= 1:
                        category = path_parts[0].replace('-', ' ').title()
                    if len(path_parts) >= 2:
                        subcategory = path_parts[1].replace('-', ' ').title()
            except:
                pass
            
            clicked_label = f"{category} > {subcategory}" if subcategory != "N/A" else category

            # Generate Results
            logger.info("Generating results from extracted JSON data...")
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

            for name, p in json_products_map.items():
                try:
                    # SANITY CHECK for Vegetables Category
                    if "vegetable" in category.lower() or "fruit" in category.lower():
                        bad_keywords = ["detergent", "liquid", "powder", "cleaner", "soap", "wash", "shampoo", "harpic", "surf", "ariel"]
                        if any(k in name.lower() for k in bad_keywords):
                            continue

                    price_val = float(p.get('sellingPrice', 0) or p.get('discountedSellingPrice', 0)) / 100
                    mrp_val = float(p.get('mrp', 0)) / 100
                    store_id = p.get('storeId')
                    pid = p.get('id')
                    
                    # Extract inventory if available
                    inventory = None
                    if 'inventory' in p or 'available_quantity' in p or 'availableQuantity' in p:
                        try:
                            inventory = int(p.get('inventory') or p.get('available_quantity') or p.get('availableQuantity') or 0)
                            if inventory == 0:
                                inventory = None
                        except:
                            pass
                    
                    # Extract shelf life if available
                    shelf_life = None
                    # Search for shelf life in attributes if not at top level
                    if 'shelf_life' in p or 'shelfLife' in p:
                         shelf_life = p.get('shelfLife') or p.get('shelf_life')
                    elif 'attributes' in p and isinstance(p['attributes'], list):
                        for attr in p['attributes']:
                            if 'shelf' in str(attr.get('name', '')).lower():
                                shelf_life = attr.get('value')
                                break

                    # Convert shelf life to hours/int if possible, else keep string or try parsing
                    # User asked for "shelf_life_in_hours". Often it's "3 days".
                    # Let's just store what we get for now or try simple conversion
                    shelf_life_val = None
                    if shelf_life:
                         try:
                             # Simple heuristic: if 'days', * 24
                             sl_str = str(shelf_life).lower()
                             if 'day' in sl_str:
                                 days = int(re.search(r'\d+', sl_str).group())
                                 shelf_life_val = days * 24
                             elif 'hour' in sl_str:
                                 shelf_life_val = int(re.search(r'\d+', sl_str).group())
                         except: pass

                    
                    # Image URL construction
                    image_url = "N/A"
                    if p.get('images') and isinstance(p['images'], list) and len(p['images']) > 0:
                            image_url = p['images'][0].get('path', 'N/A')
                            if image_url != "N/A" and not image_url.startswith('http'):
                                image_url = f"https://cdn.zepto.com/production/{image_url}"

                    item: ProductItem = {
                        "platform": "zepto",
                        "category": category,
                        "subcategory": subcategory,
                        "clicked_label": clicked_label,
                        "name": name,
                        "brand": p.get("brand") or p.get("brandName") or "Unknown",
                        "base_product_id": pid,
                        "group_id": None,  # Blinkit-specific
                        "merchant_type": None,  # Blinkit-specific
                        "mrp": mrp_val,
                        "price": price_val,
                        "weight": p.get('weight') or p.get('unitSize') or "N/A",
                        "shelf_life_in_hours": shelf_life_val,
                        "eta": self.delivery_eta,
                        "availability": "Out of Stock" if p.get("isSoldOut") else "In Stock",
                        "inventory": inventory,
                        "store_id": store_id,
                        "image_url": image_url,
                        "product_url": f"{self.base_url}pn/{name.lower().replace(' ', '-')}/pvid/{pid}",
                        "scraped_at": timestamp,
                        "pincode_input": pincode
                    }
                    results.append(item)
                except Exception as j_e:
                    logger.warning(f"Error parsing JSON product {name}: {j_e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error in extraction strategy: {e}")
    
        return results

    async def scrape_availability(self, product_url: str) -> AvailabilityResult:
        logger.info(f"Checking availability for {product_url}")
        
        result: AvailabilityResult = {
            "input_pincode": "", 
            "url": product_url,
            "platform": "zepto",
            "name": "N/A",
            "price": 0.0,
            "mrp": 0.0,
            "availability": "Unknown",
            "seller_details": None,
            "manufacturer_details": None,
            "marketer_details": None,
            "variant_count": 1,
            "variant_in_stock_count": 1,
            "inventory": None,
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "error": None
        }
        
        try:
            await self.page.goto(product_url, timeout=60000, wait_until='domcontentloaded')
            await self.page.wait_for_timeout(2000)

            await self.page.wait_for_timeout(2000)
            
            await self.smooth_scroll()

            content = await self.page.content()
            
            if "page you’re looking for" in content:
                result["availability"] = "Not Found" 
                result["error"] = "404 Not Found"
                return result

            # 1. JSON Extraction
            import json
            import re
            
            extracted_json = None
            try:
                # Zepto hydration data pattern
                start_pattern = re.compile(r'\{"id":"[a-f0-9\-]{36}"')
                normalized_content = content.replace(r'\"', '"').replace(r'\\', '\\')
                decoder = json.JSONDecoder()
                candidates = []
                
                for match in start_pattern.finditer(normalized_content):
                    try:
                        p_data, _ = decoder.raw_decode(normalized_content, match.start())
                        if isinstance(p_data, dict) and p_data.get('id') and p_data.get('name'):
                            candidates.append(p_data)
                    except: continue
                        
                # Check URL for ID
                url_id_match = re.search(r'pvid/([a-f0-9\-]{36})', product_url)
                if url_id_match:
                    target_id = url_id_match.group(1)
                    extracted_json = next((c for c in candidates if c.get('id') == target_id), None)
                
                if not extracted_json and candidates:
                     candidates.sort(key=lambda x: len(str(x)), reverse=True)
                     extracted_json = candidates[0]

                if extracted_json:
                    result["name"] = extracted_json.get("name", "N/A")
                    sp = extracted_json.get("sellingPrice")
                    if sp: result["price"] = float(sp) / 100
                    mp = extracted_json.get("mrp")
                    if mp: result["mrp"] = float(mp) / 100
                    
                    if extracted_json.get("isSoldOut"):
                        result["availability"] = "Out of Stock"
                        result["variant_in_stock_count"] = 0
                    else:
                        result["availability"] = "In Stock"
                        
                    # Detailed Metadata from JSON
                    result["manufacturer_details"] = extracted_json.get("manufacturerName") or extracted_json.get("manufacturerAddress")
                    result["marketer_details"] = extracted_json.get("importedBy")
                    result["seller_details"] = extracted_json.get("sellerName") or "Zepto" # Default if not found
                    
                    # Variants often in 'variants' list or 'productVariants'
                    if extracted_json.get("productVariants"):
                        result["variant_count"] = len(extracted_json.get("productVariants"))
                        result["variant_in_stock_count"] = sum(1 for v in extracted_json.get("productVariants", []) if not v.get("isSoldOut"))

            except Exception as e:
                logger.warning(f"JSON extraction failed in availability: {e}")

            # 2. DOM Fallback
            if result["name"] == "N/A":
                try:
                    el = await self.page.query_selector("h1")
                    if el: result["name"] = await el.inner_text()
                except: pass

            # DOM Metadata Extraction (if JSON failed)
            text_content = await self.page.inner_text("body")
            
            def extract_line_after(keyword):
                try:
                    match = re.search(f"{keyword}\\n(.*?)\\n", text_content, re.IGNORECASE)
                    if match: return match.group(1).strip()
                except: pass
                return None

            if not result["manufacturer_details"]:
                result["manufacturer_details"] = extract_line_after("Manufacturer Details")
            if not result["marketer_details"]:
                result["marketer_details"] = extract_line_after("Marketed By")

            # 3. Variants via DOM
            # Look for weight buttons/chips
            try:
                variant_chips = await self.page.query_selector_all("[data-testid='product-variant-chip']")
                if variant_chips:
                    result["variant_count"] = len(variant_chips)
                    # Difficult to check stock of other variants without clicking
                    # Assumption: count visible chips
            except: pass

        except Exception as e:
            logger.error(f"Error checking availability: {e}")
            result["error"] = str(e)
            result["availability"] = "Error"
            
        return result


