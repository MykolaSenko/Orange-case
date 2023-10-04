#! /usr/bin/python3

#Created by Henrique Rauen (rickgithub@hsj.email)
import asyncio
import time
import re
import pandas as pd
from playwright.sync_api import sync_playwright, Route, expect

def start_navigation(url="https://www2.telenet.be/residential/nl"):
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=False)
        context=browser.new_context()
        page=context.new_page()
        page.goto(url)
        objs=(page.locator('a.useful-links__link')
                    .all())
        results = []
        for obj in objs:
            link="https://www2.telenet.be"
            link +=obj.get_attribute('href')
            link = link.split("?")[0]
            options = ['internet', 'mobiel', 'tv']
            contains = sum([option in link for option in options])
            if contains >= 1:
                print(link)
                pack = False
                if contains > 1:
                    pack=True
                    ret = scrape_packs(context,link,pack)
            results.extend(ret)
        df = pd.DataFrame(results)
        df.to_csv("sample.csv")
        browser.close()

def scrape_packs(context,link,pack):
        scrape_tag=".cmp-product-summary"
        sublink_tag="a:has-text('Meer Info')"
        page=context.new_page()
        page.goto(link)
        #Makes sure price is loaded
        expect(page.locator('.promo-highlight__third-row'))
        summaries=page.query_selector_all(scrape_tag)
        results = []
        for summary in summaries:
            if summary.query_selector(sublink_tag):
                target=summary.query_selector(sublink_tag) #.locator(sublink_tag)
                target =target.get_attribute('href')
                ret = scrape_more_info(context, target)
                ret["link"] = target
            else:
                ret = scrape_summary_page(summary,link)
                ret["link"] = link
            ret["Type"] = "Pack" if pack else "Product"
            results.append(ret)
        page.close()
        return results

def scrape_summary_page(summary,link):
    ret ={}
    print(f"SUMMARY from page: {link}")
    #expect(summary.locator('.promo-highlight__third-row'))
    title_el=summary.query_selector('.text-align--left')
    if title_el:
        title=title_el.inner_text()
        print("Title: ",title)
        ret["title"] = title
    desc_el=summary.query_selector('.cmp-text__listing--primary-ticks')
    if desc_el:
        desc=desc_el.inner_text()
        print("Desc: ",desc)
        ret["desc"] = desc
    price_el=summary.query_selector('.promo-highlight__third-row')
    if price_el:
        price=price_el.inner_text()
        print("Price: ",price)
        ret["nominal_price"] = price
    # Check for discount duration
    duration_el=summary.query_selector('span.duration-month')
    if duration_el:
        duration =duration_el.inner_text()
        duration = re.findall(r'\d+', duration)[0]
        price_after_duration=summary.query_selector('.promo-highlight__second-row').inner_text()
        print("Duration: ",duration)
        print("Price after: ",price_after_duration)
        ret["discount_price"] = ret["nominal_price"]
        ret["nominal_price"] = price_after_duration
        ret["discount_duration"] = duration
    return ret

def scrape_more_info(context,link):
    page=context.new_page()
    page.goto("https://www2.telenet.be"+link)
    expect(page.locator('.promo-highlight__third-row'))
    print(f"MORE INFO from {link}")
    ret={}
    title_el=page.query_selector('.text-align--left')
    if title_el:
        title=title_el.inner_text()
        print("Title: ",title)
        ret["title"] = title
    price_el=page.query_selector('.promo-highlight__third-row')
    if price_el:
        price=price_el.inner_text()
        print("Price: ",price)
        ret["nominal_price"] = price
    duration_el=page.query_selector('span.duration-month')
    if duration_el:
        duration =duration_el.inner_text()
        duration = re.findall(r'\d+', duration)[0]
        price_after_duration=page.query_selector('.promo-highlight__second-row').inner_text()
        print("Duration: ",duration)
        print("Price after: ",price_after_duration)
        ret["discount_price"] = ret["nominal_price"]
        ret["nominal_price"] = price_after_duration
        ret["discount_duration"] = duration

    if page.query_selector(".cmp-text__listing--primary-ticks"):
        ul=page.query_selector_all(".cmp-text__listing--primary-ticks")
        text ="\n".join([x.inner_text() for x in ul])
        print(text)
        ret["desc"] = text
    page.close()
    return ret

def run():
    start_navigation()

if __name__ == "__main__":
    start = time.perf_counter()
    run()
    end = time.perf_counter()
    print(end-start)
