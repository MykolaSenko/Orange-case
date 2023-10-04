#! /usr/bin/python3

#Created by Henrique Rauen (rickgithub@hsj.email)
import asyncio
import time
import re
import pandas as pd
from copy import deepcopy
from playwright.sync_api import sync_playwright, Route, expect

config = {'residential/nl/producten/one/': {
                    'navigation': {
                        'iterator': '.aem-Grid--10'
                        #,'iterator_size': None
                        }
                    ,'data': {'title':{
                                    'tag':'h3'
                                    ,'multiple':False}
                            ,'description':{
                                    'tag':'.cmp-text__listing--primary-ticks'
                                    ,'multiple': True}
                            ,'components': {
                                            'tag':'h4'
                                            ,'multiple': True}
                            ,'internet_speed': {
                                            'tag':'.text'
                                            ,'multiple': True
                                            ,'re': '.*internet.*?(\d+\s[MG]bps)'
                                            ,'re_type': 'search'}
                            ,'benefits' : {
                                        're':'*.Gratis?([\w\s]+)'
                                        ,'re_type': 'find_all'}
                            }}
        ,'default': {'navigation':{
                        'iterator': '.cmp-product-summary'
                        ,'iterator_size': None
                        ,'sub_link_tag': "a:has-text('Meer Info')"}
                     ,'data': {'title':{
                                        'tag':'.text-align--left'}
                              ,'description':{
                                        'tag':'.cmp-text__listing--primary-ticks'}
                              ,'promotion_duration':{
                                        'tag':'span.duration-month'
                                        ,'re': '(\d+)'
                                        ,'re_type': 'search'}
                              ,'initial_price':{
                                        'tag':'.promo-highlight__third-row'
                                        ,'re': ['[€\s\n]','']
                                        ,'re_type': 'sub'}
                              ,'post_promotion_price':{
                                        'tag':'.promo-highlight__second-row'
                                        ,'re': ['[€\s\n]','']
                                        ,'re_type': 'sub'}
                                }
                     }
        ,'---' : {'navigation':{
                        'iterator': '.cmp-responsivegrid__container'
                        ,'iterator_size':1}
                  ,'data': {'components': {
                                        'tag':'.heading--4'
                                        ,'multiple': True}
                              ,'description':{
                                        'tag':'.cmp-text__listing--primary-ticks'
                                        ,'multiple':True}
                                }
                }
        }

results = []

def start_navigation(url="https://www2.telenet.be/residential/nl"):
    global config
    global results
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
                pack = False
                if contains > 1:
                    pack=True
                navigator(context,link,pack, config['default'])
        df = pd.DataFrame(results)
        df.to_csv("sample.csv")
        browser.close()

def navigator(context,link,pack,params):
        global results
        scrape_tag=params['navigation']['iterator']
        sublink_tag=params['navigation'].get('sub_link_tag','gjkdgbkd')
        page=context.new_page()
        page.goto(link)
        #Makes sure price is loaded
        page.wait_for_selector('.promo-highlight__third-row')
        summaries=page.query_selector_all(scrape_tag)[:params['navigation']['iterator_size']]
        for summary in summaries:
            if summary.query_selector(sublink_tag):
                target=summary.query_selector(sublink_tag)
                target="https://www2.telenet.be"+target.get_attribute('href')
                next_config=get_config_based_target(target)
                navigator(context, target,pack, next_config)
            else:
                ret = scrape_page(summary,link, params)
                ret["link"] = link
                ret["Type"] = "Pack" if pack else "Product"
                results.append(ret)
        page.close()
        return results

def get_config_based_target(target):
    global config
    ret=deepcopy(config)
    keys=ret.keys()
    for key in keys:
        if key in target:
            for k in ret['default'].keys():
                ret['default'][k].update(ret[key][k])
            break
    return ret['default']

def scrape_page(summary,link,params):
    ret ={}
    print(f"SUMMARY from page: {link}")
    for key,item in params['data'].items():
        result = get_text_from_tag(summary,[item.get('tag','body')],item.get('multiple',False))
        if item.get('re') and result != '':
            result=execute_regex(item['re'], item['re_type'], result)
        ret[key]=result
    """
    #title = get_text_from_tag(summary,['.text-align--left', '.cmp-text'])
    
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
    """
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

def execute_regex(pattern, re_type, text):
    res=''
    if re_type=='search':
        res=re.search(pattern,text).group(1)
    elif re_type=='sub':
        res=re.sub(pattern[0], pattern[1], text)
    elif re_type=='find_all':
        res="\n".join(re.find_all(pattern, text))
    return res

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
                #if len(tmp) < 50:
                res+=" " + tmp
    return res

def run():
    start_navigation()

if __name__ == "__main__":
    start = time.perf_counter()
    run()
    end = time.perf_counter()
    print(end-start)
