from scraper_module.config import *

config = SpiderConfig(
    name="rice",
    start_url="https://ga.rice.edu/programs-study/courses/",
    use_playwright=False,
    pagination=Search_Links(
        search_space='xpath://*[@id="textcontainer"]',
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
                "title": 'xpath:p[@class="courseblocktitle"]/strong//text()',
                "description": 'xpath:p[@class="courseblockdesc  noindent"]//text()join'
            },
            num_required=1
        )
    ]
)