from scraper_module.config import *

config = SpiderConfig(
    name="appstate",
    start_url="https://bulletin.appstate.edu/content.php?catoid=34&navoid=2104",
    use_playwright=False,
    tasks=[
        DynamicFind(
            task_name="dynamic_courses",
            search_space='xpath://a[contains(@href, "preview_course_nopop.php")]',
            base_url="https://bulletin.appstate.edu/ajax/preview_course.php",
            catoid=34,
            fields={
                "title": 'xpath://h3//text()join',
                "description": 'xpath://div[2]/text()[3]join'
            }
        )
    ]
)