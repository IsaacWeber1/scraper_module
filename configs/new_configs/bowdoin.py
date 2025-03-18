from scraper_module.config import *

config = SpiderConfig(
    name="bowdoin",
    start_url="https://bowdoin-public.courseleaf.com/courses/",
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
                "title": 'xpath:p[@class="cols courseblocktitle noindent"]//text()join',
                "description": 'xpath:div[@class="noindent"]/p[@class="courseblockdesc noindent"]//text()join'
            },
            num_required=1
        )
    ]
)