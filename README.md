# Scraper Module

The **Scraper Module** is a highly modular web scraping framework built on [Scrapy](https://scrapy.org/). It simplifies the development of site-specific scrapers by introducing **structured configurations**, **pagination handling**, and **optional Playwright integration** for dynamic content.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Setting Up the Framework](#setting-up-the-framework)
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
- **Dynamic Configuration System**: Define spiders using structured Python configuration files.
- **Modular Task Execution**: Supports **Find**, **Follow**, and **Pagination** operations.
- **Efficient Pagination Handling**: Automatically handles **recursive and link-based pagination**.
- **Playwright Integration**: Enables scraping of **JavaScript-heavy websites** when needed.
- **Duplicate Prevention & Canonicalization**: Avoids redundant requests and improves efficiency.

## Architecture

The module consists of the following key components:

- **ScraperEngine** (`scraper_module/scraper_lib/scraper_engine.py`):  
  Configures and initializes each scraper from a structured configuration.

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

1. **Clone the repository:**

   The Scraper Module is meant to be a reusable framework that plugs into your own project.

   ```bash
   git clone https://github.com/IsaacWeber1/scraper_module.git
   ```

2. **Integrate the framework into your project:**

   Place the `scraper_module/` directory in your project folder. The directory structure for your project should look something like this:
   ```
   your_project/
   ├── scraper_module/       # Cloned Scraper Module framework
   ├── configs/              # Your spider configurations (you create this folder)
   ├── run.py                # Main script to orchestrate spiders (you create this file)
   ├── data_output/          # Folder for scraped data (you create this folder)
   └── ...                   # Other project files
   ```

3. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r scraper_module/requirements.txt
   ```

## Usage

### Setting Up the Framework

1. **Create the `configs/` folder**:
   This folder will contain the configuration files for your scrapers. Each scraper should have its own configuration file written in Python.

   Example working configuration file (`configs/brown_university.py`):
   ```python
   from scraper_module.config import *

   config = SpiderConfig(
       name="brown_university",
       start_url="https://bulletin.brown.edu/",
       use_playwright=False,
       pagination=Search_Links(
           search_space='xpath://div[@id="cl-menu"]/ul[@id="/"]',
           link_selector="xpath:li/a/@href",
           target_page_selector='xpath://div[@id="tabs"]/ul/li[@id="courseinventorytab"]/a/@href' # Target page to scrape
       ),
       tasks=[
           Find(
               task_name="courses",
               search_space='xpath://*[@id="courseinventorycontainer"]/div/div',
               repeating_selector="div",
               fields={
                   "title": 'xpath:p[@class="courseblocktitle"]/strong//text()',
                   "description": 'xpath:p[@class="courseblockdesc"]//text()join'
               },
               num_required=1
           )
       ]
   )
   ```

2. **Create the `run.py` file**:
   This script orchestrates the execution of all spiders.
   ```python
   import glob
   import importlib.util
   from scraper_module.scraper_lib.runner import RunAllEngines
   from scraper_module.scraper_lib.scraper_engine import ScraperEngine

   def clean_output():
       # Remove any existing JSON output files to start fresh.
       for file in glob.glob("data_output/*.json"):
           os.remove(file)

   EXCLUDE_ENGINES = {"example_exclude"} # For testing purposes

   if __name__ == "__main__":
       clean_output()
       config_files = [
           file for file in glob.glob("configs/*.py")
           if os.path.basename(file).replace(".py", "") not in EXCLUDE_ENGINES
       ]

       engines = []
       for config_file in config_files:
           spec = importlib.util.spec_from_file_location(
               "config", config_file
           )
           module = importlib.util.module_from_spec(spec)
           spec.loader.exec_module(module)
           engines.append(ScraperEngine(module.config))

       runner = RunAllEngines(engines=engines)
       runner.run_all()
       runner.save_all()
   ```

3. **Create the `data_output/` folder**:
   This folder will store the JSON output files generated by your spiders.

### Running All Spiders

To execute all spiders defined in the `configs/` folder, run:
```bash
python run.py
```

### Running a Single Spider
To run a specific spider programmatically:
```python
from scraper_module.scraper_lib.scraper_engine import ScraperEngine
from configs.example_university import config

engine = ScraperEngine(config)
engine.run()
```

## Adding New Scrapers

1. **Create a new config file** in `configs/` (e.g., `configs/new_university.py`).
2. Define the scraper tasks and pagination in the config file using `SpiderConfig`.
3. Add your scraper configuration file to the `configs/` folder. 
4. Run the framework (`python run.py`).

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
your_project/
│── run.py                  # Orchestrates spider execution
│── configs/                # Configuration files for spiders
│   ├── example_spider.py
│── scraper_module/         # Imported scraping framework
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
