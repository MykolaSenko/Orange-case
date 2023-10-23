# Telenet Web Scraping Project

## Overview
This project involves using Selenium and Playwright to scrape data from telecom providers in general and Telenet.be more specifically. We successfully extracted information about products like internet, mobile and TV packages, promos, and over 570 gadgets available on the website. The Telenet website is dynamic and employs various anti-scraping measures, increasing the challenge of this project.

## Table of Contents
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Challenges](#challenges)
- [Scraping Strategy](#scraping-strategy)

## Requirements
- Python 3.10
- Chrome web browser
- Webdriver for Selenium and Playwright

## Installation
![python version](https://img.shields.io/badge/python-3.10.6+-blue) ![pandas](https://img.shields.io/badge/pandas-green) ![playwright](https://img.shields.io/badge/playwright-orange) ![selenium](https://img.shields.io/badge/selenium-pink) ![structlog](https://img.shields.io/badge/structlog-blue)

1. Clone the project repository to your local machine.
2. Create a virtual environment for the project and activate it:
   ```
   python -m venv venv
   source venv/bin/activate
   ```
3. Install the required Python packages using `pip`:
   ```
   pip install -r local_requirements.txt
   ```
4. Install playwright by following this official documentation: [install playwright](https://playwright.dev/python/docs/intro)

## Usage
The Scraper is split into 2 component parts:
- Dynamic, synchronous and configurable (for more details: [configuration](#configuration))
- Static and multi-threaded (focused on gadgets for telenet)

To run under the default configuration, just run `python main.py`. This will run both scrapers and save the data as csv file on the `data/` folder. This will, in order:

1. Navigate to the Telenet.be website and collect data as specified in the configuration file (defaults: products, packs and promotions). The scraped data will be saved to output csv files and store them in the data folder.

2. Navigate to the subsidized page (toestellen) and scrape all gadgets and their respective prices and attributes (memory, color etc)

Be mindful of the rate at which you make requests to the website to avoid overloading their servers and getting blocked. You may need to implement delays between requests.

## Challenges
The Telenet.be website presents several challenges for web scraping, including but not limited to:
- Dynamic content loaded via JavaScript.
- Frequent changes in the website's structure, which may require updating the scraping code.

## Scraping Strategy
Our scraping strategy involves using Selenium and Playwright to:
- Emulate user interactions to access product listings, promos, and gadgets.
- Extract data from dynamically loaded elements.
- Handle cookies buttons, if encountered.
- Store scraped data for analysis and further use.

## Disclaimer
Please note that web scraping may raise legal and ethical concerns. Ensure that your scraping activities comply with the website's terms of service and applicable laws and regulations. Use this code responsibly and respectfully.

## About us
Weiying Zhao, Data Analyst. <a href = 'https://www.linkedin.com/in/weiying-zhao-a4a307241/'> Linkedin </a>

Bo Cao, Data Engineer. <a href = 'https://www.linkedin.com/in/bo-cao-313ab244'> Linkedin </a>

<a href='https://github.com/henrique-rauen'>Henrique</a>, Data Scientist. <a href='https://www.linkedin.com/in/henrique-rauen/'> Linkedin </a>

Mykola Senko [LinkedIn](https://www.linkedin.com/in/mykola-senko-683510a4/), [GitHub](https://github.com/MykolaSenko)

George Hollingdale, Data Analyst. <a href = 'https://www.linkedin.com/in/george-hollingdale/'> Linkedin </a>, <a href = 'https://github.com/ghollingdale/'>GitHub</a>
