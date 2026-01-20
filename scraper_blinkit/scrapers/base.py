import asyncio
from playwright.async_api import async_playwright, Page, BrowserContext
from abc import ABC, abstractmethod
import logging
from typing import List, Dict, Any
from .models import ProductItem, AvailabilityResult

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


import random
import time

class BaseScraper(ABC):
    def __init__(self, headless=False, proxy=None):
        self.headless = headless
        self.proxy = proxy
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.proxies_list = []
        
        # Load proxies from file
        try:
            with open("proxies.txt", "r") as f:
                self.proxies_list = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            logger.info(f"Loaded {len(self.proxies_list)} proxies from proxies.txt")
        except FileNotFoundError:
            logger.warning("proxies.txt not found. No proxy rotation available.")
        except Exception as e:
            logger.warning(f"Error loading proxies.txt: {e}")

    async def human_delay(self, min_seconds=1.0, max_seconds=3.0):
        """Random delay to simulate human reaction time."""
        delay = random.uniform(min_seconds, max_seconds)
        logger.debug(f"Sleeping for {delay:.2f}s")
        await asyncio.sleep(delay)

    async def human_scroll(self):
        """Scrolls down and back up slightly to trigger lazy loading."""
        try:
            # Scroll down
            scroll_y = random.randint(300, 700)
            await self.page.mouse.wheel(0, scroll_y)
            await self.human_delay(0.5, 1.5)
            
            # Scroll up a bit
            await self.page.mouse.wheel(0, -random.randint(100, scroll_y))
            await self.human_delay(0.5, 1.0)
        except:
            pass
            
    async def human_type(self, selector: str, text: str):
        """Types text with random delays between keystrokes."""
        await self.page.focus(selector)
        for char in text:
            await self.page.keyboard.type(char)
            # Random typing speed: 50ms to 200ms usually
            await asyncio.sleep(random.uniform(0.05, 0.2))
        await self.human_delay(0.5, 1.0)

    async def start(self):
        self.playwright = await async_playwright().start()
        
        # Try to launch system edge, then chrome, then bundled chromium
        browsers_to_try = [
            {'channel': 'msedge'},
            {'channel': 'chrome'},
            {}, # Default bundled as fallback
        ]
        
        # Anti-detection arguments
        stealth_args = [
            '--disable-blink-features=AutomationControlled',
            '--disable-infobars',
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-extensions',
            '--disable-remote-fonts',
            '--disable-gpu' # Often helpful in headless
        ]

        for browser_kwargs in browsers_to_try:
            # Merge stealth args
            browser_kwargs['args'] = browser_kwargs.get('args', []) + stealth_args
            
            try:
                self.browser = await self.playwright.chromium.launch(headless=self.headless, **browser_kwargs)
                logger.info(f"Launched browser with kwargs: {browser_kwargs}")
                break
            except Exception as e:
                logger.warning(f"Failed to launch browser with {browser_kwargs}: {e}")
        
        if not self.browser:
            raise Exception("Could not launch any browser (Chromium, Chrome, or Edge)")

        await self._create_context_with_proxy()

    async def _create_context_with_proxy(self):
        """Creates a new browser context with a proxy (if available) and applies stealth."""
        if self.context:
            await self.context.close()

        # Rotate User Agents
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/121.0.0.0 Safari/537.36'
        ]
        chosen_ua = random.choice(user_agents)
        logger.info(f"Using User-Agent: {chosen_ua}")
        
        context_args = {
            'viewport': {'width': 1920, 'height': 1080},
            'user_agent': chosen_ua
        }
        
        # Proxy Selection
        selected_proxy = self.proxy
        if not selected_proxy and self.proxies_list:
            # Pick a regular proxy string
            proxy_str = random.choice(self.proxies_list)
            # Parse it for Playwright if needed, or pass as server
            # Format expected by Playwright: { "server": "http://ip:port", "username": "...", "password": "..." }
            # Simplified parsing: assuming standard http://user:pass@ip:port or http://ip:port
            logger.info(f"Rotating to proxy: {proxy_str}")
            
            # Basic parsing logic
            try:
                import urllib.parse
                parsed = urllib.parse.urlparse(proxy_str)
                selected_proxy = {
                    "server": f"{parsed.scheme}://{parsed.hostname}:{parsed.port}"
                }
                if parsed.username:
                    selected_proxy["username"] = parsed.username
                if parsed.password:
                    selected_proxy["password"] = parsed.password
            except Exception as e:
                logger.error(f"Failed to parse proxy {proxy_str}: {e}")
        
        if selected_proxy:
            logger.info(f"Using Proxy: {selected_proxy.get('server')}")
            context_args['proxy'] = selected_proxy

        self.context = await self.browser.new_context(**context_args)
        
        # PERFORMANCE OPTIMIZATION: Block heavy resources
        await self.context.route("**/*", lambda route: route.abort() 
            if route.request.resource_type in ["image", "media", "font"] 
            else route.continue_())
        
        # KEY STEALTH SCRIPT
        await self.context.add_init_script("""
            // 1. Pass WebDriver test
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            // 2. Mock Plugins (Basic)
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });

            // 3. Mock Languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            
            # 4. Broken Image Handling (Optional, but good for headless)
            # Some checks look for broken 0x0 images in headless
            # script skipped for simplicity, focusing on properties.
        """)
        
        self.page = await self.context.new_page()

    async def rotate_proxy(self):
        """Public method to trigger proxy rotation."""
        logger.info("🔄 Initiating Proxy Rotation...")
        await self._create_context_with_proxy()

    async def stop(self):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    @abstractmethod
    async def set_location(self, pincode: str):
        pass

    @abstractmethod
    async def scrape_assortment(self, category_url: str) -> List[ProductItem]:
        pass

    @abstractmethod
    async def scrape_availability(self, product_url: str) -> AvailabilityResult:
        pass
