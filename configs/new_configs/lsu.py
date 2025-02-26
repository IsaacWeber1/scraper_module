from scraper_module.config import *

config = SpiderConfig(
    name="lsu_university",
    start_url="https://catalog.lsu.edu/",
    use_playwright=False,
    pagination=Search_Links(
        search_space='xpath://ul[@class="nav level1"]',
        link_selector="xpath:li/a/@href",
        target_page_selector='xpath://div[@class="tab_content"]//a[contains(text(), "Courses")]/@href'  # Target page to scrape
    ),
    tasks=[
        Find(
            task_name="courses",
            search_space='xpath://div[@class="courseblock"]',
            repeating_selector="div",
            fields={
            "title": 'xpath:p[@class="courseblocktitle"]//text()',
                "description": 'xpath:p[@class="courseblockdesc"]//text()join'
            },
            num_required=1
        )
    ]
)