import os
import time
import random
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# LINE Notifyのアクセストークン
LINE_NOTIFY_TOKEN = os.getenv("LINE_NOTIFY_TOKEN")

# User-Agentのリスト
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/B08C3901",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299"
]

# ランダムにUser-Agentを選択
user_agent = random.choice(user_agents)

# WebDriverのオプション設定
options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--headless')
options.add_argument(f'user-agent={user_agent}')

# WebDriverの作成
driver = webdriver.Chrome(options=options)

def notify_line(message):
    headers = {
        "Authorization": f"Bearer {LINE_NOTIFY_TOKEN}"
    }
    data = {
        "message": message
    }
    response = requests.post("https://notify-api.line.me/api/notify", headers=headers, data=data)
    print(response.status_code)

def check_availability():
    try:
        driver.get("https://kouen.sports.metro.tokyo.lg.jp/web/index.jsp")

        # 利用日を入力
        date_input = driver.find_element(By.ID, "daystart-home")
        date_input.clear()
        date_input.send_keys("2024-07-20")

        # 種目を選択
        purpose_select = driver.find_element(By.ID, "purpose-home")
        purpose_select.click()
        purpose_select.find_element(By.XPATH, "//option[@value='1000_1030']").click()  # テニス（人工芝）

        # 公園名選択肢が表示されるのを待機
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "bname-home")))

        # 公園を選択
        bname_select = driver.find_element(By.ID, "bname-home")
        bname_select.click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//option[text()='小金井公園']")))
        bname_select.find_element(By.XPATH, "//option[text()='小金井公園']").click()

        # 検索ボタンをクリック
        search_button = driver.find_element(By.ID, "btn-go")
        search_button.click()

        # 検索結果を待機
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "search-result")))

        # 検索結果を取得
        results = driver.find_element(By.CLASS_NAME, "search-result").text
        print(results)

        # 空き状況をLINEに通知
        notify_line(f"小金井公園のテニスコート空き状況:\n{results}")

    except Exception as e:
        print(f"Error fetching search results: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    check_availability()
