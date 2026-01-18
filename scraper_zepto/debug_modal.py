import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        # Try headless=True first to be safe, but if it fails we might need False
        # But for debug let's try to match run_zepto settings
        browser = await p.chromium.launch(headless=False) 
        context = await browser.new_context(
             viewport={'width': 1920, 'height': 1080},
             user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        try:
            print("Navigating to Zepto...")
            await page.goto("https://www.zepto.com/", timeout=60000, wait_until='domcontentloaded')
            
            trigger_selector = "button[aria-label='Select Location'], h3[data-testid='user-address'], span:has-text('Select Location')"
            try:
                await page.wait_for_selector(trigger_selector, timeout=10000)
                await page.click(trigger_selector)
                print("Clicked trigger...")
                await page.wait_for_timeout(3000)
                
                print("Saving Modal HTML...")
                content = await page.content()
                with open("debug_modal.html", "w", encoding="utf-8") as f:
                    f.write(content)
                    
                await page.screenshot(path="debug_modal_view.png")
            except:
                print("Trigger wait failed")

            print("Done.")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
