from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            viewport={'width': 1920, 'height': 1080},
            geolocation={'latitude': 12.9716, 'longitude': 77.5946},
            permissions=['geolocation']
        )
        try:
            print("Navigating...")
            page.goto("https://www.swiggy.com/instamart", timeout=60000)
            page.wait_for_timeout(5000)
            
            # Click location trigger
            print("Clicking location trigger...")
            page.click("div[data-testid='DEFAULT_ADDRESS_CONTAINER']")
            page.wait_for_timeout(3000)
            
            content = page.content()
            with open("debug_instamart_modal.html", "w", encoding="utf-8") as f:
                f.write(content)
            print("Saved modal HTML.")
            
        finally:
            browser.close()

if __name__ == "__main__":
    run()
