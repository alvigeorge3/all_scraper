import asyncio
from playwright.async_api import async_playwright, Page, BrowserContext
from abc import ABC, abstractmethod
import logging
import random
from typing import List, Dict, Any
from .models import ProductItem, AvailabilityResult

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    def __init__(self, headless=False):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    async def random_sleep(self, min_seconds=1.5, max_seconds=4.0):
        """Waits for a random amount of time."""
        delay = random.uniform(min_seconds, max_seconds)
        logger.debug(f"Sleeping for {delay:.2f}s")
        await asyncio.sleep(delay)

    async def human_type(self, selector: str, text: str, delay_min=50, delay_max=200):
        """Types text into an input field with random delays between keystrokes."""
        logger.debug(f"Human typing into {selector}: {text}")
        await self.page.focus(selector)
        for char in text:
            await self.page.keyboard.type(char, delay=random.randint(delay_min, delay_max))
        await self.random_sleep(0.5, 1.5)

    def _cubic_bezier(self, t, p0, p1, p2, p3):
        """Calculates a point on a cubic Bezier curve."""
        return (1-t)**3 * p0 + 3 * (1-t)**2 * t * p1 + 3 * (1-t) * t**2 * p2 + t**3 * p3

    async def human_move_to(self, target_x, target_y, steps=25):
        """Moves mouse to coordinates using a Bezier curve trajectory."""
        start_x = self.page.mouse._x if hasattr(self.page.mouse, '_x') else 0
        start_y = self.page.mouse._y if hasattr(self.page.mouse, '_y') else 0
        
        # If playwright doesn't expose internal coordinates easily, assume 0,0 or just do linear if unknown
        # Unfortunately Playwright Python sync API doesn't expose current position easily.
        # We can track it manually or just use random start near target if we jump? 
        # Actually proper emulation requires knowing start. 
        # We will implement a "Jump to vicinity" then curve to target if start is unknown.
        
        # For simplicity and robustness, let's define Control Points
        # P0 = Start
        # P3 = Target
        # P1 = random point between start and target with offset
        # P2 = random point near target with offset
        
        # Delta
        delta_x = target_x - start_x
        delta_y = target_y - start_y
        
        # Control points with randomness
        p1_x = start_x + (delta_x * random.uniform(0.2, 0.5)) + random.uniform(-100, 100)
        p1_y = start_y + (delta_y * random.uniform(0.2, 0.5)) + random.uniform(-100, 100)
        
        p2_x = start_x + (delta_x * random.uniform(0.5, 0.8)) + random.uniform(-100, 100)
        p2_y = start_y + (delta_y * random.uniform(0.5, 0.8)) + random.uniform(-100, 100)
        
        for i in range(steps + 1):
            t = i / steps
            x = self._cubic_bezier(t, start_x, p1_x, p2_x, target_x)
            y = self._cubic_bezier(t, start_y, p1_y, p2_y, target_y)
            await self.page.mouse.move(x, y)
             # Variable sleep for velocity changes (slower at start/end)
            if i < steps * 0.2 or i > steps * 0.8:
                await asyncio.sleep(random.uniform(0.005, 0.015))
            else:
                 await asyncio.sleep(random.uniform(0.001, 0.005))


    async def human_click(self, selector: str):
        """Moves mouse to element using Bezier curves, pauses, then clicks."""
        logger.debug(f"Human clicking {selector} with Bezier path")
        try:
            # Move to element
            element = await self.page.wait_for_selector(selector, state="visible", timeout=10000)
            box = await element.bounding_box()
            if box:
                # Target center with randomness
                target_x = box["x"] + box["width"] / 2 + random.uniform(-5, 5)
                target_y = box["y"] + box["height"] / 2 + random.uniform(-5, 5)
                
                await self.human_move_to(target_x, target_y)
            
            await self.random_sleep(0.1, 0.3)
            await self.page.click(selector, delay=random.randint(50, 150)) # holding click briefly
            await self.random_sleep(0.5, 1.0)
        except Exception as e:
            logger.warning(f"Human click failed for {selector}, falling back to standard click: {e}")
            await self.page.click(selector)

    async def smooth_scroll(self, min_px=300, max_px=700):
        """Scrolls down and back up to simulate looking around."""
        try:
            scroll_amount = random.randint(min_px, max_px)
            logger.debug(f"Smooth scrolling {scroll_amount}px")
            
            # Scroll Down
            await self.page.mouse.wheel(0, scroll_amount)
            await self.random_sleep(1.0, 2.0)
            
            # Scroll Up a bit
            await self.page.mouse.wheel(0, -1 * (scroll_amount // 2))
            await self.random_sleep(0.5, 1.5)
        except Exception as e:
            logger.warning(f"Smooth scroll failed: {e}")

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

        # Rotation of modern User Agents
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0'
        ]
        ua = random.choice(user_agents)
        logger.info(f"Using User-Agent: {ua}")

        self.context = await self.browser.new_context(
             viewport={'width': 1920, 'height': 1080},
             user_agent=ua
        )
        
        # KEY STEALTH SCRIPT: Comprehensive Overrides
        await self.context.add_init_script("""
            // 1. Pass Webdriver Test
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            // 2. Mock Plugins (Zepto/Cloudflare checks)
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5] 
            });

            // 3. Mock Languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });

            // 4. Mock Chrome Runtime (Execution match)
            window.chrome = {
                runtime: {}
            };

            // 5. Mock Permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                Promise.resolve({ state: 'granted' }) :
                originalQuery(parameters)
            );
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
