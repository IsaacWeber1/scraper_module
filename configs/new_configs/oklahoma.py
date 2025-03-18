from scraper_module.config import *

config = SpiderConfig(
    name="oklahoma",
    start_url="http://catalog.okstate.edu/courses/",
    use_playwright=False,
    pagination=Search_Links(
        search_space='xpath://*[@id="/courses/"]',
        link_selector='xpath:/li/a/@href',
        target_page_selector='html', # Target page to scrape
        max_depth = 1
    ),
    tasks=[
        Find(
            task_name="courses",
            search_space='xpath://div[@class="sc_sccoursedescs"]',
            repeating_selector="div",
            fields={
                "title": 'xpath:p[@class="courseblocktitle noindent"]/strong//text()',
                "description": 'xpath:p[@class="courseblockdesc noindent"]//text()join'
            },
            num_required=1
        )
    ]
)