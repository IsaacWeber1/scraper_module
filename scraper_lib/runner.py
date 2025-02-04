# scraper_module/scraper_lib/runner.py
import logging
import json
from scrapy.crawler import CrawlerProcess
from scrapy import signals
from .engine_spider import StepSpider

logger = logging.getLogger(__name__)

class RunAllEngines:
    """
    Orchestrates multiple ScraperEngine instances using a single CrawlerProcess.
    """
    def __init__(self, engines, global_settings=None):
        self.engines = engines
        self.global_settings = global_settings or {}
        self.logger = logger

    def run_all(self):
        process = CrawlerProcess(self.global_settings)
        for engine in self.engines:
            if not engine.start_url:
                raise ValueError(f"Engine '{engine.spider_name}' has no start_url set.")
            crawler = process.create_crawler(StepSpider)

            def item_collector(item, response, spider, this_engine=engine):
                this_engine.logger.debug(f"{this_engine.spider_name} scraped item: {item}")
                this_engine.items_collected.append(item)

            crawler.signals.connect(item_collector, signal=signals.item_scraped)
            process.crawl(crawler,
                          start_url=engine.start_url,
                          steps=engine.steps,
                          use_playwright=engine.playwright,
                          pagination=engine.pagination)
        self.logger.info("Starting all spiders...")
        process.start()  # Blocking until all spiders finish.
        return {engine.spider_name: engine.items_collected for engine in self.engines}

    def save_all(self, output_folder="./data_output"):
        for engine in self.engines:
            fname = f"{engine.spider_name}_out.json"
            path = f"{output_folder}/{fname}"
            self.logger.info(f"Saving {len(engine.items_collected)} items to {path}")
            with open(path, "w", encoding="utf8") as f:
                json.dump(engine.items_collected, f, indent=4, ensure_ascii=False)
