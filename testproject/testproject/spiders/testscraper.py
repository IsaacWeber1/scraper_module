import scrapy
import re
from urllib.parse import quote

class DynamicCourseSpider(scrapy.Spider):
    name = 'dynamic_course_spider'
    base_url = 'https://bulletin.appstate.edu/ajax/preview_course.php'
    catoid = 34

    def start_requests(self):
        # Start by sending a request to the main course catalog page.
        yield scrapy.Request(url="https://bulletin.appstate.edu/content.php?catoid=34&navoid=2104", callback=self.parse_catalog)

    def parse_catalog(self, response):
        # Extract all course links from the catalog page.
        course_links = response.xpath('//a[contains(@href, "preview_course_nopop.php")]/@href').getall()
        self.logger.debug(f"Found {len(course_links)} course links.")
        
        for link in course_links:
            # Extract the course ID using regex.
            match = re.search(r'coid=(\d+)', link)
            if match:
                coid = match.group(1)
                # Build the AJAX URL dynamically.
                display_options = 'a:2:{s:8:"~location~";s:8:"~template~";s:28:"~course_program_display_field~";s:0:"";}'
                encoded_display_options = quote(display_options)
                ajax_url = f"{self.base_url}?catoid={self.catoid}&coid={coid}&display_options={encoded_display_options}&show"
                yield scrapy.Request(url=ajax_url, callback=self.parse_course)

    def parse_course(self, response):
        # Extract course details.
        title = response.xpath('//h3/text()').get()
        description = response.xpath("//div[2]/text()[3]").get()
        yield {
            'title': title if title else "No Title Found",
            'description': description if description else "No Description Found",
        }