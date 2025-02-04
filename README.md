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

- **Sample Spiders** (`spiders/*.py`):  
  Example spider definitions for various sites (e.g., `boston_university.py`, `brown_university.py`, `texas_am_university.py`) that demonstrate how to configure the engine for each site.

## Requirements

- Python 3.7+
- [Scrapy](https://scrapy.org/)
- Optional (if using Playwright integration):
  - [scrapy-playwright](https://github.com/scrapy-plugins/scrapy-playwright)  
  - [Playwright](https://playwright.dev/python/)

Other dependencies include standard libraries such as `glob`, `os`, and `importlib`.

## Installation

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd <repository-directory>
