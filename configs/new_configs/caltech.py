from scraper_module.config import *

config = SpiderConfig(
    name="caltech",
    start_url="https://www.catalog.caltech.edu/",
    use_playwright=False,
    pagination=Search_Links(
        search_space='xpath://*[@id="sidebar-menu-block-44778"]',
        link_selector='xpath:/li/div/a/@href',
        target_page_selector='html', # Target page to scrape
        max_depth = 1
    ),
    tasks=[
        Find(
            task_name="courses",
            search_space='xpath://div[@class="left-sidebar-block__content grid-item col-sm-8 pb-5 pb-sm-0 js-sidebar-content"]',
            repeating_selector="div",
            fields={
                "title": 'xpath:h2//text()',
                "description": 'xpath:div[@class="course-description2__description course-description2__general-text"]//text()join'
            },
            num_required=1
        )
    ]
)