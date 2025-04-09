# scraper_module/scraper_lib/engine_spider.py
import scrapy
from scrapy_playwright.page import PageMethod
from .helpers import canonicalize_url, find_pages, find, _select

class StepSpider(scrapy.Spider):
    name = "step_spider"
    custom_settings = {}  # Allow per-spider settings override if needed

    def __init__(self, start_url, steps, use_playwright=False, pagination=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_url = start_url
        self.steps = steps or []
        self.use_playwright = use_playwright
        self.pagination = pagination
        # NEW: Create a spider-level set to track visited URLs
        self.visited_urls = set()
        if self.use_playwright:
            self.custom_settings.update({
                "PLAYWRIGHT_BROWSER_TYPE": "chromium",
                "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True, "timeout": 30000},
            })

    def start_requests(self):
        canonical_start = canonicalize_url(self.start_url)
        # Mark the start_url as visited
        self.visited_urls.add(canonical_start)
        # If pagination is configured, use handle_pagination; otherwise, parse steps directly.
        callback = self.handle_pagination if self.pagination else self.parse_steps
        yield self._make_request(self.start_url, callback)

    def _make_request(self, url, callback):
        meta = {}
        if self.use_playwright:
            meta.update({
                "playwright": True,
                "playwright_page_methods": [PageMethod("wait_for_timeout", 3000)]
            })
            canonical_url = canonicalize_url(url)
            if canonical_url in self.visited_urls:
                return None
            self.visited_urls.add(canonical_url)
        return scrapy.Request(url, callback=callback, meta=meta)

    def _search_links_recursive(self, response, max_depth, depth=0):
        if depth > max_depth:
            self.logger.debug(f"Reached max recursion depth {max_depth}")
            return
        target_page_selector = self.pagination.get("target_page_selector")
        if (not target_page_selector) or (target_page_selector and _select(response, target_page_selector)):
            yield from self.parse_steps(response)
        search_space = self.pagination.get("search_space")
        must_contain = self.pagination.get("base_url")
        if not must_contain:
            must_contain = list(str(self.start_url).strip("http://").split('/'))[0]
        if not search_space:
            return
        for parent in _select(response, search_space):
            for ln in _select(parent, "xpath:.//a/@href"):
                href = ln.get()
                if href:
                    abs_url = response.urljoin(href)
                    canonical_url = canonicalize_url(abs_url)
                    if (canonical_url not in self.visited_urls) and (must_contain in canonical_url):
                        self.visited_urls.add(canonical_url)
                        yield self._make_request(abs_url, lambda r: self._search_links_recursive(response = r, depth = depth+1, max_depth = self.pagination.get("max_depth", 10)))

    def handle_pagination(self, response):
        content_type = response.headers.get('Content-Type', b'').decode('utf8').lower()
        if "html" not in content_type:
            self.logger.debug(f"Skipping pagination on non-HTML response: {response.url} with content type: {content_type}")
            return

        target_page_selector = self.pagination.get("target_page_selector")
        if (not target_page_selector) or (target_page_selector and _select(response, target_page_selector)):
            yield from self.parse_steps(response)
        ptype = self.pagination.get("type")

        if ptype == "listed_links":
            yield from self.parse_steps(response)
            for url in find_pages(response, self.pagination):
                abs_url = response.urljoin(url)
                canonical_url = canonicalize_url(abs_url)
                if canonical_url not in self.visited_urls:
                    self.visited_urls.add(canonical_url)
                    yield self._make_request(abs_url, self.handle_pagination)
        elif ptype == "search_links":
            yield from self._search_links_recursive(response, max_depth = self.pagination.get("max_depth", 10))
        else:
            yield from self.parse_steps(response)


    def parse_steps(self, response, step_index=0, parent_item=None):
        content_type = response.headers.get('Content-Type', b'').decode('utf8').lower()
        if "html" not in content_type:
            self.logger.debug(f"Skipping non-HTML response: {response.url} with content type: {content_type}")
            return
    
        self.logger.debug(f"ATTEMPTING TO PARSE STEP {step_index}")
        if step_index >= len(self.steps):
            if parent_item:
                yield parent_item
            return

        step = self.steps[step_index]
        action = step.get("type", "").lower()
        self.logger.debug(f"ACTION: {action}")
        if action == "find":
            self.logger.debug(f"FINDING {step['task_name']}")
            for item in find(response, step):
                self.logger.debug(f"FOUND ITEM: {item}")
                yield from self.parse_steps(response, step_index + 1, item)
        elif action == "dynamicfind":
            yield from self.dynamic_find(response, step)
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
                    yield response.follow(
                        url,
                        callback=lambda r, s=next_steps, pi=parent_item: self.parse_followed_steps(r, s, pi)
                    )
        else:
            yield from self.parse_steps(response, step_index + 1, parent_item)
            
    '''def dynamic_find(self, response, step):
        # Extract links (each link should be an AJAX URL parameter containing a course ID)
        links = _select(response, step.get("search_space")).getall()
        self.logger.debug(f"DynamicFind: Found {len(links)} links.")
        import re
        for link in links:
            match = re.search(r'coid=(\d+)', link)
            if match:
                coid = match.group(1)
                display_options = 'a:2:{s:8:"~location~";s:8:"~template~";s:28:"~course_program_display_field~";s:0:"";}'
                from urllib.parse import quote
                encoded_display_options = quote(display_options)
                ajax_url = f"{step.get('base_url')}?catoid={step.get('catoid')}&coid={coid}&display_options={encoded_display_options}&show"
                yield scrapy.Request(url=ajax_url, callback=self.parse_dynamic_course, meta={'step': step})'''
                
    def dynamic_find(self, response, step):
        # First, extract AJAX course links (each should contain a course ID in its query string)
        links = _select(response, step.get("search_space")).getall()
        self.logger.debug(f"DynamicFind: Found {len(links)} course links.")
        import re
        for link in links:
            match = re.search(r'coid=(\d+)', link)
            if match:
                coid = match.group(1)
                display_options = 'a:2:{s:8:"~location~";s:8:"~template~";s:28:"~course_program_display_field~";s:0:"";}'
                from urllib.parse import quote
                encoded_display_options = quote(display_options)
                ajax_url = (
                    f"{step.get('base_url')}?catoid={step.get('catoid')}"
                    f"&coid={coid}&display_options={encoded_display_options}&show"
                )
                yield scrapy.Request(
                    url=ajax_url,
                    callback=self.parse_dynamic_course,
                    meta={'step': step}
                )

        # Next, handle pagination if a pagination selector is provided in the step config.
        # (For example, add "pagination_selector": "css_selector_for_pagination_links" in your config.)
        pagination_selector = step.get("pagination_selector")
        if pagination_selector:
            pagination_links = _select(response, pagination_selector)
            all_page_links = pagination_links.getall() if pagination_links else []
            self.logger.debug(f"DynamicFind: Found {len(all_page_links)} pagination link(s).")
            for link in pagination_links:
                href = link.get()
                if href:
                    abs_url = response.urljoin(href)
                    from .helpers import canonicalize_url  # Ensure canonicalization is imported
                    canonical_url = canonicalize_url(abs_url)
                    if canonical_url not in self.visited_urls:
                        self.visited_urls.add(canonical_url)
                        self.logger.debug(f"DynamicFind: Following pagination URL: {abs_url}")
                        yield scrapy.Request(
                            url=abs_url,
                            callback=lambda r, s=step: self.dynamic_find(r, s)
                        )
                
    def parse_dynamic_course(self, response):
        step = response.meta.get('step')
        fields = step.get('fields', {})
        title_xpath = fields.get('title')
        desc_xpath = fields.get('description')
        from .helpers import _extract_text  # Use our helper for text extraction
        title = _extract_text(response, title_xpath)
        description = _extract_text(response, desc_xpath)
        yield {
            'title': title if title else "No Title Found",
            'description': description if description else "No Description Found",
        }

    def parse_followed_steps(self, response, steps, parent_item):
        if not steps:
            yield parent_item
            return
        step = steps[0]
        action = step.get("type", "").lower()
        if action == "find":
            for item in find(response, step):
                merged = {**parent_item, **item}
                yield from self.parse_followed_steps(response, steps[1:], merged)
        else:
            yield from self.parse_followed_steps(response, steps[1:], parent_item)