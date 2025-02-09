# scraper_module/config.py
from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass(kw_only=True)
class _DefaultConfig:
    type: str = None

@dataclass
class PaginationConfig:
    search_space: str              # Selector to limit pagination container

@dataclass
class Listed_Links(PaginationConfig, _DefaultConfig):
    link_selector: str             # Selector for pagination links

@dataclass
class Search_Links(PaginationConfig, _DefaultConfig):
    link_selector: str             # Selector for pagination links
    target_page_selector: str      # Selector for target page links

@dataclass
class TaskConfig:
    # Consider removing the default to avoid ordering issues
    task_name: str

@dataclass
class Find(TaskConfig, _DefaultConfig):
    search_space: str              # Selector for the container of data
    repeating_selector: str        # Selector for repeating elements
    fields: Dict[str, str]         # Mapping of field names to selectors
    num_required: int = 0
    include: Optional[Dict[str, str]] = None

@dataclass
class Follow(_DefaultConfig, TaskConfig):
    link_field: str                # Field containing the link to follow
    fields: Dict[str, str]         # Mapping of field names to selectors

@dataclass
class SpiderConfig:
    name: str
    start_url: str
    use_playwright: bool = False
    pagination: Optional[PaginationConfig] = None
    tasks: List[TaskConfig] = field(default_factory=list)
