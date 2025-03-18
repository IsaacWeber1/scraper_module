from scraper_module.config import *

config = SpiderConfig(
    name="ncsu",
    start_url="https://catalog.ncsu.edu/course-descriptions/",
    use_playwright=False,
    pagination=Search_Links(
        search_space='xpath://*[@id="textcontainer"]/div',
        link_selector='xpath:/ul/li/a/@href',
        target_page_selector='html', # Target page to scrape
        max_depth = 1
    ),
    tasks=[
        Find(
            task_name="courses",
            search_space='xpath://div[@class="sc_sccoursedescs"]',
            repeating_selector="div",
            fields={
                "title": 'xpath:span[@class="text detail-title margin--tiny text--semibold"]/strong//text()',
                "description": 'xpath://div[@class="noindent"]/p[@class="courseblockextra"]//text()join'
            },
            num_required=1
        )
    ]
)