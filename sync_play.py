#! /usr/bin/python3

#Created by Henrique Rauen (rickgithub@hsj.email)
import asyncio
import time
import re
import pandas as pd
from playwright.sync_api import sync_playwright, Route, expect

config = {'ONE': {'iterator': '.aem-Grid--10'
                  ,'data': {'title':{
                                    'tag':'.cmp-responsivegrid__container >> h3'
                                    ,'multiple':False}}
                            ,'components': {
                                            'tag':'h4'
                                            ,'multiple': True}
                            ,'download_speed': {
                                            're': ''}
                            ,'benefits' : {
                                        're':''}
                            }
        ,'default': {'iterator': '.cmp-product-summary'
                     ,'sub_link_tag': "a:has-text('Meer Info')"
                     ,'data': {'title':{
                     }
                     }
        }
        }

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
                ret = navigator(context,link,pack)
                results.extend(ret)
        df = pd.DataFrame(results)
        df.to_csv("sample.csv")
        browser.close()

def navigator(context,link,pack, params=None):
        scrape_tag=".cmp-product-summary"
        sublink_tag="a:has-text('Meer Info')"
        global config
        if params:
            scrape_tag=params['iterator']
            sublink_tag=params.get('sub_link_tag','fnskfgbdkd')
        page=context.new_page()
        page.goto(link)
        #Makes sure price is loaded
        page.wait_for_selector('.promo-highlight__third-row')
        summaries=page.query_selector_all(scrape_tag)
        results = []
        for summary in summaries:
            if summary.query_selector(sublink_tag):
                target=summary.query_selector(sublink_tag)
                target="https://www2.telenet.be"+target.get_attribute('href')
                if '/one/' not in target:
                    ret = scrape_more_info(context, target)    
                else:
                    ret = navigator(context, target,pack, config["ONE"])
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
    title = get_text_from_tag(summary,['.text-align--left', '.cmp-text'])
    print("Title: ",title)
    ret["title"] = title
    desc=get_text_from_tag(summary,['.cmp-text__listing--primary-ticks'])
    print("Desc: ",desc)
    ret["description"] = desc
    price = get_text_from_tag(summary,['.promo-highlight__third-row'])
    price = re.sub('[€\s\n]', '', price)
    price = price.replace(',','.')
    print("Price: ",price)
    ret["nominal_price"] = price
    # Check for discount duration
    duration = get_text_from_tag(summary,['span.duration-month'])
    if duration:
        duration = re.findall(r'\d+', duration)[0]
        price_after_duration=re.sub('[€\s\n]', '',
                        get_text_from_tag(summary,['.promo-highlight__second-row']))
        price_after_duration = price_after_duration.replace(',','.')
        print("Duration: ",duration)
        print("Price after: ",price_after_duration)
        ret["discount_price"] = ret["nominal_price"]
        ret["nominal_price"] = price_after_duration
        ret["discount_duration"] = duration
    return ret

def scrape_more_info(context,link):
    page=context.new_page()
    page.goto(link)
    page.wait_for_selector('.promo-highlight__third-row')
    print(f"MORE INFO from {link}")
    ret={}
    title = get_text_from_tag(page,['.cmp-responsivegrid__container >> h1'])
    print("Title: ",title)
    ret["title"] = title
    price=get_text_from_tag(page,['.promo-highlight__third-row'])
    price=re.sub('[€\s\n]', '', price)
    price = price.replace(',','.')
    print("Price: ",price)
    ret["nominal_price"] = price

    duration=get_text_from_tag(page,['span.duration-month'])
    if duration:
        duration=re.findall(r'\d+', duration)[0]
        price_after_duration=get_text_from_tag(page,['.promo-highlight__second-row'])
        price_after_duration=re.sub('[€\s\n]', '', price_after_duration)
        price_after_duration = price_after_duration.replace(',','.')
        print("Duration: ",duration)
        print("Price after: ",price_after_duration)
        ret["discount_price"] = ret["nominal_price"]
        ret["nominal_price"] = price_after_duration
        ret["discount_duration"] = duration
    desc = get_text_from_tag(page,['.cmp-text__listing--primary-ticks'], True)
    print(desc)
    ret["description"] = desc
    page.close()
    return ret

def scrape_more_info_one():
    return None

def get_text_from_tag(element,selector, multiple=False):
    res = ''
    for sel in selector:
        if multiple:
            inner_el=element.query_selector_all(sel)
            if inner_el:
                res+=" " + "\n".join([x.inner_text() for x in inner_el])
        else:
            inner_el=element.query_selector(sel)
            if inner_el:
                tmp = inner_el.inner_text()
                if len(tmp) < 50:
                    res+=" " + tmp
    return res

def run():
    start_navigation()

if __name__ == "__main__":
    start = time.perf_counter()
    run()
    end = time.perf_counter()
    print(end-start)
