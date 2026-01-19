
import asyncio
import json
from scrapers.zepto import ZeptoScraper

async def main():
    scraper = ZeptoScraper(headless=True)
    await scraper.start()
    await scraper.set_location("560001")
    
    url = "https://www.zepto.com/cn/munchies/chips-crisps/cid/d2c2a144-43cd-43e5-b308-92628fa68596"
    
    print(f"Navigating to {url}...")
    
    captured_jsons = []
    
    async def handle_response(response):
        ct = response.headers.get("content-type", "")
        if "application/json" in ct or "text/x-component" in ct:
            try:
                if "json" in ct:
                    data = await response.json()
                    captured_jsons.append({"url": response.url, "type": "json", "data": data})
                else:
                    text = await response.text()
                    captured_jsons.append({"url": response.url, "type": "rsc", "data": text})
                    
                print(f"Captured {ct} from {response.url}")
            except: pass

    scraper.page.on("response", handle_response)
    
    try:
        await scraper.page.goto(url, timeout=30000, wait_until='networkidle')
        await asyncio.sleep(5)
    except Exception as e:
        print(f"Navigation error: {e}")
        
    print(f"Captured {len(captured_jsons)} JSON responses")
    
    # Save the most promising one (largest or containing 'products')
    best_candidate = None
    
    for item in captured_jsons:
        text = json.dumps(item['data'])
        if "availableQuantity" in text or "sellingPrice" in text:
             print(f"Found candidate with price/qty: {item['url']}")
             best_candidate = item
             break
             
    if best_candidate:
        with open("debug_api_response.json", "w", encoding="utf-8") as f:
            json.dump(best_candidate, f, indent=2)
        print("Saved best candidate to debug_api_response.json")
    else:
        # Save all just in case
        with open("debug_all_api_responses.json", "w", encoding="utf-8") as f:
            json.dump(captured_jsons, f, indent=2)
        print("Saved all responses")

    await scraper.stop()

if __name__ == "__main__":
    asyncio.run(main())
