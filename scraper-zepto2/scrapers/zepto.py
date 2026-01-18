
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

class ZeptoScraper(BaseScraper):
    def __init__(self, headless=False):
        super().__init__(headless)
        self.base_url = "https://www.zepto.com/"
        self.delivery_eta = "N/A"
        # Store captured products from network intercepts
        self.captured_products = {}

    async def start(self):
        await super().start()
        # Set up network interception to capture product data from API responses
        await self.page.route("**/*", self._handle_route)
        # Listen for API responses
        self.page.on("response", self._capture_api_response)

    async def _handle_route(self, route):
        # Don't block images for now - Zepto might need them to render
        if route.request.resource_type in ["font", "media"]:
            await route.abort()
        else:
            await route.continue_()

    async def _capture_api_response(self, response):
        """Capture product data from API responses."""
        try:
            url = response.url
            # Look for API endpoints that might contain product data
            if any(x in url for x in ['widget', 'products', 'catalog', 'inventory', 'layout']):
                if response.status == 200:
                    try:
                        data = await response.json()
                        self._extract_products_from_response(data)
                    except:
                        pass
        except:
            pass
    
    def _extract_products_from_response(self, data):
        """Extract products from API response data."""
        if isinstance(data, dict):
            # Look for product arrays
            for key in ['products', 'items', 'widgets', 'data', 'productVariants']:
                if key in data and isinstance(data[key], list):
                    for item in data[key]:
                        self._try_add_product(item)
            
            # Recurse into nested structures
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    self._extract_products_from_response(value)
                    
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    self._try_add_product(item)
                    self._extract_products_from_response(item)
    
    def _try_add_product(self, item):
        """Try to add an item as a product if it has required fields."""
        if not isinstance(item, dict):
            return
            
        # Check for product variant ID (Zepto uses productVariantId)
        pvid = item.get('productVariantId') or item.get('id') or item.get('productId')
        name = item.get('name') or item.get('productName')
        
        # Need at least an ID and name
        if pvid and name:
            # Check for pricing fields
            price = item.get('sellingPrice') or item.get('price') or item.get('discountedPrice')
            mrp = item.get('mrp') or item.get('maxRetailPrice')
            
            if price or mrp:
                self.captured_products[str(pvid)] = item

    async def set_location(self, pincode: str):
        logger.info(f"Setting location to {pincode}")
        try:
            # Navigate to homepage
            await self.page.goto(self.base_url, timeout=60000, wait_until='domcontentloaded')
            await asyncio.sleep(2)
            
            # Humanize: Scroll a bit
            await self.human_scroll()
            await self.human_delay()

            # Look for location button/trigger
            logger.info("Looking for location trigger...")
            
            # Zepto's common location trigger patterns
            location_clicked = False
            
            # Try clicking the search/location area at top
            location_triggers = [
                "button:has-text('Delivery in')",
                "div:has-text('Delivery in')",
                "text='Delivery in'",
                "[data-testid*='location']",
                "[data-testid*='address']",
                "button:has-text('Enter')",
                "text='Enter your delivery location'",
                "text='Select your location'",
            ]
            
            for trigger in location_triggers:
                try:
                    elem = await self.page.wait_for_selector(trigger, timeout=3000, state='visible')
                    if elem:
                        await elem.click()
                        location_clicked = True
                        logger.info(f"Clicked location trigger: {trigger}")
                        await asyncio.sleep(1)
                        break
                except:
                    continue
            
            if not location_clicked:
                logger.warning("No location trigger found, looking for input directly")
            
            # Now look for pincode input
            await asyncio.sleep(1)
            
            input_selectors = [
                "input[placeholder*='pincode' i]",
                "input[placeholder*='Pincode' i]",
                "input[placeholder*='location' i]",
                "input[placeholder*='area' i]",
                "input[placeholder*='address' i]",
                "input[placeholder*='Search' i]",
                "input[type='text']",
                "input[type='search']",
            ]
            
            input_elem = None
            for selector in input_selectors:
                try:
                    input_elem = await self.page.wait_for_selector(selector, timeout=3000, state='visible')
                    if input_elem:
                        logger.info(f"Found input: {selector}")
                        break
                except:
                    continue
            
            if input_elem:
                # Clear and type pincode
                await input_elem.click()
                await self.page.keyboard.press("Control+A")
                await self.page.keyboard.press("Backspace")
                
                # Type pincode with human-like speed
                for char in pincode:
                    await self.page.keyboard.type(char)
                    await asyncio.sleep(0.1)
                    
                logger.info(f"Typed pincode: {pincode}")
                await asyncio.sleep(2)
                
                # Try to click a suggestion
                suggestion_clicked = False
                suggestion_selectors = [
                    f"div:has-text('{pincode}'):not(input)",
                    f"li:has-text('{pincode}')",
                    f"button:has-text('{pincode}')",
                    "[role='option']",
                    "[data-testid*='suggestion']",
                    "div[class*='suggestion']",
                    "div[class*='result']",
                ]
                
                for selector in suggestion_selectors:
                    try:
                        elem = await self.page.wait_for_selector(selector, timeout=2000, state='visible')
                        if elem:
                            text = await elem.inner_text()
                            if pincode in text or len(text) < 200:  # Avoid clicking huge containers
                                await elem.click()
                                suggestion_clicked = True
                                logger.info(f"Clicked suggestion: {selector}")
                                break
                    except:
                        continue
                
                if not suggestion_clicked:
                    logger.info("No suggestion clicked, pressing Enter")
                    await self.page.keyboard.press("Enter")
                    
                await asyncio.sleep(3)
            else:
                logger.warning("Could not find pincode input")
            
            # Try to extract ETA
            try:
                page_text = await self.page.inner_text("body")
                eta_match = re.search(r'(\d+)\s*(min|mins|minutes)', page_text, re.IGNORECASE)
                if eta_match:
                    self.delivery_eta = f"{eta_match.group(1)} mins"
                    logger.info(f"Captured ETA: {self.delivery_eta}")
            except:
                pass
                
            logger.info(f"Location setting complete for {pincode}")
            
        except Exception as e:
            logger.error(f"Error setting location: {e}")
            try:
                await self.page.screenshot(path="error_zepto_location.png")
            except:
                pass

    async def get_all_categories(self) -> List[str]:
        """Extract all category URLs from the homepage."""
        logger.info("Extracting all categories from homepage...")
        categories = set()
        
        try:
            # Make sure we're on homepage
            current_url = self.page.url
            if not current_url.startswith(self.base_url):
                await self.page.goto(self.base_url, timeout=60000, wait_until='domcontentloaded')
                await asyncio.sleep(2)
            
            # Scroll to load all categories
            for _ in range(3):
                await self.human_scroll()
                await asyncio.sleep(0.5)

            # Zepto uses /cn/ for category URLs with /cid/ and /scid/ params
            links = await self.page.evaluate('''() => {
                return Array.from(document.querySelectorAll('a'))
                    .map(a => a.href)
                    .filter(href => href.includes('/cn/') && href.includes('/cid/'));
            }''')
            
            for link in links:
                # Filter out cart/account pages
                if not any(x in link.lower() for x in ['cart', 'account', 'orders', 'profile', 'login']):
                    categories.add(link)
                
            logger.info(f"Found {len(categories)} unique category links.")
            
            # If no categories found, provide some default ones
            if len(categories) == 0:
                logger.warning("No categories found dynamically, using hardcoded list")
                default_categories = [
                    "https://www.zepto.com/cn/fruits-vegetables/fresh-fruits/cid/64374cfe-d06f-4a01-898e-c07c46462c36/scid/09e63c15-e5f7-4712-9ff8-513250b79942",
                    "https://www.zepto.com/cn/dairy-bread-eggs/top-picks/cid/4b938e02-7bde-4479-bc0a-2b54cb6bd5f5/scid/b26b6bcf-7c81-48e7-a9bc-fec3825bad2a",
                    "https://www.zepto.com/cn/munchies/top-picks/cid/d2c2a144-43cd-43e5-b308-92628fa68596/scid/d648ea7c-18f0-4178-a202-4751811b086b",
                    "https://www.zepto.com/cn/cold-drinks-juices/top-picks/cid/947a72ae-b371-45cb-ad3a-778c05b64399/scid/7dceec53-78f9-4f06-83d7-c8edd9c2f71a",
                    "https://www.zepto.com/cn/atta-rice-oil-dals/top-picks/cid/2f7190d0-7c40-458b-b450-9a1006db3d95/scid/84f270cf-ae95-4d61-a556-b35b563fb947",
                ]
                return default_categories
            
            return list(categories)
            
        except Exception as e:
            logger.error(f"Error extracting categories: {e}")
            return []

    async def scrape_assortment(self, category_url: str, pincode: str = "N/A") -> List[ProductItem]:
        logger.info(f"Scraping assortment from {category_url}")
        results: List[ProductItem] = []
        
        # Clear captured products before navigating
        self.captured_products = {}
        
        # Extract category and subcategory from URL
        # URL format: /cn/category-name/subcategory-name/cid/xxx/scid/xxx
        category = "N/A"
        subcategory = "N/A"
        try:
            if '/cn/' in category_url:
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
            await asyncio.sleep(3)
            
            # Check if redirected to homepage
            if 'cn/' not in self.page.url and category_url != self.base_url:
                logger.warning(f"Redirected away from category. URL might be invalid: {category_url}")
                return []
            
            # Scroll to trigger lazy loading and API calls
            logger.info("Scrolling to load products...")
            for i in range(5):
                await self.page.mouse.wheel(0, 800)
                await asyncio.sleep(1)
            
            # Wait for potential API responses to be captured
            await asyncio.sleep(2)
            
            products_map = {}
            
            # 1. Try captured API responses first
            if self.captured_products:
                logger.info(f"Found {len(self.captured_products)} products from API interception")
                products_map = self.captured_products.copy()
            
            # 2. Try __NEXT_DATA__ if API interception didn't work
            if not products_map:
                try:
                    next_data = await self.page.evaluate("window.__NEXT_DATA__")
                    if next_data:
                        logger.info("Extracting from __NEXT_DATA__...")
                        self._find_products_in_json(next_data, products_map)
                        logger.info(f"Found {len(products_map)} products from __NEXT_DATA__")
                except Exception as e:
                    logger.warning(f"__NEXT_DATA__ extraction failed: {e}")
            
            # 3. Fallback: Parse product cards from DOM
            if not products_map:
                logger.info("Trying DOM-based extraction...")
                products_map = await self._extract_from_dom()
            
            # 4. Last resort: Regex JSON extraction from page source
            if not products_map:
                logger.info("Trying regex JSON extraction...")
                content = await self.page.content()
                products_map = self._extract_json_from_content(content)
            
            logger.info(f"Total products extracted: {len(products_map)}")
            
            # Convert to ProductItem list
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            
            for pid, p in products_map.items():
                try:
                    item = self._create_product_item(p, pid, category, subcategory, clicked_label, pincode, timestamp)
                    if item:
                        results.append(item)
                except Exception as e:
                    logger.warning(f"Skipping product {pid}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error scraping assortment: {e}")
            try:
                await self.page.screenshot(path="error_zepto_assortment.png")
            except:
                pass
            
        return results

    def _find_products_in_json(self, data, collector):
        """Recursively find products in JSON data."""
        if isinstance(data, dict):
            # Check if this looks like a product
            # Zepto products typically have: productVariantId, name, sellingPrice/mrp
            pvid = data.get('productVariantId') or data.get('id') or data.get('productId')
            name = data.get('name') or data.get('productName')
            price = data.get('sellingPrice') or data.get('price') or data.get('discountedPrice')
            mrp = data.get('mrp') or data.get('maxRetailPrice')
            
            if pvid and name and (price or mrp):
                collector[str(pvid)] = data
            
            # Recurse
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    self._find_products_in_json(value, collector)
                    
        elif isinstance(data, list):
            for item in data:
                self._find_products_in_json(item, collector)

    async def _extract_from_dom(self) -> dict:
        """Extract product data from DOM elements."""
        products = {}
        
        try:
            # Look for product links with /pn/ pattern (Zepto product URLs)
            product_links = await self.page.evaluate('''() => {
                const products = [];
                const processedPvids = new Set();
                const links = document.querySelectorAll('a[href*="/pn/"]');
                
                links.forEach(link => {
                    // Get the parent product card container - go up several levels
                    let container = link;
                    for (let i = 0; i < 5; i++) {
                        if (container.parentElement) {
                            container = container.parentElement;
                        }
                    }
                    
                    const text = container.innerText || '';
                    const href = link.href;
                    
                    // Extract pvid from URL
                    const pvidMatch = href.match(/pvid\\/([a-f0-9-]+)/i);
                    const pvid = pvidMatch ? pvidMatch[1] : null;
                    
                    // Skip duplicates
                    if (!pvid || processedPvids.has(pvid)) return;
                    processedPvids.add(pvid);
                    
                    // Extract product name from URL path: /pn/product-name-here/pvid/xxx
                    const nameMatch = href.match(/\\/pn\\/([^\\/]+)\\/pvid/i);
                    const urlName = nameMatch ? nameMatch[1].replace(/-/g, ' ') : null;
                    
                    // Find image within the product card
                    const img = container.querySelector('img');
                    let imageUrl = null;
                    if (img) {
                        imageUrl = img.src || img.getAttribute('data-src') || img.getAttribute('srcset')?.split(' ')[0];
                    }
                    
                    // Extract price patterns - look for ₹XXX
                    const allPrices = text.match(/₹\\s*(\\d+)/g) || [];
                    let price = null;
                    let mrp = null;
                    if (allPrices.length >= 2) {
                        // First is selling price, second is MRP (crossed out)
                        price = parseInt(allPrices[0].replace(/₹\\s*/, ''));
                        mrp = parseInt(allPrices[1].replace(/₹\\s*/, ''));
                    } else if (allPrices.length === 1) {
                        price = parseInt(allPrices[0].replace(/₹\\s*/, ''));
                        mrp = price;
                    }
                    
                    // Extract weight/pack size patterns - multiple patterns
                    let weight = null;
                    const weightPatterns = [
                        /(\\d+(?:\\.\\d+)?\\s*(?:kg|g|gm|ml|l|ltr|litre|pcs?|pc|pack|unit|piece)s?)/i,
                        /(\\d+\\s*x\\s*\\d+\\s*(?:g|ml|pcs?))/i,  // 6 x 100g format
                        /\\((\\d+(?:\\.\\d+)?\\s*(?:kg|g|gm|ml|l)\\s*)\\)/i,  // (500 g) format
                    ];
                    for (const pattern of weightPatterns) {
                        const m = text.match(pattern);
                        if (m) {
                            weight = m[1] || m[0];
                            break;
                        }
                    }
                    
                    // Extract brand - usually appears before or after product name in text
                    let brand = null;
                    const lines = text.split('\\n').map(l => l.trim()).filter(l => l && !l.startsWith('₹') && l !== 'ADD');
                    if (lines.length > 0 && lines[0].length < 30) {
                        // First short line might be brand
                        brand = lines[0];
                    }
                    
                    products.push({
                        pvid: pvid,
                        urlName: urlName,
                        text: text.substring(0, 800),
                        href: href,
                        price: price,
                        mrp: mrp,
                        weight: weight,
                        imageUrl: imageUrl,
                        brand: brand
                    });
                });
                return products;
            }''')
            
            for p in product_links:
                if p.get('pvid') and p.get('price'):
                    # Get name from URL (more reliable)
                    name = p.get('urlName', '')
                    
                    # Title case the name
                    if name:
                        name = name.title()
                    else:
                        # Fallback to text parsing
                        text = p.get('text', '')
                        lines = [l.strip() for l in text.split('\n') if l.strip()]
                        name = lines[0] if lines else "Unknown Product"
                        if name.startswith('₹') or name == 'ADD':
                            name = lines[1] if len(lines) > 1 else "Unknown Product"
                    
                    products[p['pvid']] = {
                        'name': name,
                        'sellingPrice': p.get('price'),
                        'mrp': p.get('mrp') or p.get('price'),
                        'url': p.get('href'),
                        'productVariantId': p['pvid'],
                        'packSize': p.get('weight'),
                        'imageUrl': p.get('imageUrl'),
                        'brand': p.get('brand')
                    }
                    
            logger.info(f"DOM extraction found {len(products)} products")
            
        except Exception as e:
            logger.warning(f"DOM extraction failed: {e}")
            
        return products

    def _extract_json_from_content(self, content: str) -> dict:
        """Extract product JSON from page content using regex."""
        products = {}
        
        # Look for patterns like "sellingPrice":XXX
        patterns = [
            r'"productVariantId"\s*:\s*"([^"]+)"[^}]*"name"\s*:\s*"([^"]+)"[^}]*"sellingPrice"\s*:\s*(\d+)',
            r'"name"\s*:\s*"([^"]+)"[^}]*"sellingPrice"\s*:\s*(\d+)[^}]*"mrp"\s*:\s*(\d+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if len(match) >= 3:
                    pvid = match[0] if len(match[0]) > 10 else f"prod_{len(products)}"
                    name = match[1] if len(match) > 1 else match[0]
                    price = int(match[2]) if len(match) > 2 else int(match[1])
                    
                    if name and price:
                        products[pvid] = {
                            'name': name,
                            'sellingPrice': price,
                            'mrp': price,
                            'productVariantId': pvid
                        }
        
        return products

    def _create_product_item(self, p: dict, pid: str, category: str, subcategory: str, 
                            clicked_label: str, pincode: str, timestamp: str) -> ProductItem:
        """Create a ProductItem from raw product data."""
        
        # Extract name
        name = (p.get('name') or p.get('productName') or 
               p.get('title') or p.get('display_name') or "")
        
        if not name:
            return None
        
        # Extract pricing - Zepto uses sellingPrice and mrp
        price = float(p.get('sellingPrice') or p.get('price') or 
                     p.get('discountedPrice') or 0)
        mrp = float(p.get('mrp') or p.get('maxRetailPrice') or 
                   p.get('original_price') or price)
        
        if price == 0 and mrp == 0:
            return None
        
        # If we only have MRP, use it as price too
        if price == 0:
            price = mrp
        
        # Extract availability
        is_sold_out = (
            p.get('outOfStock') == True or
            p.get('isSoldOut') == True or
            p.get('is_sold_out') == True or
            p.get('productState') == 'OUT_OF_STOCK' or
            p.get('available_quantity') == 0
        )
        
        # Extract inventory
        inventory = None
        inv_fields = ['inventory', 'availableQuantity', 'available_quantity', 'stock']
        for field in inv_fields:
            if field in p and p[field] is not None:
                try:
                    inventory = int(p[field])
                    break
                except:
                    pass
        
        # Extract weight/pack size
        weight = (p.get('packSize') or p.get('pack_size') or 
                 p.get('weight') or p.get('unit') or 
                 p.get('packDesc') or "N/A")
        
        # Extract shelf life (Zepto uses shelfLifeInHours)
        shelf_life = None
        shelf_fields = ['shelfLifeInHours', 'shelf_life_in_hours', 'shelfLife']
        for field in shelf_fields:
            if field in p and p[field]:
                try:
                    shelf_life = int(p[field])
                    break
                except:
                    pass
        
        # Build product URL
        product_url = p.get('url') or p.get('productUrl') or ""
        if not product_url and pid:
            safe_name = name.lower().replace(' ', '-').replace('/', '-')[:50]
            product_url = f"{self.base_url}pn/{safe_name}/pvid/{pid}"
        
        return {
            "platform": "zepto",
            "category": category,
            "subcategory": subcategory,
            "clicked_label": clicked_label,
            "name": name,
            "brand": p.get('brand') or p.get('brandName') or "Unknown",
            "base_product_id": str(p.get('productId') or pid),
            "product_id": str(pid),
            "group_id": p.get('groupId') or p.get('variantGroupId'),
            "merchant_type": p.get('merchantType') or p.get('sellerType'),
            "mrp": mrp,
            "price": price,
            "weight": str(weight),
            "shelf_life_in_hours": shelf_life,
            "eta": self.delivery_eta,
            "availability": "Out of Stock" if is_sold_out else "In Stock",
            "inventory": inventory,
            "store_id": str(p.get('storeId') or p.get('merchantId') or "Unknown"),
            "product_url": product_url,
            "image_url": p.get('imageUrl') or p.get('image') or p.get('thumbnail') or "N/A",
            "scraped_at": timestamp,
            "pincode_input": pincode
        }

    async def scrape_availability(self, product_url: str) -> AvailabilityResult:
        """Placeholder for availability scraping - can be implemented later."""
        logger.info(f"Scraping availability from {product_url}")
        
        return {
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
            "variant_count": None,
            "variant_in_stock_count": None,
            "inventory": None,
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "error": "Not implemented yet"
        }
