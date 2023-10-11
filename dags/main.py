#! /usr/bin/python3
import time
import scrape_urls as su
import scrape_gadgets as sg
import Scraper as scraper
import structlog
import logging
import os
from pathlib import Path
import pandas as pd
from airflow.decorators import dag, task
from datetime import datetime, timedelta
from pathlib import Path
import json
import pickle

default_args = {
    'owner': 'bo',
    'retires': 5,
    'retry_delay':timedelta(minutes=5)
}

@dag(dag_id = 'dag_immo_pipeline_v1',
     default_args=default_args,
     start_date = datetime(2023,10,7,23,0,0),
     schedule='@daily',
     catchup=False)
def full_pipeline_etl():
    @task
    def scrape_packs_and_promo():
        #Scrape providers
        logger = structlog.get_logger()
        providers = ['telenet_promo','telenet_packs']
        for provider in providers:
            scrp = scraper.Scraper(provider, logger)
            scrp.run()

    @task
    def scrape_category_urls():
        #Scrape gadgets urls for telenet and write to CSV so they can be different tasks on airflow
        logger = structlog.get_logger()
        category_urls=su.get_category_links("https://www2.telenet.be/residential/nl/toestellen/?intcmp=ToestNav", logger)
        all_devices_urls = []
        for category in category_urls:
            urls = su.get_all_urls(category['url'], logger)
            all_devices_urls.append({"category":category['category'].replace(" ","_"),"urls":urls})
        df = pd.DataFrame(all_devices_urls)
        df.to_csv(f"{Path().cwd()}/rawdata/devices_urls.csv")
      
    
    @task
    def scrape_all_gadgets():
        logger = structlog.get_logger()
        all_urls=sg.get_urls_from_csv(f"{Path().cwd()}/rawdata/devices_urls.csv",logger)
        for i in all_urls:
            device = i["category"]
            device_url_list = i["urls"]
            df = pd.DataFrame(sg.get_devices(device_url_list,logger),columns=['product_id', 'model', 'color', 'memory', 'price_regular', 'price_for_clients', 'link'])
            df.to_csv(f"{Path().cwd()}/rawdata/telenet_{device}.csv")
    task1 = scrape_packs_and_promo()
    task2 = scrape_category_urls()
    task3 = scrape_all_gadgets()

    task1 >> task2 >> task3
    


etl = full_pipeline_etl()