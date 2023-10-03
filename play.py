#! /usr/bin/python3

#Created by Henrique Rauen (rickgithub@hsj.email)
from playwright.async_api import async_playwright
import asyncio
async def navigate_pages(url="https://www2.telenet.be/residential/nl/producten/internet/",
                     scrape_tag=".cmp-product-summary",
                     sublink_tag="a:has-text('Meer Info')"):
    async_tasks = []
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=False)
        context=await browser.new_context()
        tabs=[await context.new_page()]
        await tabs[0].goto(url)
        await tabs[0].wait_for_timeout(1000)
        summaries=await tabs[0].query_selector_all(scrape_tag)
        for summary in summaries:
            #If it has more info link, clicks on it
            link=await summary.query_selector(sublink_tag)
            if link:
                link = await link.get_attribute('href')
                async_tasks.append(
                    asyncio.create_task(scrape_more_info_page(context,link)))
            else:
                async_tasks.append(
                    asyncio.create_task(scrape_page(summary)))
        results = await asyncio.gather(*async_tasks,return_exceptions=True)
        await browser.close()

async def scrape_page(summary):
    print("Data from main Page")
    data = await summary.inner_text()
    print(data)

async def scrape_more_info_page(context,link):
    print(link)
    page=(await context.new_page())
    print("Opened new tab and will read from it")
    await page.goto("https://www2.telenet.be"+link)
    ul = await page.query_selector("//div[@ class='cmp cmp-grouping aem-GridColumn aem-GridColumn--default--12']//ul")
    text = await ul.inner_text()
    print(text)

def run():
    asyncio.run(navigate_pages())

if __name__ == "__main__":
    run()
