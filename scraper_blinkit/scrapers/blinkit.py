
import asyncio
import logging
import json
import re
import time
from typing import List
from .base import BaseScraper
from .models import ProductItem, AvailabilityResult
from playwright.async_api import TimeoutError

logger = logging.getLogger(__name__)

class BlinkitScraper(BaseScraper):
    def __init__(self, headless=False):
        super().__init__(headless)
        self.base_url = "https://blinkit.com/"
        self.delivery_eta = "N/A"

    async def start(self):
        await super().start()
        # Resource blocking for performance
        await self.page.route("**/*", self._handle_route)

    async def _handle_route(self, route):
        if route.request.resource_type in ["image", "media", "font"]:
            await route.abort()
        else:
            await route.continue_()

    async def set_location(self, pincode: str):
        logger.info(f"Setting location to {pincode}")
        try:
            await self.page.goto(self.base_url, timeout=60000, wait_until='domcontentloaded')
            
            # Humanize: Scroll a bit to look real
            await self.human_scroll()

            # 1. Trigger Location Modal
            logger.info("Clicking location trigger...")
            try:
                # Random delay before clicking
                await self.human_delay()
                
                trigger_selector = "div[class*='LocationBar__']"
                try:
                    await self.page.wait_for_selector(trigger_selector, timeout=5000)
                except: pass

                if await self.page.is_visible("div[class*='LocationBar__']"):
                    try:
                        await self.page.hover("div[class*='LocationBar__']") 
                        await self.human_delay(0.2, 0.5)
                        # Force click to bypass transparent overlays
                        await self.page.click("div[class*='LocationBar__']", force=True) 
                    except:
                        # If hover fails, try JS click
                        await self.page.evaluate("document.querySelector(\"div[class*='LocationBar__']\").click()")

                elif await self.page.is_visible("text=Delivery in"):
                    await self.page.click("text=Delivery in", force=True)
                else:
                    await self.page.click("header div[class*='Container']", force=True)
            except Exception as e:
                logger.warning(f"Trigger click failed: {e}")

            # Wait for modal with smart wait
            modal_input = "input[name='search'], input[placeholder*='search']"
            await self.page.wait_for_selector(modal_input, state="visible", timeout=15000)
            
            # 2. Type pincode naturally
            logger.info(f"Typing pincode: {pincode}")
            try:
                # Clear existing text first
                await self.page.click(modal_input)
                await self.page.keyboard.press("Control+A")
                await self.page.keyboard.press("Backspace")
                
                await self.human_type(modal_input, pincode)
                
                # 3. Wait for and click result
                logger.info("Waiting for suggestions...")
                # Improved selector: Just look for the pincode text anywhere in the list
                suggestion_selector = f"div[class*='LocationSearchList'] div:has-text('{pincode}')"
                try:
                    await self.page.wait_for_selector(suggestion_selector, timeout=8000)
                    await self.page.click(suggestion_selector, force=True)
                except:
                     # Fallback: click the first suggestion if specific pincode match fails
                     logger.warning("Specific pincode match failed, clicking first suggestion...")
                     await self.page.click("div[class*='LocationSearchList'] > div:nth-child(1)", force=True)
                
                await self.page.wait_for_selector(modal_input, state="hidden", timeout=5000)
                await self.page.wait_for_timeout(2000)
            except Exception as e:
                logger.warning(f"Location input interaction failed: {e}")
            
            # 4. Extract Delivery ETA
            try:
                eta_el = await self.page.query_selector("div[class*='LocationBar__Title']")
                if eta_el:
                    text = await eta_el.inner_text()
                    logger.info(f"Raw ETA Text: '{text}'")
                    match = re.search(r'(\d+\s*minutes?|mins?)', text, re.IGNORECASE)
                    if match:
                        self.delivery_eta = match.group(1).lower()
                        logger.info(f"Captured Delivery ETA: {self.delivery_eta}")
                    else:
                        logger.warning(f"ETA regex mismatch. Keeping: {self.delivery_eta}")
                else:
                    logger.warning("ETA Element not found")
            except Exception as e:
                logger.warning(f"Could not extract ETA: {e}")
                
            logger.info("Location set successfully")
            
        except Exception as e:
            logger.error(f"Error setting location: {e}")
            try:
                await self.page.screenshot(path="error_blinkit_location.png")
            except: pass

    async def get_all_categories(self) -> List[str]:
        """
        Navigates to the homepage and extracts all category URLs.
        """
        logger.info("Extracting all categories from homepage...")
        categories = set()
        try:
            if self.page.url != self.base_url:
                await self.page.goto(self.base_url, timeout=60000, wait_until='domcontentloaded')
                await self.page.wait_for_timeout(3000)

            # Extract all links containing '/cn/'
            links = await self.page.evaluate('''() => {
                return Array.from(document.querySelectorAll('a'))
                    .map(a => a.href)
                    .filter(href => href.includes('/cn/'));
            }''')
            
            for link in links:
                categories.add(link)
                
            logger.info(f"Found {len(categories)} unique category links.")
            return list(categories)
        except Exception as e:
            logger.error(f"Error extracting categories: {e}")
            return []

    async def scrape_assortment(self, category_url: str, pincode: str = "N/A") -> List[ProductItem]:
        logger.info(f"Scraping assortment from {category_url}")
        results: List[ProductItem] = []
        
        # Extract category and subcategory from URL
        # URL format: https://blinkit.com/cn/vegetables-fruits/vegetables/cid/1487/1489
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
        
        try:
            await self.page.goto(category_url, timeout=60000, wait_until="domcontentloaded")
            if self.page.url == self.base_url and "cid" in category_url:
                 logger.warning(f"Redirected to homepage. Category URL {category_url} might be invalid.")
                 return []

            await self.page.wait_for_timeout(3000)

            products_map = {}
            # 1. JSON Data Extraction Strategy (Primary)
            try:
                # Try to get data directly from Next.js hydration state
                next_data = await self.page.evaluate("window.__NEXT_DATA__")
                if next_data:
                    # Traverse the JSON to find products
                    # Usually in props > pageProps > initialAppShellPrefetch > ... or similar
                    # But simpler to just traverse recursively or JSON dump and regex search the clean object
                    
                    # Strategy: Serialize back to string and use multiple regex patterns or just recursive search
                    # Efficient recursive search for dicts with 'product_id'
                    
                    def find_products_recursive(data, collector):
                        if isinstance(data, dict):
                            if 'product_id' in data and ('name' in data or 'product_name' in data):
                                pid = str(data['product_id'])
                                if pid not in collector:
                                    collector[pid] = data
                            for k, v in data.items():
                                find_products_recursive(v, collector)
                        elif isinstance(data, list):
                            for item in data:
                                find_products_recursive(item, collector)
                                
                    find_products_recursive(next_data, products_map)
            except Exception as e:
                logger.warning(f"NEXT_DATA extraction failed: {e}")

            # Fallback to Regex if NEXT_DATA didn't yield results
            if not products_map:
                content = await self.page.content()
                start_pattern = re.compile(r'\{"product_id"\s*:\s*"?\d+')
                decoder = json.JSONDecoder()
                
                for match in start_pattern.finditer(content):
                    try:
                        prod_obj, _ = decoder.raw_decode(content, match.start())
                        if isinstance(prod_obj, dict):
                            pid = str(prod_obj.get('product_id') or prod_obj.get('id'))
                            if pid and pid not in products_map:
                                products_map[pid] = prod_obj
                    except:
                        continue

            logger.info(f"Extracted {len(products_map)} unique products (Method: {'NEXT_DATA' if products_map else 'Regex/None'})")
            
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            
            for pid, p in products_map.items():
                try:
                    name = p.get('product_name') or p.get('display_name') or "Unknown"
                    is_unavailable = p.get('unavailable_quantity') == 1 or p.get('inventory') == 0
                    
                    # Extract inventory/quantity if available
                    inventory = None
                    if 'inventory' in p and p['inventory'] is not None:
                        try:
                            inventory = int(p['inventory'])
                        except:
                            pass
                    
                    # Extract shelf life if available
                    shelf_life = None
                    if 'shelf_life' in p or 'shelf_life_hours' in p:
                        try:
                            shelf_life = int(p.get('shelf_life_hours') or p.get('shelf_life') or 0)
                            if shelf_life == 0:
                                shelf_life = None
                        except:
                            pass
                    
                    item: ProductItem = {
                        "platform": "blinkit",
                        "category": category,
                        "subcategory": subcategory,
                        "clicked_label": clicked_label,
                        "name": name,
                        "brand": p.get('brand') or "Unknown",
                        "base_product_id": pid,
                        "product_id": pid, # Explicitly requested
                        "group_id": p.get('group_id') or p.get('groupId'),
                        "merchant_type": p.get('merchant_type') or p.get('merchantType'),
                        "mrp": float(p.get('mrp', 0)),
                        "price": float(p.get('price', 0)),
                        "weight": p.get('unit') or p.get('quantity_info') or "N/A",
                        "shelf_life_in_hours": shelf_life,
                        "eta": self.delivery_eta, 
                        "availability": "Out of Stock" if is_unavailable else "In Stock",
                        "inventory": inventory,
                        "store_id": str(p.get('merchant_id') or "Unknown"),
                        "product_url": f"{self.base_url}prn/{name.lower().replace(' ', '-')}/prid/{pid}",
                        "image_url": p.get('image_url') or "N/A",
                        "scraped_at": timestamp,
                        "pincode_input": pincode
                    }
                    results.append(item)
                except Exception as e:
                    logger.warning(f"Skipping product {pid}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error scraping assortment: {e}")
            await self.page.screenshot(path="error_blinkit_assortment.png")
            
        return results

    async def scrape_availability(self, product_url: str) -> AvailabilityResult:
        logger.info(f"Scraping availability from {product_url}")
        
        result: AvailabilityResult = {
             "input_pincode": "",
             "url": product_url,
             "platform": "blinkit",
             "name": "N/A",
             "price": 0.0,
             "mrp": 0.0,
             "availability": "Unknown",
             "seller_details": None,
             "manufacturer_details": None,
             "marketer_details": None,
             "variant_count": None,
             "variant_in_stock_count": None,
             "inventory": None,
             "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
             "error": None
        }
        
        try:
            await self.page.goto(product_url, timeout=60000, wait_until="domcontentloaded")
            await self.page.wait_for_timeout(2000) # Stabilize
            
            # 1. Expand "Product Details" if necessary
            try:
                # Look for "See all details" or similar buttons
                see_more_btns = await self.page.query_selector_all("text='See all details'")
                for btn in see_more_btns:
                    if await btn.is_visible():
                        await btn.click()
                        await self.page.wait_for_timeout(1000)
            except: pass

            content = await self.page.content()
            
            # 2. JSON Strategy for Core Data
            normalized_content = content.replace(r'\"', '"').replace(r'\\', '\\')
            start_pattern = re.compile(r'\{"product_id":')
            decoder = json.JSONDecoder()
            
            target_data = None
            url_id_match = re.search(r'prid/(\d+)', product_url)
            
            if url_id_match:
                target_id = url_id_match.group(1)
                for match in start_pattern.finditer(normalized_content):
                    try:
                        p_data, _ = decoder.raw_decode(normalized_content, match.start())
                        if isinstance(p_data, dict) and str(p_data.get('product_id')) == target_id:
                            target_data = p_data
                            break
                    except: continue
            
            # Fill Core Data from JSON
            if target_data:
                result["name"] = target_data.get('name') or target_data.get('product_name') or target_data.get('display_name') or 'N/A'
                result["price"] = float(target_data.get('price', 0))
                result["mrp"] = float(target_data.get('mrp', 0))
                
                # Inventory
                inv = 0
                if 'inventory' in target_data:
                     inv = int(target_data.get('inventory') or 0)
                result["inventory"] = inv
                result["availability"] = "In Stock" if inv > 0 else "Out of Stock"
            else:
                # Fallback DOM for Core Data
                try:
                    name_el = await self.page.query_selector('h1')
                    if name_el: result["name"] = await name_el.inner_text()
                    # Add price element checks here if needed
                except: pass

            # 3. Extract Detailed Metadata (DOM Strategy)
            # Use specific text parsing for Manufacturer, Marketed By, etc.
            text_content = await self.page.inner_text("body")
            
            def extract_section(keyword):
                try:
                    # Logic: find text line with Keyword, extract following lines
                    match = re.search(f"{keyword}\\n(.*?)(?:\\n\\n|\\Z)", text_content, re.IGNORECASE | re.DOTALL)
                    if match:
                        return match.group(1).strip()
                except: pass
                return None

            result["manufacturer_details"] = extract_section("Manufacturer Details")
            result["marketer_details"] = extract_section("Marketed By")
            result["seller_details"] = extract_section("Seller Details") or extract_section("Sold By")  # Blinkit often uses "Sold By"

            # 4. Variant Analysis
            # Look for logic that indicates variants (e.g. weight buttons)
            # This is complex on single product page, often requires looking at "Pack Sizes" section
            try:
                # Common selector for variants
                variants = await self.page.query_selector_all("div[class*='PackSizeSelector']") 
                # Or just general buttons with weights
                if not variants:
                    # Fallback logic: check for "Select Unit" or similar
                    pass
                
                # If we assume the current product is one variant that is loaded
                # We can look for siblings in the JSON or DOM
                # For now, simplistic approach: "1" if no explicit selector found
                result["variant_count"] = 1
                result["variant_in_stock_count"] = 1 if result["availability"] == "In Stock" else 0
                
            except:
                pass
                
        except Exception as e:
            logger.error(f"Error scraping availability for {product_url}: {e}")
            result["error"] = str(e)
            
        return result

