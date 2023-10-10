#! /usr/bin/python3
import time
#import scr.scrape_gadgets as sg
import src.scrape_urls as su
import src.scrape_gadgets as sg
import src.Scraper as scraper
import structlog
import os

logger=structlog()
start = time.perf_counter()
#Scrape providers
providers = ['telenet_promo','telenet_packs','proximus','mobile_vikings']
for provider in providers:
    scrp = scraper.Scraper(provider, logger)
    scrp.run()
#Scrape gadgets urls for telenet and write to CSV so they can be different tasks on airflow
category_urls=su.get_category_links("https://www2.telenet.be/residential/nl/toestellen/?intcmp=ToestNav", logger)
all_devices_urls = []
for category in category_urls:
    urls = su.get_all_urls(category['url'])
    all_devices_urls.append({"category":category['category'].replace(" ","_"),"urls":urls})
df = pd.DataFrame(all_devices_urls)
df.to_csv("devices_urls.csv")
#Scrape gadgets from saved urls
all_urls=sg.get_urls_from_csv("devices_urls.csv")
for i in all_urls:
    device = i["category"]
    device_url_list = i["urls"]
    df = pd.DataFrame(sg.get_devices(device_url_list),columns=['product_id', 'model', 'color', 'memory', 'price_regular', 'price_for_clients', 'link'])
    df.to_csv(f"data/telenet_{device}.csv")
os.remove("devices_urls.csv")
end = time.perf_counter()
print(f'Time required to scrape: {end}-{start} seconds')
