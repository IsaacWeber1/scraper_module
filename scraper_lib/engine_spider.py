# scraper_module/scraper_lib/engine_spider.py

import scrapy
from scrapy_playwright.page import PageMethod
from .helpers import find_repeating

class StepSpider(scrapy.Spider):
    name = "step_spider"

    # Optionally define default settings
    custom_settings = {
        # If use_playwright=True at runtime, we'll update these below
        # "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        # "PLAYWRIGHT_LAUNCH_OPTIONS": {...}
    }

    def __init__(self, start_url=None, steps=None, use_playwright=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_url = start_url
        self.steps = steps or []
        self.use_playwright = use_playwright

        if self.use_playwright:
            # Override or set some settings specifically for Playwright
            self.custom_settings.update({
                "PLAYWRIGHT_BROWSER_TYPE": "chromium",
                "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True}
            })
    
    def start_requests(self):
        """
        Kick off the first request to self.start_url using a custom method
        that sets meta['playwright']=True if needed.
        """
        yield self._make_request(self.start_url, callback=self.parse_steps)

    def _make_request(self, url, callback):
        """
        A helper to build a Scrapy Request with optional Playwright meta.
        """
        if self.use_playwright:
            meta = {
                "playwright": True,
                # Optionally wait a bit or wait for a selector
                "playwright_page_methods": [
                    PageMethod("wait_for_timeout", 8000),  # 8s just as an example
                    # or: PageMethod("wait_for_selector", "div.product-group")
                ]
            }
        else:
            meta = {}
        
        return scrapy.Request(
            url,
            callback=callback,
            meta=meta,
            dont_filter=True  # optional
        )

    def parse_steps(self, response, step_index=0, parent_item=None):
        # Normal step-based logic, same as before.
        # But *all* requests we make in follow or sub-steps can also go through _make_request
        # if you want them rendered via Playwright.
        if step_index >= len(self.steps):
            if parent_item:
                yield parent_item
            return

        step = self.steps[step_index]
        action = step["action"]

        if action == "find_repeating":
            # Use your find_repeating helper
            for item in find_repeating(response, step):
                yield from self.parse_steps(response, step_index + 1, item)

        elif action == "follow":
            # Suppose step has "link_field"
            link_field = step["link_field"]
            if not parent_item or not parent_item.get(link_field):
                # skip
                yield parent_item
            else:
                links = parent_item[link_field]
                if not isinstance(links, list):
                    links = [links]

                next_steps = step.get("next_steps", [])
                for url in links:
                    # Note: now we generate a new *playwright* request
                    yield self._make_request(
                        response.urljoin(url),
                        callback=lambda r, s=next_steps, pi=parent_item: self.parse_followed_steps(r, s, pi)
                    )
        else:
            # unknown step
            yield from self.parse_steps(response, step_index + 1, parent_item)

    def parse_followed_steps(self, response, steps, parent_item):
        # Similar logic to run sub-steps
        if not steps:
            yield parent_item
            return
        step = steps[0]
        action = step["action"]
        if action == "find_repeating":
            for item in find_repeating(response, step):
                merged = {**parent_item, **item}
                yield from self.parse_followed_steps(response, steps[1:], merged)
        else:
            # etc.
            yield from self.parse_followed_steps(response, steps[1:], parent_item)
