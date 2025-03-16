# Scraper Module Structure

The scraper module is designed with a modular architecture so that team members can work on specific parts independently. Although this requires a bit more upfront effort, it greatly reduces refactoring later and minimizes the impact of changes on other parts of the system.

## `run.py` _(High-Level Execution)_
- **Purpose:** This is the entry point for the entire scraping process. It’s located outside the scraper module.
- **Usage:** It calls the `runner.py` class to run the scrapers.
- **Note:** You should only interact with the module through `runner.py` at this level.

## `runner.py` _(Orchestration & Aggregation)_
- **Purpose:** Orchestrates the execution of multiple scrapers (engines) and handles overall process control.
- **Usage:** Sets up the Scrapy process, collects items from each engine, and saves aggregated results.

## `scraper_engine.py` _(Scraper Configuration & Execution)_
- **Purpose:** Translates the user-defined `SpiderConfig` into steps that the Scrapy spider can execute.
- **Usage:** Initializes and runs the main spider (`StepSpider`) with the appropriate settings and tasks.

## `engine_spider.py` _(Core Scrapy Spider)_
- **Purpose:** Implements the `StepSpider` class, which handles the actual crawling.
- **Usage:** Manages requests (including pagination and Playwright integration for dynamic content) and processes each defined task (e.g., find, follow, click).
- **Note:** This is where the core logic of your scraping – like pagination handling and element extraction – takes place.

## `config.py` _(Scraper Configuration Definitions)_
- **Purpose:** Defines the data classes and types (like `Find`, `Follow`, and `PaginationConfig`) for configuring the scrapers.
- **Usage:** Provides a structured way to define scraper behavior that is both reusable and easy to update.

## `helpers.py` _(Utility Functions)_
- **Purpose:** Contains utility functions for common tasks such as element selection, text extraction, and URL normalization.
- **Usage:** Keeps the core spider code clean and DRY (Don’t Repeat Yourself) by centralizing reusable logic.

