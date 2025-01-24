# scraper_module/scraper_lib/engine_spider.py

import scrapy
from scrapy_playwright.page import PageMethod
from .helpers import find_pages, find_repeating

class StepSpider(scrapy.Spider):
    name = "step_spider"

    # Optionally define default settings
    custom_settings = {
        # These settings can be overridden if use_playwright=True
    }

    def __init__(
        self,
        start_url=None,
        steps=None,
        use_playwright=False,
        pagination=None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.start_url = start_url
        self.steps = steps or []
        self.use_playwright = use_playwright
        self.pagination = pagination

        if self.use_playwright:
            # Override or set some settings specifically for Playwright
            self.custom_settings.update({
                "PLAYWRIGHT_BROWSER_TYPE": "chromium",
                "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True}
            })

    def start_requests(self):
        if self.pagination:
            # Start with handling pagination
            yield self._make_request(self.start_url, callback=self.handle_pagination)
        else:
            # Start with parsing steps
            yield self._make_request(self.start_url, callback=self.parse_steps)

    def _make_request(self, url, callback):
        """
        A helper to build a Scrapy Request with optional Playwright meta.
        """
        if self.use_playwright:
            meta = {
                "playwright": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_timeout", 8000),  # Wait for 8 seconds
                    # You can add more PageMethods if needed
                ]
            }
        else:
            meta = {}

        return scrapy.Request(
            url,
            callback=callback,
            meta=meta,
            dont_filter=True  # Prevents filtering of duplicate requests
        )

    def handle_pagination(self, response):
        """
        Handle pagination by extracting pagination links and scheduling new requests.
        Also process the current page's items.
        """
        # Extract and follow pagination links
        if self.pagination and self.pagination.get("type") == "link_iterator":
            for url in find_pages(response, self.pagination):
                yield self._make_request(response.urljoin(url), callback=self.handle_pagination)

        # Process items on the current page
        if self.steps:
            for item in find_repeating(response, self.steps[0]):
                yield from self.parse_steps(response, 1, item)

    def parse_steps(self, response, step_index=0, parent_item=None):
        """
        Recursively process steps to extract and follow links.
        """
        if step_index >= len(self.steps):
            if parent_item:
                yield parent_item
            return

        step = self.steps[step_index]
        action = step.get("action")

        if action == "find_repeating":
            # Extract items based on the current step
            for item in find_repeating(response, step):
                yield from self.parse_steps(response, step_index + 1, item)

        elif action == "follow":
            # Follow links extracted from the current item
            link_field = step.get("link_field")
            if not parent_item or not parent_item.get(link_field):
                # Skip if the link field is missing
                yield parent_item
            else:
                links = parent_item[link_field]
                if not isinstance(links, list):
                    links = [links]

                next_steps = step.get("next_steps", [])
                for url in links:
                    # Schedule new requests with the next steps
                    yield self._make_request(
                        response.urljoin(url),
                        callback=lambda r, s=next_steps, pi=parent_item: self.parse_followed_steps(r, s, pi)
                    )

        else:
            # Unknown action; skip to the next step
            yield from self.parse_steps(response, step_index + 1, parent_item)

    def parse_followed_steps(self, response, steps, parent_item):
        """
        Process sub-steps after following a link.
        """
        if not steps:
            yield parent_item
            return

        step = steps[0]
        action = step.get("action")

        if action == "find_repeating":
            for item in find_repeating(response, step):
                merged = {**parent_item, **item}
                yield from self.parse_followed_steps(response, steps[1:], merged)
        else:
            # Handle other actions similarly
            yield from self.parse_followed_steps(response, steps[1:], parent_item)
