
# ... existing imports ...
import re
import time
import json
from typing import List, Dict, Any, Optional
from scrapers.base import BaseScraper, logger
from scrapers.models import ProductItem

class ZeptoScraper(BaseScraper):
    def __init__(self, headless: bool = True):
        super().__init__(headless)
        self.delivery_eta = "N/A"
        self.store_id = "N/A"

    async def set_location(self, pincode: str):
        # ... existing implementation ...
        pass
    
    async def get_all_categories(self) -> List[str]:
        # ... existing implementation ...
        return []

    async def scrape_assortment(self, category_url: str, pincode: str = "N/A") -> List[ProductItem]:
        logger.info(f"Scraping {category_url}")
        products: List[ProductItem] = []
        captured_data = []

        async def handle_response(response):
            try:
                ct = response.headers.get("content-type", "").lower()
                if "image" in ct or "font" in ct or "css" in ct or "javascript" in ct:
                    return
                # Capture useful types
                if response.status == 200:
                    try:
                        data = await response.json()
                        captured_data.append({"url": response.url, "type": "json", "data": data})
                    except:
                         try:
                             text = await response.text()
                             # Save string data if length seems substantial or type matches
                             # Flight data is usually huge
                             if len(text) > 10000 or "x-component" in ct:
                                 captured_data.append({"url": response.url, "type": ct, "data": text})
                         except: pass
            except: pass

        self.page.on("response", handle_response)

        try:
            await self.page.goto(category_url, timeout=60000)
            await self.human_delay(3)
            await self.human_scroll()
            await self.human_delay(2)
            
            # Dump HTML (Optional kept for debug)
            # content = await self.page.content()
            # with open("debug_plp.html", "w", encoding="utf-8") as f: f.write(content)
            
        except Exception as e:
            logger.error(f"Error navigating/scrolling: {e}")
        finally:
             self.page.remove_listener("response", handle_response)

        # Parse captured data
        logger.info(f"Captured {len(captured_data)} responses. Parsing...")
        
        for capture in captured_data:
            content = capture.get("data")
            if isinstance(content, str) and len(content) > 20000:
                # Regex parsing logic
                link_matches = re.finditer(r'href=\"(/pn/[^\"]+)\"', content)
                for match in link_matches:
                    try:
                        url_part = match.group(1)
                        start_idx = match.end()
                        snippet = content[start_idx:start_idx+500]
                        
                        name_match = re.search(r'>([^<]+)</a>', snippet)
                        product_name = "Unknown"
                        if name_match:
                            product_name = name_match.group(1).replace("<!-- -->", "").strip()
                            product_name = re.sub(r'^\d+\.\s*', '', product_name)
                            
                        price_match = re.search(r'<td>(₹\d+)</td>', snippet)
                        price = "N/A"
                        if price_match:
                            price = price_match.group(1)
                            
                        if not any(p['base_product_id'] == url_part for p in products):
                            item: ProductItem = {
                                "Category": "Unknown",
                                "Subcategory": "Unknown",
                                "Item Name": product_name,
                                "Brand": "Unknown", 
                                "Mrp": "N/A", 
                                "Price": price,
                                "Weight/pack_size": "N/A",
                                "Delivery ETA": self.delivery_eta,
                                "availability": "In Stock",
                                "inventory": "N/A",
                                "store_id": self.store_id,
                                "base_product_id": url_part,
                                "shelf_life_in_hours": "N/A",
                                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                                "pincode_input": pincode,
                                "clicked_label": "N/A"
                            }
                            products.append(item)
                    except Exception as e:
                        pass
                        
        logger.info(f"Scraped {len(products)} products from Flight data")
        return products
