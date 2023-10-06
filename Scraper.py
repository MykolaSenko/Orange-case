#! /usr/bin/python3

#Created by Henrique Rauen (rickgithub@hsj.email)
import asyncio
import time
import re
import pandas as pd
import json
from copy import deepcopy
from playwright.sync_api import sync_playwright, Route, expect

class Scraper():
    def __init__(self,scraper):
        self._results = []
        self._scraper = scraper
        with open(scraper + '_config.json','r') as file:
            self._config = json.load(file)
    
    def filter(self,objs):
        return objs
    
    def run(self):
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=False)
            context=browser.new_context()
            self.start_navigation(self._config['start']['url'], context)
            browser.close()

    def start_navigation(self,url, context):
        page=context.new_page()
        page.goto(url)
        objs=(page.locator(self._config['start']['locator'])
                    .all())
        objs=self.filter(objs)
        for obj in objs:
            if obj.get_attribute('href'):
                link=self._config['params']['default']['navigation']['url_prefix']
                link +=obj.get_attribute('href')
            else:
                # If it's not link it's clickable object, so we click
                link = 'here'
                obj.click()
            self.navigator(context,link, self._config['params']['default'])
        df = pd.DataFrame(self._results)
        df.to_csv("data/" + self._scraper + '.csv')

    def navigator(self,context,link,params, scrape_type=''):
            scrape_tag=params['navigation']['iterator']
            sublink_tag=params['navigation'].get('sub_link_tag','gjkdgbkd')
            if link == 'here':
                page=context.pages()[-1]
            else:
                page=context.new_page()
            #Makes sure critical info is loaded
            try:
                page.goto(link)
                page.wait_for_selector(params['navigation'].get('page_load', 'body.default-page'))
            except:
                print(f'Page {link} did not load critical information')
            else:
                summaries=page.query_selector_all(scrape_tag)[:params['navigation']['iterator_size']]
                for summary in summaries:
                    if summary.query_selector(sublink_tag):
                        target=summary.query_selector(sublink_tag)
                        target="https://www2.telenet.be"+target.get_attribute('href')
                        scrape_type += target.split("/")[-2]
                        next_config=self.get_config_based_target(target)
                        self.navigator(context, target, next_config, scrape_type)
                    else:
                        ret = self.scrape_page(summary,link, params)
                        ret["link"] = page.url
                        ret["scrape_type"] = scrape_type
                        self._results.append(ret)
            finally:            
                page.close()

    def get_config_based_target(self,target):
        ret=deepcopy(self._config['params'])
        keys=ret.keys()
        for key in keys:
            if key in target:
                for k in ret['default'].keys():
                    ret['default'][k].update(ret[key][k])
                break
        return ret['default']

    def scrape_page(self,summary,link,params):
        ret ={}
        #print(f"SUMMARY from page: {link}")
        for key,item in params['data'].items():
            result = self.get_text_from_tag(summary,[item.get('tag','body')],item.get('multiple',False))
            if len(result)> 1:
                if item.get('re'):
                    result=self.execute_regex(item['re'], item['re_type'], result)
                ret[key]=result
        return ret

    def execute_regex(self,pattern, re_type, text):
        res=''
        if re_type=='search':
            res=re.search(pattern,text).group(1)
        elif re_type=='sub':
            res=re.sub(pattern[0], pattern[1], text)
        elif re_type=='find_all':
            res="\n".join(re.find_all(pattern, text))
        return res

    def get_text_from_tag(self,element,selector, multiple=False):
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

if __name__ == "__main__":
    start = time.perf_counter()
    telenet = Scraper('mobile-vikings')
    telenet.run()
    end = time.perf_counter()
    print(end-start)