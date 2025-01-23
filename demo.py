from scraper_lib.scraper_engine import ScraperEngine

if __name__ == "__main__":
    steps = [
      {
        "name": "find_tracks",
        "action": "find_repeating",
        "search_space": "xpath://h2[contains(text(), 'Featured Tracks')]/../table/tbody",
        "repeating_selector": "tr",
        "fields": {
          "track_name": "xpath:td[@class='track']/a/text()",
          "date_links": "xpath:td[@class='date']/a[@class='dkbluesm']/@href"
        }
      }
    ]
    engine = ScraperEngine()
    items = engine.run(
        url='https://www.equibase.com/static/chart/pdf/index.html?SAP=TN',
        steps=steps,
        use_playwright=True
    )
    print(f"Collected {len(items)} items.")

    print(items)