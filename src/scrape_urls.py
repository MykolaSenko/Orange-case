#! /usr/bin/python3
""" Copyright 2023 by:
Henrique Rauen Silva Jardim
Bo Cao
Mykola Senko
George Hollingdale
Weiying Zhao

Usage agreements can be achieved by contacting the code owners
"""
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By

def get_page(url, logger):
    """Initializes the connection and clicks the cookie button"""
    opt=webdriver.ChromeOptions()
    opt.add_argument("--headless")
    driver = webdriver.Chrome(options=opt)

    driver.get(url)
    cookie_accept = driver.find_element(By.XPATH,"//button[@ id='onetrust-accept-btn-handler']")
    cookie_accept.click()

    #wait until the whole page is loaded
    try:
        body_xpath = "//head[@class = 'at-element-marker']"
        wait = WebDriverWait(driver, 100)
        wait.until(EC.presence_of_element_located((By.XPATH,body_xpath)))
    except:
        logger.critical('scrape failure', msg="Page Timeout", type='page', page=url)
    return driver

def get_category_links(link, logger):
    """Takes the main page of 'toestellen' and scrape all links to the categories"""
    driver = get_page(link, logger)
    button_xpath = "//a[@class = 'cards--append cards--container cursor--pointer cards--shadow border--all--r border-width--all--r border-color--all--transparant color-text link link--no-underline secondary hardware-categories__items mr--l--sm mb--l--sm mb--s p--m']"
    try:
        #wait until the element is loaded
        wait = WebDriverWait(driver, 100)
        wait.until(EC.presence_of_element_located((By.XPATH,button_xpath)))

        #find all categories of divices in text format
        category_xpath = "//div//a[@ class='cards--append cards--container cursor--pointer cards--shadow border--all--r border-width--all--r border-color--all--transparant color-text link link--no-underline secondary hardware-categories__items mr--l--sm mb--l--sm mb--s p--m']"
        wait.until(EC.presence_of_element_located((By.XPATH,category_xpath)))

        #get the category names
        category_elements= driver.find_elements(By.XPATH,category_xpath)
        category_keys = [element.text for element in category_elements]

        #get the catgory links
        endpoints = [word.replace(' ', '%20') for word in category_keys]
        category_urls = []
        for index, category in enumerate(category_keys):
            url = f"https://www2.telenet.be/residential/nl/toestellen/toestellen-overzicht?intcmp=ToestNav#/category={endpoints[index]}/pageNo=1"
            category_urls.append({"category":category,
                                "url":url})
    except:
        logger.error('scrape failure',type='page',msg="time out", page=link)
    driver.close()
    return category_urls

def get_how_many_pages(url, logger):
    """Checks how many pages are listed under my single page"""
    driver = get_page(url, logger)
    #wait until the element is loaded
    try:
        wait = WebDriverWait(driver, 30)
        wait.until(EC.presence_of_element_located((By.XPATH,"//head[@class = 'at-element-marker']")))
        try:
            wait.until(EC.presence_of_element_located((By.XPATH,"//ul//li[@ class='pagination__list__item in-active ng-star-inserted']")))
            ul = driver.find_elements(By.XPATH,"//ul//li[@ class='pagination__list__item in-active ng-star-inserted']")
            return (len(ul)+1)
        except:
            return 1
    except:
        logger.error('scrape failure',type='page',msg="time out", page=url)

def get_all_urls(device_url, logger):
    page = 1
    total_page = get_how_many_pages(device_url, logger)
    try:
        logger.info('scraping page',page=device_url,amount_pages=total_page)
        total_urls = []

        while page <= total_page:
            current_url = f"{device_url[:-1]}{page}"
            logger.info('scraping page',page=current_url)
            driver = get_page(current_url,logger)

            wait = WebDriverWait(driver, 100)
            wait.until(EC.presence_of_element_located((By.XPATH,"//head[@class = 'at-element-marker']")))

            urls_in_on_page =driver.find_elements(By.XPATH,"//a[@ class='color-dark-brown display--flex flex-direction--column width--full position--full-height']")

            for single_page in urls_in_on_page:
                i = single_page.get_attribute("href")
                # print(f"get this url: {i}")
                total_urls.append(i)
            page += 1
        return(total_urls)
    except:
        logger.critical('scrape failure', msg="Page Timeout", type='page', page=device_url)

if __name__ == "__main__":
    #get the category first , the return result is a list of dictionary:
    import structlog
    logger = structlog.get_logger()
    category_urls = get_category_links("https://www2.telenet.be/residential/nl/toestellen/?intcmp=ToestNav", logger)

    all_devices_urls = []
    for category in category_urls:
        urls = get_all_urls(category['url'], logger)
        all_devices_urls.append({"category":category['category'].replace(" ","_"),"urls":urls})
        df = pd.DataFrame(all_devices_urls)
        df.to_csv("devices_urls.csv")
