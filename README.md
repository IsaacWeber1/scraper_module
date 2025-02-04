# Scraper Module

The **Scraper Module** is a modular web scraping framework built on top of [Scrapy](https://scrapy.org/). It is designed to allow rapid development of site-specific spiders through a unified engine that supports configurable tasks, pagination, and optional Playwright integration for dynamic content.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Running All Spiders](#running-all-spiders)
  - [Running a Single Spider](#running-a-single-spider)
- [Adding New Spiders](#adding-new-spiders)
- [Configuration Options](#configuration-options)
  - [Setting the URL and Playwright Mode](#setting-the-url-and-playwright-mode)
  - [Pagination Configuration](#pagination-configuration)
  - [Task/Field Extraction Configuration](#taskfield-extraction-configuration)
- [Project Structure](#project-structure)
- [Extending the Module](#extending-the-module)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Overview

The scraper module is designed to be both reusable and extensible. It allows you to:
- Define site-specific spiders in a simple Python file (in the **spiders/** directory).
- Configure each spider with a start URL, pagination rules, and extraction tasks.
- Use a central runner to execute all spiders (or a single spider) using Scrapy’s asynchronous engine.
- Optionally integrate Playwright for pages that require JavaScript rendering.

## Architecture

The module consists of the following key components:

- **ScraperEngine** (`scraper_module/scraper_lib/scraper_engine.py`):  
  Acts as the central configuration object for a spider. It lets you set the start URL, enable/disable Playwright, define pagination (using `next_page()`), and add extraction tasks (using `add_task()`).

- **EngineSpider** (`scraper_module/scraper_lib/engine_spider.py`):  
  A generic spider that uses the provided engine configuration to drive the scraping process. It supports:
  - Running initial requests (with or without pagination).
  - Recursively following links for pagination.
  - Executing sequential “steps” to extract data.

- **Helpers** (`scraper_module/scraper_lib/helpers.py`):  
  Utility functions for selecting elements (using XPath or CSS), extracting text, and processing pagination links.

- **Runner** (`scraper_module/scraper_lib/runner.py`):  
  Orchestrates multiple scraper engines by launching a single Scrapy `CrawlerProcess` to run all defined spiders. It also collects and saves the output items to JSON files.

## Requirements

- Python 3.7+
- [Scrapy](https://scrapy.org/)
- Optional (if using Playwright integration):
  - [scrapy-playwright](https://github.com/scrapy-plugins/scrapy-playwright)  
  - [Playwright](https://playwright.dev/python/)

Other dependencies include in requirements.txt

## Installation

1. **Clone the repository:**

   Within your project directory, clone the scraper module. (run from outside the module)

   ```bash
   git clone <https://github.com/IsaacWeber1/scraper_module.git>
   cd <scraper_module>

2. **Create and activate a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt

## Usage

   **Running All Spiders**

  New spiders and scripts for running them should be defined outside of the scraper module.
  
  To run all spider engines at once, use a main run script similar to this:
   ```python
   # run.py
   import glob
   import os
   import importlib.util
   from scraper_module.scraper_lib.runner import RunAllEngines

   def import_spider_module(spider_path, spider_name):
       spec = importlib.util.spec_from_file_location(spider_name, spider_path)
       module = importlib.util.module_from_spec(spec)
       spec.loader.exec_module(module)
       return module

   def clean_output():
       # Remove any existing JSON output files
       for file in glob.glob("data_output/*.json"):
           os.remove(file)

   if __name__ == "__main__":
       clean_output()
       # Load spider modules from the 'spiders' directory
       spider_files = glob.glob("spiders/*.py")
       engines = []
       for spider_file in spider_files:
           spider_name = os.path.basename(spider_file).replace(".py", "")
           module = import_spider_module(spider_file, spider_name)
           if hasattr(module, "engine"):
               engine = module.engine
               # Ensure the engine has a spider name set
               if not engine.spider_name:
                   engine.spider_name = spider_name
               engines.append(engine)
        
       # Instantiate and run the orchestrator
       runner = RunAllEngines(
           engines=engines,
           global_settings={
               "LOG_LEVEL": "DEBUG",
               "FEEDS": {}  # Disable built-in feed exports if not needed
           }
       )
       runner.run_all()
       runner.save_all()
   ```

  If you wish to run one spider at a time, you can use a run_single script like this:
   ```python
   # run_single.py
   import os
   import importlib.util
   from scraper_module.scraper_lib.scraper_engine import ScraperEngine

   def import_spider_module(spider_path, spider_name):
       spec = importlib.util.spec_from_file_location(spider_name, spider_path)
       module = importlib.util.module_from_spec(spec)
       spec.loader.exec_module(module)
       return module

   if __name__ == "__main__":
       spider_name = "example_spider"  # Change this to the desired spider's name
       spider_path = os.path.join("spiders", f"{spider_name}.py")
       module = import_spider_module(spider_path, spider_name)
       if hasattr(module, "engine"):
           engine = module.engine
           engine.spider_name = spider_name  # Ensure the spider name is set
           engine.run()  # Run this engine on its own
   ```

