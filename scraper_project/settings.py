BOT_NAME = 'scraper_module'

SPIDER_MODULES = ['scraper_module.scraper_project.spiders']
NEWSPIDER_MODULE = 'scraper_module.scraper_project.spiders'

# Crawl responsibly by identifying yourself on the user-agent
# USER_AGENT = 'scraper_module (+http://example.com)'

# Obey robots.txt rules? (Many turn this off to scrape more freely)
ROBOTSTXT_OBEY = True

ITEM_PIPELINES = {
    'scraper_module.scraper_project.pipelines.ScraperModulePipeline': 300,
    'scraper_module.scraper_project.pipelines.JsonWriterPipeline': 300,
}