# Scraper Module

The **Scraper Module** is a highly modular web scraping framework built on [Scrapy](https://scrapy.org/). It simplifies the development of site-specific scrapers by introducing **structured configurations**, **pagination handling**, and **optional Playwright integration** for dynamic content.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Running All Spiders](#running-all-spiders)
  - [Running a Single Spider](#running-a-single-spider)
- [Adding New Scrapers](#adding-new-scrapers)
- [Configuration System](#configuration-system)
- [Pagination & Task Configuration](#pagination--task-configuration)
- [Project Structure](#project-structure)
- [License](#license)

## Overview

The **Scraper Module** is designed for **scalability, reusability, and ease of use**.

### **Key Features:**
- **Dynamic Configuration System**: Define spiders using structured Python configuration files (`configs/`).
- **Modular Task Execution**: Supports **Find**, **Follow**, and **Pagination** operations.
- **Efficient Pagination Handling**: Automatically handles **recursive and link-based pagination**.
- **Playwright Integration**: Enables scraping of **JavaScript-heavy websites** when needed.
- **Duplicate Prevention & Canonicalization**: Avoids redundant requests and improves efficiency.

## Architecture

The module consists of the following key components:

- **ScraperEngine** (`scraper_module/scraper_lib/scraper_engine.py`):  
  Configures and initializes each scraper from the **configuration system** (`configs/`).

- **StepSpider** (`scraper_module/scraper_lib/engine_spider.py`):  
  The Scrapy-based spider that executes configured tasks (Find, Follow) and handles pagination.

- **RunAllEngines** (`scraper_module/scraper_lib/runner.py`):  
  Orchestrates multiple scrapers and ensures **efficient execution** with duplicate filtering.

- **Helper Functions** (`scraper_module/scraper_lib/helpers.py`):  
  Includes **URL canonicalization**, XPath/CSS selection, and pagination utilities.

## Requirements

- Python 3.7+
- [Scrapy](https://scrapy.org/)
- Optional (for Playwright integration):
  - [scrapy-playwright](https://github.com/scrapy-plugins/scrapy-playwright)
  - [Playwright](https://playwright.dev/python/)

Install dependencies from `requirements.txt`.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/IsaacWeber1/scraper_module.git
   cd scraper_module
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### **Running All Spiders**
Run all configured scrapers using:
```bash
python run.py
```
This script:
- Loads **spider configurations** from `configs/`
- Filters out **excluded spiders** (e.g., long-running scrapers)
- Runs all **enabled spiders in parallel**

### **Running a Single Spider**
To run a specific spider:
```python
from scraper_module.scraper_lib.scraper_engine import ScraperEngine
from configs.brown_university import config

engine = ScraperEngine(config)
engine.run()
```

## Adding New Scrapers

1. **Create a new config file** in `configs/` (e.g., `configs/example_university.py`).
2. **Define the scraper using `SpiderConfig`**:
   ```python
   from scraper_module.config import *

   config = SpiderConfig(
       name="example_university",
       start_url="https://example.edu/courses",
       use_playwright=False,
       pagination=Search_Links(
           search_space='xpath://div[@class="pagination"]',
           link_selector="xpath:a/@href",
           target_page_selector='xpath://a[contains(text(), "Next")]/@href'
       ),
       tasks=[
           Find(
               task_name="courses",
               search_space='xpath://div[@class="course-list"]',
               repeating_selector="div",
               fields={
                   "title": 'xpath:h2/text()',
                   "description": 'xpath:p[@class="summary"]//text()join'
               },
               num_required=1
           )
       ]
   )
   ```

3. **Run the scraper**:
   ```bash
   python run.py
   ```

## Configuration System

Each scraper is **fully configurable** using `SpiderConfig`. Below are the available configuration options:

### **SpiderConfig**
| Parameter       | Type                   | Description                         |
|-----------------|------------------------|-------------------------------------|
| `name`          | `str`                  | Unique name for the scraper         |
| `start_url`     | `str`                  | URL where scraping starts           |
| `use_playwright`| `bool`                 | Enable Playwright for JavaScript-heavy sites |
| `pagination`    | `PaginationConfig`     | Defines pagination strategy         |
| `tasks`         | `List[TaskConfig]`     | Defines what data to extract        |

### **Pagination & Task Configuration**

#### **Pagination Types**
| Type           | Description                       |
|----------------|-----------------------------------|
| `Search_Links` | Finds and follows links dynamically |
| `Listed_Links` | Uses a predefined list of pagination links |

#### **Task Types**
| Type           | Description                       |
|----------------|-----------------------------------|
| `Find`         | Extracts structured data using XPath/CSS |
| `Follow`       | Follows links and extracts additional fields |

Example `Find` task:
```python
Find(
    task_name="courses",
    search_space='xpath://div[@class="course-list"]',
    repeating_selector="div",
    fields={
        "title": 'xpath:h2/text()',
        "description": 'xpath:p[@class="summary"]//text()join'
    },
    num_required=1
)
```

## Project Structure

```
scraper_module/
│── run.py                  # Runs all scrapers
│── configs/                 # Configuration files for spiders
│   ├── example_university.py
│   ├── brown_university.py
│── scraper_module/
│   ├── config.py            # Dataclasses for scraper configs
│   ├── scraper_lib/
│   │   ├── runner.py        # Runs multiple scrapers
│   │   ├── scraper_engine.py # Handles spider execution
│   │   ├── engine_spider.py  # Core Scrapy spider
│   │   ├── helpers.py       # Utility functions
│── data_output/             # Scraped data output
```

## License

This project is released under the **MIT License**.
