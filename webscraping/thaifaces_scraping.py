# This website is pretty good, It's a biggest sources of Thai Fonts dataset right now.
# Best for collecting fonts.
# This website is linking into popular open font website like f0nt.com, fontcraftstudio.com and also unpopular even facebook giveaway...

import re
from playwright.sync_api import Playwright, sync_playwright, expect, Page
from playwright_stealth import stealth_sync # used playwright_stealth since thaifonts gave me headache.
from typing import List
import time
import os

args = [
    '--no-sandbox',
    '--disable-infobars',
    '--start-maximized',
    '--window-position=-10,0',
    # '--proxy-server=http=' + ipAndPort
]

ignoreDefaultArgs = ['--enable-automation']

dirname = os.path.dirname(__file__)
scrape_folder = os.path.join(dirname, "scrape_files", "thaifaces")
os.makedirs(scrape_folder, exist_ok=True)
log_path = os.path.join(scrape_folder, 'log.txt')
log_other_path = os.path.join(scrape_folder, 'log_other.txt')
log_demo_path = os.path.join(scrape_folder, 'log_demo_other.txt')
num_passed_path = os.path.join(scrape_folder, 'num_passed.txt')

# Download File
def download_file(download_info, folder=scrape_folder) -> None:
    download = download_info.value
    download_path = os.path.join(folder, download.suggested_filename)
    download.save_as(download_path)

# Close Ads which appear
def check_ads(page: Page) -> None:
    # Ads 1
    if page.frame_locator("iframe[name=\"aswift_5\"]").frame_locator("iframe[name=\"ad_iframe\"]").get_by_label("ปิดโฆษณา").is_visible():
        page.frame_locator("iframe[name=\"aswift_5\"]").frame_locator("iframe[name=\"ad_iframe\"]").get_by_label("ปิดโฆษณา").click()
    # Ads 2
    if page.frame_locator("iframe[name=\"aswift_7\"]").frame_locator("iframe[name=\"ad_iframe\"]").get_by_label("ปิดโฆษณา").is_visible():
        page.frame_locator("iframe[name=\"aswift_7\"]").frame_locator("iframe[name=\"ad_iframe\"]").get_by_label("ปิดโฆษณา").click()
    # Ads 3
    if page.frame_locator("iframe[name=\"aswift_5\"]").get_by_label("ปิดโฆษณา").is_visible():
        page.frame_locator("iframe[name=\"aswift_5\"]").get_by_label("ปิดโฆษณา").click()

# www.f0nt.com
def font_1(page: Page) -> None:
    # Download Button Clicking 
    try:
        with page.expect_download() as download_info:
            page.get_by_role("link", name="ดาวน์โหลด!").click()
            check_ads(page)
        download_file(download_info)
        page.close()
    except Exception as e:
        print(e)
        page.close()
   
# www.fontcraftstudio.com
def font_2(page: Page) -> None:
    
    try:
        with page.expect_download() as download_info:
            with page.expect_popup() as page2_info:
                page.get_by_role("link", name="ดาวน์โหลดฟอนต์", exact=True).click()
            page2 = page2_info.value
            download_file(download_info)
            page2.close()
        page.close()
    except Exception as e:
        print(e)
        page.close()

def other_website(page: Page, info: List) -> None:
    ...

def write_log(info: List, other: bool = False, demo: bool = False) -> None:
    log = open(log_path, 'a')
    log_other = open(log_other_path, 'a')
    log_demo = open(log_demo_path, 'a')
    # Write global log
    log.write(f"{info[0]}, {info[1]}, {info[2]}, {info[3]}\n")
    # Write other log
    if other:
        log_other.write(f"{info[0]}, {info[1]}, {info[2]}, {info[3]}\n")
    elif demo:
        log_demo.write(f"{info[0]}, {info[1]}, {info[2]}, {info[3]}\n")
    
    increment_log()

def increment_log() -> None:
    current_number = int(open(num_passed_path, 'r').read().strip())
    new_number = current_number + 1
    file = open(num_passed_path, 'w')
    file.write(str(new_number))

def set_num() -> None:
    current_number = int(open(num_passed_path, 'r').read().strip())
    new_number = (current_number + 1)//15 * 15
    print("Current Font", current_number, "->", new_number)
    file = open(num_passed_path, 'w')
    file.write(str(new_number))
    
def run(playwright: Playwright) -> None:
    auto_website = ["https://www.f0nt.com", "https://www.fontcraftstudio.com"] # website that allow to automatically download
    count_progress = True
    current_number = int(open(num_passed_path, 'r').read().strip())
    set_num()

    if count_progress:
        file_progress_page_len = (current_number + 1)//15 
    else: 
        log = open(log_path, 'w')
        log_other = open(log_other_path, 'w')
        log_demo = open(log_demo_path, 'w')
        file_progress_page_len = 0
    print("Your progress is Page:", file_progress_page_len+1)
    browser = playwright.firefox.launch(args=args, headless=False, ignore_default_args=ignoreDefaultArgs)
    context = browser.new_context()
    context.set_default_timeout(30_000)
    stealth_sync(context) # Stealth PlayWright
    page = context.new_page()
    for idx in range(96 - file_progress_page_len):
        idx = idx + 1 + file_progress_page_len
        for num_font in range(15):
        
            page.goto(f"https://thaifaces.com/?page={idx}")
            check_ads(page)
            page.get_by_role("link", name="กขค").nth(num_font).click()
            font_url = page.url
            check_ads(page)

            if page.get_by_role("button", name="ลิงก์ดาวน์โหลด").is_visible() or page.get_by_role("button", name=" ดาวน์โหลด Demo").is_visible():
                pass
            else:
                write_log([idx, num_font, font_url, "None"], demo=True)
                print("page:",idx, "font:",num_font)
                print("#2 demo website")
                continue
            
            # Open Link in ThaiFaces
            with page.expect_popup() as page1_info:
                if page.get_by_role("button", name="ลิงก์ดาวน์โหลด").is_visible(): # Normal Link
                    page.get_by_role("button", name="ลิงก์ดาวน์โหลด").click()

                elif page.get_by_role("button", name=" ดาวน์โหลด Demo").is_visible(): # Demo, Failed to Download -> Do it by hand.
                    page.get_by_role("button", name=" ดาวน์โหลด Demo").click()
                    page_demo = page1_info.value
                    url = page_demo.url
                    write_log([idx, num_font, font_url, url], demo=True)
                    print("page:",idx, "font:",num_font)
                    print("demo website")
                    page_demo.close()
                    continue

            page_pop_up = page1_info.value
            url = page_pop_up.url
            print(url)

            # www.f0nt.com
            if url.startswith(auto_website[0]):
                print("page:",idx, "font:",num_font)
                print("www.f0nt.com")
                font_1(page_pop_up)
                write_log([idx, num_font, font_url, url])

            # www.fontcraftstudio.com
            elif url.startswith(auto_website[1]):
                print("page:",idx, "font:",num_font)
                print("www.fontcraftstudio.com")
                font_2(page_pop_up)
                write_log([idx, num_font, font_url, url])

            else:
                print("page:",idx, "font:",num_font)
                print("other website")
                # other_website(page_pop_up, [idx, num_font, font_url, url])
                write_log([idx, num_font, font_url, url], other=True)

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    while True:
        try:
            run(playwright)
        except KeyboardInterrupt:
            raise "Stopped"
