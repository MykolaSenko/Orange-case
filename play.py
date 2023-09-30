#! /usr/bin/python3

#Created by Henrique Rauen (rickgithub@hsj.email)
from playwright.async_api import async_playwright
import asyncio
async def main():
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=False)
        context = await browser .new_context()
        tabs=[await context.new_page()]
        await tabs[0].goto("https://www2.telenet.be/residential/nl/producten/internet-mobiel/")
        await tabs[0].wait_for_timeout(1000)
        summaries= await tabs[0].query_selector_all(".cmp-product-summary")
        for summary in summaries:
            #If it has more info link, clicks on it
            link=await summary.query_selector('a:has-text("Meer Info")')
            if link:
                link = await link.get_attribute('href')
                print(link)
                print("Opened new tab and will read from it")
                tabs.append(await context.new_page())
                await tabs[-1].goto("https://www2.telenet.be"+link)
                ul = await tabs[-1].query_selector("//div[@ class='cmp cmp-grouping aem-GridColumn aem-GridColumn--default--12']//ul")
                text = await ul.inner_text()
                print(text)
            else:
                print("Data from main Page")
                data = await summary.inner_text()
                print(data)
            #print(data.split("\n"))
            #title=await summary.query_selector('.cmp cmp-title aem-GridColumn aem-GridColumn--default--12')
            #print(await title.inner_text())
            #title=await summary.query_selector('.text')
            #print(await title.inner_text())
            #await page.wait_for_selector('span.promo-highlight__third-row--price')
            #price=await summary.query_selector('span.promo-highlight__third-row--price')
            #print(await price.inner_text())
            #print([await x.inner_text() for x in titles])
        await browser.close()

def run():
    asyncio.run(main())

if __name__ == "__main__":
    run()
