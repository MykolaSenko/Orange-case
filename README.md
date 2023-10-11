# Telenet Web Scraping Project

## Overview
This project involves using Selenium and Playwright to scrape data from the Telenet.be website. We successfully extracted information about products like internet, mobile and TV packages, promos, and over 570 gadgets available on the website. The Telenet website is dynamic and employs various anti-scraping measures, making this project challenging.

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
- requirements.txt

## Installation
1. Clone the project repository to your local machine.
2. Create a virtual environment for the project and activate it:
   ```
   python -m venv venv
   source venv/bin/activate
   ```
3. Install the required Python packages using `pip`:
   ```
   pip install -r requirements.txt
   ```
4. Install playwright by following this official documentation: [install playwright](https://playwright.dev/python/docs/intro)

## Usage
1. Configure the scraping parameters in the `config.py` file. This includes specifying the URL to scrape, selectors for the different elements, and any other settings required for your scraping tasks. You can skip this step if you just need to scrape telenet.

2. Run the scraper using the main script:
   ```
   python main.py
   ```

3. The scraper will navigate the Telenet.be website and collect data as specified in the configuration file. The scraped data will be saved to output csv files and store them in the data folder.

4. Be mindful of the rate at which you make requests to the website to avoid overloading their servers and getting blocked. You may need to implement delays between requests.

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
Ying

Bo Cao, Data Engineer. <a href = 'https://www.linkedin.com/in/bo-cao-313ab244'> Linkedin </a>

Henrique

Mykola

George Hollingdale, Data Analyst. <a href = 'https://www.linkedin.com/in/george-hollingdale/'> Linkedin </a> & <a href = 'https://github.com/ghollingdale/'> GitHub </a>
