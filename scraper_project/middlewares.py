# scraper_module/scraper_project/middlewares.py

from scrapy import signals

class ScraperProjectSpiderMiddleware:
    """
    Not activated by default. See settings.py to enable it.
    """

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        """
        Called for each response that goes through the spider
        middleware and into the spider.
        """
        return None  # or raise IgnoreRequest

    def process_spider_output(self, response, result, spider):
        """
        Called with results returned from the Spider.
        """
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        """
        Called when a spider or process_spider_input() method raises an exception.
        """
        pass

    def process_start_requests(self, start_requests, spider):
        """
        Called with the start requests of the spider.
        """
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ScraperProjectDownloaderMiddleware:
    """
    Not activated by default. See settings.py to enable it.
    """

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your downloader middleware.
        s = cls()
        return s

    def process_request(self, request, spider):
        """
        Called for each request that goes through the downloader middleware.
        """
        return None

    def process_response(self, request, response, spider):
        """
        Called with the response returned from the downloader.
        """
        return response

    def process_exception(self, request, exception, spider):
        """
        Called when a download handler or process_request() raises an exception.
        """
        pass
