# scraper_module/scraper_lib/scraper_engine.py
import logging
from scrapy.utils.project import get_project_settings
from .engine_spider import StepSpider
from scrapy.crawler import CrawlerProcess
from scrapy import signals

logger = logging.getLogger(__name__)

class ScraperEngine:
    def __init__(self, spider_name=None):
        self.spider_name = spider_name or ""
        self.logger = logger.getChild(self.spider_name)
        self.items_collected = []
        self.pagination = None
        self.steps = []
        self.playwright = False
        self.start_url = None

    def set_url(self, url):
        self.start_url = url

    def set_playwright(self, use_playwright):
        self.playwright = bool(use_playwright)

    def next_page(self, type, search_space, target_page_selector=None, link_selector=None):
        if not (target_page_selector or link_selector):
            raise ValueError("Missing required parameters for next_page.")
        self.pagination = {
            "type": type,
            "search_space": search_space,
            "target_page_selector": target_page_selector,
            "link_selector": link_selector
        }

    def add_task(self, name, action, include=None, search_space=None, repeating_selector=None, fields=None, num_required=0):
        if not action or not name:
            raise ValueError("Both action and name are required for add_task.")
        task = {
            "name": name,
            "action": action,
            "search_space": search_space,
            "repeating_selector": repeating_selector,
            "num_required": num_required,
            "fields": fields or {},
            "include": include,
        }
        self.steps.append(task)

    def run(self):
        settings = get_project_settings()
        # Configure a feed export to a JSON file for this single run.
        output_file = f"./data_output/{self.spider_name}.json"
        settings.set("FEEDS", {
            output_file: {
                "format": "json",
                "encoding": "utf8",
                "store_empty": False,
                "indent": 4,
                "overwrite": True,
            },
        })
        items_collected = []

        def item_collector(item, response, spider):
            items_collected.append(item)

        process = CrawlerProcess(settings)
        crawler = process.create_crawler(StepSpider)
        crawler.signals.connect(item_collector, signal=signals.item_scraped)
        process.crawl(crawler,
                      start_url=self.start_url,
                      steps=self.steps,
                      use_playwright=self.playwright,
                      pagination=self.pagination)
        process.start()
        return items_collected
