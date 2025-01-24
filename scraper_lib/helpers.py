# scraper_module/scraper_lib/helpers.py

from parsel import Selector
import logging

logger = logging.getLogger(__name__)

def _select(selector_or_response, selector_str):
    """
    Generic function to select nodes by either
    CSS or XPath. If selector_str starts with 'xpath:',
    we do an XPath. Else we do CSS.
    """
    if selector_str.startswith('xpath:'):
        expr = selector_str.replace('xpath:', '')
        return selector_or_response.xpath(expr)
    else:
        return selector_or_response.css(selector_str)

def _extract_text(selector_or_response, selector_str):
    """
    Extract the text/attr from the *first* match of selector_str,
    *or* return a list if multiple non-blank matches.

    1. We grab all matches (via getall()).
    2. We strip whitespace and remove empty strings.
    3. If zero remain, return None.
    4. If exactly one remains, return that string.
    5. If more, return the entire list.
    """
    raw_matches = _select(selector_or_response, selector_str).getall()

    # Strip each match and remove empties
    matches = [m.strip() for m in raw_matches if m.strip()]

    if not matches:
        return None
    if len(matches) == 1:
        return matches[0]
    return matches

def find_pages(selector_or_response, step):
    """
    For pagination steps like:
    {
        "action": "pagination",
        "type": "link_iterator",
        "search_space": "...",
        "link_selector": "..."
    }

    Yields a URL for each page found.
    """
    search_space = step.get("search_space")
    link_selector = step.get("link_selector")

    # 1) Narrow down to the search space, which might return multiple nodes
    parent_nodes = _select(selector_or_response, search_space)
    if not parent_nodes:
        logger.debug(f"No parent nodes found with search_space: {search_space}")

    for node in parent_nodes:
        # 2) For each node in the search space, select the links
        link_nodes = _select(node, link_selector)
        if not link_nodes:
            logger.debug(f"No link nodes found with link_selector: {link_selector} within search_space: {search_space}")

        for ln in link_nodes:
            # Since link_selector is "xpath:li/a/@href", ln.get() should return the href
            href = ln.get()
            if href:
                logger.debug(f"Found pagination URL: {href}")
                yield href
            else:
                logger.debug("Found pagination link with no href.")

def find_repeating(selector_or_response, step):
    """
    Example step:
    {
      "action": "find_repeating",
      "search_space": "...",
      "repeating_selector": "...",
      "fields": {
         "title": "a strong::text",
         "description": "xpath:br/following-sibling::text()"
      },
      "num_required": 1
    }

    Yields a dict for each repeated element, ensuring that the required fields are present.
    """
    search_space = step.get("search_space")
    repeating_sel = step["repeating_selector"]
    fields = step["fields"]

    # If there's a search_space, select it; otherwise treat the entire response as parent
    if search_space:
        parents = _select(selector_or_response, search_space)
    else:
        parents = [selector_or_response]

    # Number of required fields from the start
    num_required = step.get("num_required", 0)
    if num_required > 0:
        field_list = list(fields.keys())
        required_fields = field_list[:num_required]
    else:
        required_fields = []

    for p in parents:
        # For each parent node, find repeated elements
        rows = _select(p, repeating_sel)
        if not rows:
            logger.debug(f"No rows found with repeating_selector: {repeating_sel} within search_space: {search_space}")

        for row in rows:
            item = {}
            # Extract each field by its selector
            for field_name, field_selector in fields.items():
                item[field_name] = _extract_text(row, field_selector)

            # If we have required_fields, skip the item if any required field is empty
            if required_fields:
                if any(not item.get(req) for req in required_fields):
                    logger.debug(f"Skipping item due to missing required fields: {item}")
                    continue  # Skip this item

            yield item
