import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
             viewport={'width': 1920, 'height': 1080},
             user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        try:
            print("Navigating to Zepto...")
            await page.goto("https://www.zepto.com/", timeout=60000, wait_until='domcontentloaded')
            await page.wait_for_timeout(5000)
            
            print(" taking screenshot...")
            await page.screenshot(path="debug_homepage.png")
            
            print("Saving HTML...")
            content = await page.content()
            with open("debug_homepage.html", "w", encoding="utf-8") as f:
                f.write(content)
                
            print("Done.")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
