#! /usr/bin/python3
from playwright.sync_api import Playwright, sync_playwright
from pathlib import Path
import re
import pandas as pd
from playwright._impl._api_types import Error
from concurrent.futures.thread import ThreadPoolExecutor
import ast
import os
import time

def scrape_gadgets(playwright: Playwright,link, logger):
    """
    Uses Playwright to scrape data from a list of links, specifically
    extracting information about smartphone models, colors, memories, regular prices, and prices for
    clients, and then saves the data to a CSV file.
    :param playwright: The `playwright` parameter is an instance of the Playwright library. It is used
    to launch and control a web browser for web scraping purposes
    :type playwright: Playwright
    """
    data = []
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    try:
        page.goto(link)
        page.get_by_role("button", name="Alle cookies aanvaarden").click(force=True)
    except:
        logger.critical('scrape failure', msg="Page Timeout", type='page', page=link)
        return
    try:
        page.wait_for_selector(".heading--6.heading--nomargin.hardware-product--info__content__configurations-color__label")
        colors = page.locator(".heading--6.heading--nomargin.hardware-product--info__content__configurations-color__label").all()
    except:
        logger.critical('scrape failure', msg="Page Timeout", type='page', page=link)
        return
    if colors:
        for color_element in colors:
            color = color_element.text_content()
            try:
                page.locator("label").filter(has_text = color).check()
            except Error as e:
                logger.warning('scrape failure', type='field',target='color', page=link)
            memories = page.locator(".heading--6.heading--nomargin.hardware-product--info__content__configurations-size__label").all()
            if memories:
                for memory_element in memories:
                    list_of_models = []
                    memory = memory_element.text_content()
                    page.locator("label").filter(has_text = memory).check()
                    page.wait_for_selector(".text-weight--g.hardware-sticky-header__name.mr--s.word-break--ellipsis")
                    product_id = re.findall(r"productId=(\d+)", link)
                    product_id = product_id[0]
                    list_of_models.append(product_id)
                    model = page.query_selector(".text-weight--g.hardware-sticky-header__name.mr--s.word-break--ellipsis").text_content()
                    list_of_models.append(model)
                    list_of_models.append(color)
                    list_of_models.append(memory)
                    price_regular_tag = page.query_selector(".align-self--center.text-decoration--line-through.mr--xs--md")
                    if price_regular_tag:
                        price_regular = price_regular_tag.text_content()
                    else:
                        logger.warning('scrape failure', type='field',target='price_regular', page=link)
                        price_regular = None
                    list_of_models.append(price_regular)
                    price_for_clients = page.query_selector(".heading--nomargin.price--superscript-amount.heading--3").text_content()
                    list_of_models.append(price_for_clients)
                    list_of_models.append(link)
                    data.append(list_of_models)
            else:
                list_of_models = []
                memory = None
                logger.warning('scrape failure', type='field',target='memory', page=link)
                product_id = re.findall(r"productId=(\d+)", link)
                product_id = product_id[0]
                list_of_models.append(product_id)
                model = page.query_selector(".text-weight--g.hardware-sticky-header__name.mr--s.word-break--ellipsis").text_content()
                list_of_models.append(model)
                list_of_models.append(color)
                list_of_models.append(memory)
                price_regular_tag = page.query_selector(".align-self--center.text-decoration--line-through.mr--xs--md")
                if price_regular_tag:
                    price_regular = price_regular_tag.text_content()
                else:
                    logger.warning('scrape failure', type='field',target='price_regular', page=link)
                    price_regular = None
                list_of_models.append(price_regular)
                price_for_clients = page.query_selector(".heading--nomargin.price--superscript-amount.heading--3").text_content()
                list_of_models.append(price_for_clients)
                list_of_models.append(link)
                data.append(list_of_models)
    else:
        list_of_models = []
        memory = None
        logger.warning('scrape failure', type='field',target='memory', page=link)
        color=None
        logger.warning('scrape failure', type='field',target='color', page=link)
        product_id = re.findall(r"productId=(\d+)", link)
        product_id = product_id[0]
        list_of_models.append(product_id)
        model = page.query_selector(".text-weight--g.hardware-sticky-header__name.mr--s.word-break--ellipsis").text_content()
        list_of_models.append(model)
        list_of_models.append(color)
        list_of_models.append(memory)
        price_regular_tag = page.query_selector(".align-self--center.text-decoration--line-through.mr--xs--md")
        if price_regular_tag:
            price_regular = price_regular_tag.text_content()
        else:
            logger.warning('scrape failure', type='field',target='price_regular', page=link)
            price_regular = None
        list_of_models.append(price_regular)
        price_for_clients = page.query_selector(".heading--nomargin.price--superscript-amount.heading--3").text_content()
        list_of_models.append(price_for_clients)
        list_of_models.append(link)
        data.append(list_of_models)

    context.close()
    browser.close()
    return data

def worker(link, logger):
    with sync_playwright() as playwright:
        data=scrape_gadgets(playwright,link, logger)
    return data

def get_devices(links, logger):
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(worker, link, logger) for link in links]
        list_of_watch = []
        for item in futures:
            if item.result():
                list_of_watch.append(item.result())
    smartphones = [item for sublist in list_of_watch for item in sublist]
    return smartphones

def get_urls_from_csv(path, logger):
    all_urls=[]
    df = pd.read_csv(path)
    device_list = df["category"].to_list()
    for device in device_list:
        try:
            device_list_string=df[df["category"]==device]["urls"].to_list()[0]
            device_url_list = ast.literal_eval(device_list_string)
            all_urls.append({"category":device,"urls":device_url_list})
        except:
            logger.warning('scrape failure', type='page',target="links",msg="urls missing")
    return all_urls