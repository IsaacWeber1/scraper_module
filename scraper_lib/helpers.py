# scraper_module/scraper_lib/helpers.py

from parsel import Selector

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
    Extract the text/attr from the *first* match of selector_str.
    """
    matches = _select(selector_or_response, selector_str)
    return matches.get()  # parsel's .get() returns first match or None

def find_repeating(selector_or_response, step):
    """
    Interprets a single step that looks like:

      {
        "action": "find_repeating",
        "search_space": "...",
        "repeating_selector": "...",
        "fields": {
          "track_name": "xpath:td[@class='track']/a/text()",
          "date_links": "xpath:td[@class='date']/a[@class='dkbluesm']/@href"
        }
      }

    Yields a dict for each 'repeating_selector' item.
    """
    # 1) Narrow the initial selector to "search_space" if provided
    search_space = step.get("search_space")
    if search_space:
        parent = _select(selector_or_response, search_space)
    else:
        parent = [selector_or_response]  # treat the entire doc as parent

    repeating_sel = step["repeating_selector"]
    fields = step["fields"]

    for p in parent:
        # For each "parent" node, find the repeated items
        rows = _select(p, repeating_sel)
        for row in rows:
            item = {}
            # Extract each field by its selector
            for field_name, field_selector in fields.items():
                item[field_name] = _extract_text(row, field_selector)
            yield item
