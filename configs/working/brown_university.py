from scraper_module.config import *

config = SpiderConfig(
    name="brown_university",
    start_url="https://bulletin.brown.edu/",
    use_playwright=False,
    pagination=Search_Links(
        search_space='xpath://div[@id="cl-menu"]/ul[@id="/"]',
        link_selector="xpath:li/a/@href",
        target_page_selector='xpath://div[@id="tabs"]/ul/li[@id="courseinventorytab"]/a/@href' # Target page to scrape
    ),
    tasks=[
        Find(
            task_name="courses",
            search_space='xpath://*[@id="courseinventorycontainer"]/div/div',
            repeating_selector="div",
            fields={
                "title": 'xpath:p[@class="courseblocktitle"]/strong//text()',
                "description": 'xpath:p[@class="courseblockdesc"]//text()join'
            },
            num_required=1
        )
    ]
)