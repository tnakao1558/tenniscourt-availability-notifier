import requests
from bs4 import BeautifulSoup
import datetime
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# 小金井公園のTOPページURL
url = 'https://kouen.sports.metro.tokyo.lg.jp/web/index.jsp'

def get_search_results():
    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--remote-debugging-port=9222')
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        driver.get(url)
        
        # 入力フォームに値を設定し、検索を実行
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'daystarthome'))).send_keys(
            datetime.datetime.now().strftime('%Y-%m-%d'))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'purpose-home'))).send_keys('テニス（人工芝）')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'bname-home'))).send_keys('小金井公園')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'command'))).send_keys(Keys.RETURN)
        
        # 検索結果を取得
        search_results_html = driver.page_source
        driver.quit()
        
        return search_results_html
    except Exception as e:
        print(f"Error fetching search results: {e}")
        sys.exit(1)

# 省略...

if __name__ == "__main__":
    main()
