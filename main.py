import os
import time
import random
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException, UnexpectedAlertPresentException, NoSuchElementException

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
        print("Date input set to 2024-07-20")

        # 種目を選択
        purpose_select = driver.find_element(By.ID, "purpose-home")
        purpose_select.click()
        purpose_select.find_element(By.XPATH, "//option[. = 'テニス（人工芝）']").click()  # テニス（人工芝）
        print("Purpose set to テニス（人工芝）")

        # 公園名選択肢が表示されるのを待機
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "bname-home")))

        # 公園を選択
        bname_select = driver.find_element(By.ID, "bname-home")
        bname_select.click()

        # 公園の選択肢をデバッグ出力
        park_options = bname_select.find_elements(By.TAG_NAME, "option")
        for option in park_options:
            print(f"Option: {option.text}, Value: {option.get_attribute('value')}")

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//option[. = '小金井公園']")))
        bname_select.find_element(By.XPATH, "//option[. = '小金井公園']").click()  # 小金井公園
        print("Park set to 小金井公園")

        # 検索ボタンをクリック
        search_button = driver.find_element(By.ID, "btn-go")
        search_button.click()

        # ページのHTMLを出力して確認
        print(driver.page_source)

        # アラートが表示されるか確認し、閉じる
        try:
            WebDriverWait(driver, 10).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            print(f"Alert Text: {alert.text}")
            alert.accept()
            notify_line(f"検索結果にエラー: {alert.text}")
            return  # アラートが表示された場合、処理を中断
        except NoAlertPresentException:
            pass

        # ページが遷移するまで待機
        WebDriverWait(driver, 10).until(EC.url_changes(driver.current_url))
        print(driver.current_url)  # 現在のURLを表示

    except UnexpectedAlertPresentException as e:
        alert = driver.switch_to.alert
        print(f"Error fetching search results: Alert Text: {alert.text}")
        alert.accept()
        notify_line(f"検索結果にエラー: {alert.text}")
    except NoSuchElementException as e:
        print(f"No such element: {str(e)}")
        notify_line(f"指定された要素が見つかりませんでした: {str(e)}")
    except Exception as e:
        print(f"Error fetching search results: {str(e)}")
        notify_line(f"検索結果にエラー: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    check_availability()
