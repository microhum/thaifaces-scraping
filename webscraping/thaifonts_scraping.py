# At first I started the project by scraping in thaifonts.net.
# But, after that I find out thaifaces is bigger sources of dataset. I think thaifonts is subset of thatfaces.
# So I'm not reccommended to scrape on this website.

import re
from playwright.sync_api import Playwright, sync_playwright, expect, Page
from playwright_stealth import stealth_sync # I found out this website got a lot of ads and recapcha that's so annoying so playwright_stealth might help. 
import os

dirname = os.path.dirname(__file__)
args = [
    '--no-sandbox',
    '--disable-infobars',
    '--start-maximized',
    '--window-position=-10,0',
    # '--proxy-server=http=' + ipAndPort
]

ignoreDefaultArgs = ['--enable-automation']s

def run(playwright: Playwright) -> None:
    scrape_folder = os.path.join(dirname, "scrape_files")
    file_progress_page_len = (len(os.listdir(scrape_folder))+1)//5
    browser = playwright.firefox.launch(args=args, headless=False, ignore_default_args=ignoreDefaultArgs)
    context = browser.new_context()
    context.set_default_timeout(600_000)
    page = context.new_page()
    stealth_sync(page)

    for idx in range(63 - file_progress_page_len):
        if idx == 63 - 1:
            all_font = 4
        else:
            all_font = 5
        
        idx = idx + file_progress_page_len
    
        for num_font in range(all_font):
            page.goto(f"https://thaifonts.net/fonts/{idx + 1}")
            page.locator("ul").filter(has_text="ดาวน์โหลดตอนนี้").nth(num_font).get_by_role("link").click(delay=300)
            if page.frame_locator("iframe[name=\"aswift_6\"]").frame_locator("iframe[name=\"ad_iframe\"]").get_by_label("ปิดโฆษณา").is_visible():
                page.frame_locator("iframe[name=\"aswift_6\"]").frame_locator("iframe[name=\"ad_iframe\"]").get_by_label("ปิดโฆษณา").click(delay=300)
            page.get_by_role("link", name="ดาวน์โหลดแบบอักษร").click(delay=300)
            # Download Files
            with page.expect_download() as download_info:
                page.get_by_role("link", name="Clicking Here").click(delay=300)
            download = download_info.value
            download_path = os.path.join(scrape_folder, download.suggested_filename)
            download.save_as(download_path)
            print("Downloaded ",download_path)
            print("Page:", idx+1, "Font:", num_font+1)
            # expect(page.get_by_role("heading", name="Downloading")).to_be_visible()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    while True:
        try:
            run(playwright)
        except KeyboardInterrupt:
            raise "Stopped"
