# scraper_module/scraper_lib/helpers.py
from parsel import Selector
from urllib.parse import urlparse, urlunparse
import logging

logger = logging.getLogger(__name__)

def _select(selector_or_response, selector_str):
    """
    Select elements using either XPath or CSS.
    If the selector_str starts with 'xpath:', use XPath; otherwise, assume CSS.
    """
    if selector_str.startswith("xpath:"):
        expr = selector_str.replace("xpath:", "")
        try:
            return selector_or_response.xpath(expr)
        except Exception as e:
            logger.error(f"XPath expression failed: {expr}. Error: {e}")
            raise
    else:
        try:
            return selector_or_response.css(selector_str)
        except Exception as e:
            logger.error(f"CSS selector failed: {selector_str}. Error: {e}")
            raise

def _extract_text(selector_or_response, selector_str):
    """
    Extract text from the first match or join all matches if 'join' is appended.
    """
    if selector_str.endswith("join"):
        raw_matches = _select(selector_or_response, selector_str.replace("join", "")).getall()
        return " ".join(m.strip() for m in raw_matches if m.strip())
    else:
        raw_matches = _select(selector_or_response, selector_str).getall()
        matches = [m.strip() for m in raw_matches if m.strip()]
        if not matches:
            return None
        return matches[0] if len(matches) == 1 else matches

def find_pages(selector_or_response, step):
    """
    Given a pagination step definition, yield each found pagination URL.
    """
    search_space = step.get("search_space")
    if not ("href" in str(step.get("link_selector"))):
        link_selector = str(step.get("link_selector")) + "/@href"
    else:
        link_selector = step.get("link_selector")
    if not (search_space and link_selector):
        logger.debug("Pagination step missing search_space or link_selector.")
        return []
    seen_urls = set()
    for node in _select(selector_or_response, search_space):
        for ln in _select(node, link_selector):
            href = ln.get()
            if href:
                abs_url = selector_or_response.urljoin(href)
                canonical_url = canonicalize_url(abs_url)
                if canonical_url not in seen_urls:
                    seen_urls.add(canonical_url)
                    logger.debug(f"Found pagination URL: {canonical_url}")
                    yield abs_url


def find(selector_or_response, step):
    """
    Given a 'find' step definition, yield dictionaries representing items.
    """
    search_space = step.get("search_space")
    repeating_selector = step.get("repeating_selector")
    fields = step.get("fields", {})
    parents = _select(selector_or_response, search_space) if search_space else [selector_or_response]
    logger.debug(f"Found {len(parents)} parent(s) using search_space: {search_space}")
    if not parents:
        logger.debug(f"No parents found in {selector_or_response.url} using search_space: {search_space}")

    num_required = step.get("num_required", 0)
    required_fields = list(fields.keys())[:num_required] if num_required > 0 else []
    for p in parents:
        for row in _select(p, repeating_selector):
            item = {field: _extract_text(row, selector) for field, selector in fields.items()}
            if required_fields and any(not item.get(req) for req in required_fields):
                logger.debug(f"Skipping item due to missing required fields: {item}")
                continue
            # Optionally add source URL if available
            if hasattr(selector_or_response, "request"):
                item["source"] = selector_or_response.request.url
            yield item

def canonicalize_url(url):
    """
    Returns a canonical form of the URL by normalizing the path.
    For example, removes a trailing slash (unless the path is just '/').
    """
    parsed = urlparse(url)
    # Normalize the path: remove trailing slash if not the root
    path = parsed.path.rstrip('/')
    if not path:
        path = '/'
    return urlunparse((parsed.scheme, parsed.netloc, path, parsed.params, parsed.query, parsed.fragment))