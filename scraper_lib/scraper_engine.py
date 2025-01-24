# scraper_module/scraper_lib/scraper_engine.py

import logging
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy import signals

from .engine_spider import StepSpider

class ScraperEngine:
    def __init__(self, settings=None):
        if settings is None:
            settings = get_project_settings()
        self.settings = settings
        self.process = CrawlerProcess(self.settings)
        self.logger = logging.getLogger(__name__)

    def run(self, url, steps, use_playwright=False, pagination=None):
        """
        Launch the StepSpider with the given url and steps.
        Blocks until scraping finishes.
        Returns a list of all items scraped (optional).
        """
        # We'll store items in a simple collector
        items_collected = []

        def _item_collector(item, response, spider):
            items_collected.append(item)

        # 1) Create a crawler for our StepSpider
        crawler = self.process.create_crawler(StepSpider)

        # 2) Connect the item_scraped signal on this crawler
        crawler.signals.connect(_item_collector, signal=signals.item_scraped)

        # 3) Schedule the spider to run with our custom arguments
        self.process.crawl(
            crawler,
            start_url=url,
            steps=steps,
            use_playwright=use_playwright,
            pagination=pagination
        )

        self.logger.info("Starting crawl.")
        # 4) Start the reactor (blocking)
        self.process.start()
        self.logger.info("Crawl finished.")
        return items_collected
