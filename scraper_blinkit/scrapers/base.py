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
    def __init__(self, headless=False):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

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

        self.context = await self.browser.new_context(
             viewport={'width': 1920, 'height': 1080},
             user_agent=chosen_ua
        )
        
        # PERFORMANCE OPTIMIZATION: Block heavy resources
        # We block images, media, and fonts.
        # CRITICAL FIX: Do NOT block 'stylesheet' - modern anti-bots check for CSS loading/rendering.
        await self.context.route("**/*", lambda route: route.abort() 
            if route.request.resource_type in ["image", "media", "font"] 
            else route.continue_())
        
        # KEY STEALTH SCRIPT: Remove navigator.webdriver and mask other properties
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
            
            // 4. Broken Image Handling (Optional, but good for headless)
            // Some checks look for broken 0x0 images in headless
            // script skipped for simplicity, focusing on properties.
        """)
        
        self.page = await self.context.new_page()

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
