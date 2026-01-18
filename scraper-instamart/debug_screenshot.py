from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            geolocation={'latitude': 12.9716, 'longitude': 77.5946},
            permissions=['geolocation']
        )
        try:
            print("Navigating to Instamart...")
            page.goto("https://www.swiggy.com/instamart", timeout=60000, wait_until='domcontentloaded')
            page.wait_for_timeout(5000)
            
            print("Taking screenshot...")
            page.screenshot(path="debug_homepage.png", full_page=True)
            
            # Check for specific texts
            content = page.content()
            if "Setup your location" in content:
                print("Found 'Setup your location' text")
            if "Locate Me" in content:
                print("Found 'Locate Me' text")
                
            print("Captured debug_homepage.png")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    run()
