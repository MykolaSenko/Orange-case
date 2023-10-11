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
    def __init__(self,scraper, logger):
        self._logger = logger
        self._results = []
        self._scraper = scraper
        try:
            with open('config/'+scraper + '_config.json','r') as file:
                self._config = json.load(file)
        except:
            self._logger.critical('Error loading config', config_file=scraper)

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
                prefix=self._config['params']['default']['navigation']['url_prefix']
                suffix=obj.get_attribute('href')
                if prefix not in suffix:
                    link = prefix + suffix
                else:
                    link = suffix
                tmp = link.split("/")
                if "." in tmp[-1]:
                    scrape_type = [tmp[-1]]
                else:
                    scrape_type = [tmp[-2]]
                next_config=self.get_config_based_target(link)
            else:
                # If it's not link it's clickable object, so we click
                link = 'here'
                scrape_type = [url.split("/")[-2]]
                obj.click()
                next_config=self._config['params']['default']
            self._logger.info('navigate', destiny=link)
            self.navigator(context,link,next_config, scrape_type)
        df = pd.DataFrame(self._results)
        df.to_csv("data/" + self._scraper + '.csv')

    def navigator(self,context,link,params, scrape_type):
            scrape_tag=params['navigation']['iterator']
            sublink_tag=params['navigation'].get('sub_link_tag','gjkdgbkd')
            try:
                if link == 'here':
                    page=context.pages()[-1]
                else:
                    page=context.new_page()
                    page.goto(link)
                #Makes sure critical info is loaded
                page.wait_for_selector(params['navigation'].get('page_load', 'body'))
            except:
                self._logger.critical('required information not found',
                                  page=link,awaited_info=params['navigation'].get('page_load',
                                                                                 'body'))
            else:
                summaries=page.query_selector_all(scrape_tag)[:params['navigation']['iterator_size']]
                self._logger.info('Page read', page=link, look_for=scrape_tag)
                if len(summaries) == 0:
                    self._logger.error('scrape failure', type='page', page=link)
                for summary in summaries:
                    if summary.query_selector(sublink_tag):
                        target=summary.query_selector(sublink_tag)
                        target=params['navigation']['url_prefix']+target.get_attribute('href')
                        #scrape_type.append(target.split("/")[-2])
                        next_config=self.get_config_based_target(target)
                        self._logger.info('navigate', destiny=target)
                        self.navigator(context, target, next_config, scrape_type)
                    else:
                        self._logger.info('Scraping page', page=link)
                        ret = self.scrape_page(summary,link, params)
                        if ret:
                            ret["link"] = page.url
                            ret["scrape_type"] = scrape_type[0]
                            self._results.append(ret)
            finally:
                page.close()

    def get_config_based_target(self,target):
        ret=deepcopy(self._config['params'])
        keys=ret.keys()
        try:
            for key in keys:
                if key in target:
                    for k in ret['default'].keys():
                        ret['default'][k].update(ret[key][k])
                    break
        except:
            self._logger.critical('Config error', target=target)
        finally:
            return ret['default']

    def scrape_page(self,summary,link,params):
        ret ={}
        for key,item in params['data'].items():
            result = self.get_text_from_tag(summary,[item.get('tag','body')],item.get('multiple',False))
            if len(result)> 1:
                if item.get('re'):
                    result=self.execute_regex(item['re'], item['re_type'], result)
                if len(result) > 0:
                    ret[key]=result
            else:
                self._logger.warning('scrape failure', type='field', page=link,target=key, attempt=item.get('tag','body'))
        if not ret:
            self._logger.error('scrape failure', type='page', page=link, data=summary.inner_text())
        return ret

    def execute_regex(self,pattern, re_type, text):
        res=''
        try:
            if re_type=='search':
                res=re.search(pattern,text).group(1)
            elif re_type=='sub':
                res=re.sub(pattern[0], pattern[1], text)
            elif re_type=='find_all':
                res="\n".join(re.find_all(pattern, text))
        except:
                self._logger.error('regex failure', pattern=pattern,text=text)
        finally:
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
                    res+=" " + tmp
        return res

if __name__ == "__main__":
    start = time.perf_counter()
    telenet = Scraper('proximus')
    telenet.run()
    end = time.perf_counter()
    print(end-start)
