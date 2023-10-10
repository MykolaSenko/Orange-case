#! /usr/bin/python3
from playwright.sync_api import Playwright, sync_playwright
from pathlib import Path
import re
import pandas as pd
from playwright._impl._api_types import Error
from concurrent.futures.thread import ThreadPoolExecutor
import ast

def scrape_gadgets(playwright: Playwright,link):
    """
    The function `scrape_gadgets` uses Playwright to scrape data from a list of links, specifically
    extracting information about smartphone models, colors, memories, regular prices, and prices for
    clients, and then saves the data to a CSV file.
    :param playwright: The `playwright` parameter is an instance of the Playwright library. It is used
    to launch and control a web browser for web scraping purposes
    :type playwright: Playwright
    """
    data = []
    # The code block you provided is a loop that iterates over each link in the `list_of_links` list.
    # For each link, it performs the following actions:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.goto(link)
    page.get_by_role("button", name="Alle cookies aanvaarden").click(force=True)

    try:
        page.wait_for_selector(".heading--6.heading--nomargin.hardware-product--info__content__configurations-color__label")
        colors = page.locator(".heading--6.heading--nomargin.hardware-product--info__content__configurations-color__label").all()
    except:
        print(f"Timeout while trying to open this website:{link}")
        return
    # The code block you provided is a loop that iterates over each color element in the `colors`
    # list. For each color element, it performs the following actions:
    if colors:
        for color_element in colors:
            color = color_element.text_content()
            print(color)
            try:
                page.locator("label").filter(has_text = color).check()
            except Error as e:
                try:
                    page.locator("label").filter(has_text = re.compile(r"^Wit$")).check()
                except:
                    page.locator("label").filter(has_text="Wit(Niet beschikbaar)").check()
            memories = page.locator(".heading--6.heading--nomargin.hardware-product--info__content__configurations-size__label").all()
            # The code block you provided is a loop that iterates over each memory element in the
            # `memories` list. For each memory element, it performs the following actions:
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
                    print(memory)
                    list_of_models.append(memory)
                    price_regular_tag = page.query_selector(".align-self--center.text-decoration--line-through.mr--xs--md")
                    if price_regular_tag:
                        price_regular = price_regular_tag.text_content()
                    else:
                        price_regular = None
                    list_of_models.append(price_regular)
                    price_for_clients = page.query_selector(".heading--nomargin.price--superscript-amount.heading--3").text_content()
                    list_of_models.append(price_for_clients)
                    list_of_models.append(link)
                    data.append(list_of_models)
                # print(list_of_models)
            else:
                list_of_models = []
                memory = None
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
                    price_regular = None
                list_of_models.append(price_regular)
                price_for_clients = page.query_selector(".heading--nomargin.price--superscript-amount.heading--3").text_content()
                list_of_models.append(price_for_clients)
                list_of_models.append(link)
                data.append(list_of_models)
        else:
            list_of_models = []
            memory = None
            color=None
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
                price_regular = None
            list_of_models.append(price_regular)
            price_for_clients = page.query_selector(".heading--nomargin.price--superscript-amount.heading--3").text_content()
            list_of_models.append(price_for_clients)
            list_of_models.append(link)
            data.append(list_of_models)

    context.close()
    browser.close()
    return data

def worker(link):
    with sync_playwright() as playwright:
        data=scrape_gadgets(playwright,link)
    return data

def get_devices(links):
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(worker, link) for link in links]
        list_of_watch = []
        for item in futures:
            if item.result():
                list_of_watch.append(item.result())
    smartphones = [item for sublist in list_of_watch for item in sublist]
    return smartphones

def get_urls_from_csv(path):
    all_urls=[]
    df = pd.read_csv(path)
    device_list = df["category"].to_list()
    for device in device_list:
        device_list_string=df[df["category"]==device]["urls"].to_list()[0]
        device_url_list = ast.literal_eval(device_list_string)
        all_urls.append({"category":device,"urls":device_url_list})
    return all_urls

if __name__ == "__main__":
    all_urls=get_urls_from_csv("data_scraped/all_devices_urls.csv")


    for i in all_urls:
        device = i["category"]
        device_url_list = i["urls"]
        df = pd.DataFrame(get_devices(device_url_list),columns=['product_id', 'model', 'color', 'memory', 'price_regular', 'price_for_clients', 'link'])
        df.to_csv(f"data_scraped/{device}.csv")
