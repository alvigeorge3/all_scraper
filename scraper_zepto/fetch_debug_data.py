
import asyncio
from playwright.async_api import async_playwright
import time

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Set location first
        print("Setting location...")
        await page.goto("https://www.zepto.com/")
        await page.wait_for_timeout(3000)
        
        try:
            # Click location
            await page.click("div[data-testid='location-box'], [class*='location-header'], span:has-text('Select Location')", timeout=5000)
        except:
             # Force click center if needed or try JS
             pass
             
        # Wait for modal
        await page.wait_for_timeout(2000)
        try:
             await page.fill("input[placeholder*='Search']", "560001")
             await page.wait_for_timeout(1000)
             await page.keyboard.press("Enter")
             await page.wait_for_timeout(2000)
             await page.click("div[data-testid='location-prediction-item'], [class*='prediction-item']", timeout=3000)
             await page.wait_for_timeout(2000)
             # Confirm
             try:
                await page.click("button:has-text('Confirm'), button:has-text('Continue')", timeout=2000)
             except:
                pass
        except Exception as e:
             print(f"Location error (might be already set): {e}")

        # Go to Biscuits
        url = "https://www.zepto.com/cn/biscuits/biscuits/cid/2552acf2-2f77-4714-adc8-e505de3985db/scid/3a10723e-ba14-4e5c-bdeb-a4dce2c1bec4"
        print(f"Navigating to {url}")
        await page.goto(url)
        await page.wait_for_timeout(5000)
        
        # Scroll to load some items
        await page.evaluate("window.scrollTo(0, 500)")
        await page.wait_for_timeout(2000)
        
        # Dump HTML
        content = await page.content()
        with open("debug_biscuits.html", "w", encoding="utf-8") as f:
            f.write(content)
        print("Saved debug_biscuits.html")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
