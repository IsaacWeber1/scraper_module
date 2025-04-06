# scraper_module/scraper_lib/scraper_engine.py
import logging
from scrapy.utils.project import get_project_settings
from .engine_spider import StepSpider
from scrapy.crawler import CrawlerProcess
from typing import List
from scraper_module.config import SpiderConfig
from scrapy import signals
logger = logging.getLogger(__name__)

class ScraperEngine:
    def __init__(self, config: SpiderConfig):
        self.config = config
        self.name = config.name
        self.logger = logger.getChild(self.name)
        self.items_collected: List[dict] = []
        self.seen_items = set()
        self.start_url = config.start_url
        self.playwright = config.use_playwright
        # Convert pagination and tasks from the config to the internal format
        if config.pagination:
            # Create a local pagination dict, setting the 'type' key explicitly.
            pagination_type = type(config.pagination).__name__.lower()
            self.pagination = {**config.pagination.__dict__, "type": pagination_type}
        else:
            self.pagination = None
        # Convert tasks to a list of dicts
        def task_to_dict(task):
            # Use the task's own type name if the task doesn't specify one (or if task.task_type is not set)
            task_type = task.task_type if hasattr(task, "type") and task.type else type(task).__name__.lower()
            # Convert to a dict and inject the computed 'action'
            task_dict = task.__dict__.copy()
            task_dict["type"] = task_type
            return task_dict
        self.steps = [task_to_dict(task) for task in config.tasks]

    def run(self):
        settings = get_project_settings()
        output_file = f"./data_output/{self.name}.json"
        settings.set("FEEDS", {
            output_file: {
                "format": "json",
                "encoding": "utf8",
                "store_empty": False,
                "indent": 4,
                "overwrite": True,
            },
        })
        process = CrawlerProcess(settings)
        crawler = process.create_crawler(StepSpider)
        
        # Define a simple item collector
        def item_collector(item, response, spider):
            self.items_collected.append(item)
        crawler.signals.connect(item_collector, signal=signals.item_scraped)
        process.crawl(crawler,
                      start_url=self.start_url,
                      steps=self.steps,
                      use_playwright=self.playwright,
                      pagination=self.pagination)
        process.start()
        return self.items_collected
    
    def schedule(self, process):
        output_file = f"./data_output/{self.name}.json"
        process.settings.set("FEEDS", {
            output_file: {
                "format": "json",
                "encoding": "utf8",
                "store_empty": False,
                "indent": 4,
                "overwrite": True,
            },
        })

        crawler = process.create_crawler(StepSpider)

        def item_collector(item, response, spider):
            self.items_collected.append(item)

        crawler.signals.connect(item_collector, signal=signals.item_scraped)

        process.crawl(
            crawler,
            start_url=self.start_url,
            steps=self.steps,
            use_playwright=self.playwright,
            pagination=self.pagination,
        )