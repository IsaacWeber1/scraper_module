from scraper_module.config import *

config = SpiderConfig(
    name="oregon_state_university",
    start_url="https://catalog.oregonstate.edu/courses/",
    use_playwright=False,
    pagination=Search_Links(
        search_space='xpath://ul[@id="/courses/"]',
        link_selector='xpath:li/a/@href',
        target_page_selector='html',
        max_depth=1
    ),
    tasks=[
        Find(
            task_name="courses",
            search_space='xpath://div[@class="sc_sccoursedescs"]',
            repeating_selector='xpath:div',
            fields={
                'title': 'xpath:h2//text()',
                'description': 'xpath:p//text()join'
            },
            num_required=1
        )
    ]
)