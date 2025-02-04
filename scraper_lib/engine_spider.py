# scraper_module/scraper_lib/engine_spider.py
import scrapy
from scrapy_playwright.page import PageMethod
from .helpers import find_pages, find, _select

class StepSpider(scrapy.Spider):
    name = "step_spider"
    custom_settings = {}  # Allow per-spider settings override if needed

    def __init__(self, start_url, steps, use_playwright=False, pagination=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_url = start_url
        self.steps = steps or []
        self.use_playwright = use_playwright
        self.pagination = pagination
        if self.use_playwright:
            self.custom_settings.update({
                "PLAYWRIGHT_BROWSER_TYPE": "chromium",
                "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},
            })

    def start_requests(self):
        # If pagination is configured, use handle_pagination; otherwise, parse steps directly.
        callback = self.handle_pagination if self.pagination else self.parse_steps
        yield self._make_request(self.start_url, callback)

    def _make_request(self, url, callback):
        meta = {}
        if self.use_playwright:
            meta.update({
                "playwright": True,
                "playwright_page_methods": [PageMethod("wait_for_timeout", 8000)]
            })
        return scrapy.Request(url, callback=callback, meta=meta)

    def _search_links_recursive(self, response):
        visited = response.meta.setdefault("visited", set())
        # Optionally parse the current page if a target selector exists.
        target_page_selector = self.pagination.get("target_page_selector")
        if (not target_page_selector) or _select(response, target_page_selector):
            yield from self.parse_steps(response)
        # Gather links from the defined search space.
        search_space = self.pagination.get("search_space")
        if not search_space:
            return
        for parent in _select(response, search_space):
            for ln in _select(parent, "xpath:.//a/@href"):
                href = ln.get()
                if href:
                    abs_url = response.urljoin(href)
                    if abs_url not in visited:
                        visited.add(abs_url)
                        yield self._make_request(abs_url, self._search_links_recursive)

    def handle_pagination(self, response):
        target_page_selector = self.pagination.get("target_page_selector")
        if (not target_page_selector) or _select(response, target_page_selector):
            yield from self.parse_steps(response)
        ptype = self.pagination.get("type")
        if ptype == "listed_links":
            for url in find_pages(response, self.pagination):
                yield self._make_request(response.urljoin(url), self.handle_pagination)
        elif ptype == "search_links":
            yield from self._search_links_recursive(response)
        else:
            yield from self.parse_steps(response)

    def parse_steps(self, response, step_index=0, parent_item=None):
        if step_index >= len(self.steps):
            if parent_item:
                yield parent_item
            return

        step = self.steps[step_index]
        action = step.get("action")
        if action == "find":
            for item in find(response, step):
                yield from self.parse_steps(response, step_index + 1, item)
        elif action == "follow":
            link_field = step.get("link_field")
            if not parent_item or not parent_item.get(link_field):
                yield parent_item
            else:
                links = parent_item[link_field]
                if not isinstance(links, list):
                    links = [links]
                next_steps = step.get("next_steps", [])
                for url in links:
                    # Use response.follow to handle relative URLs directly.
                    yield response.follow(url, callback=lambda r, s=next_steps, pi=parent_item: self.parse_followed_steps(r, s, pi))
        else:
            # Skip unrecognized actions
            yield from self.parse_steps(response, step_index + 1, parent_item)

    def parse_followed_steps(self, response, steps, parent_item):
        if not steps:
            yield parent_item
            return
        step = steps[0]
        action = step.get("action")
        if action == "find":
            for item in find(response, step):
                merged = {**parent_item, **item}
                yield from self.parse_followed_steps(response, steps[1:], merged)
        else:
            yield from self.parse_followed_steps(response, steps[1:], parent_item)
