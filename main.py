from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import datetime
import os
import sys

def get_search_results():
    try:
        # Chrome WebDriverのセットアップ
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

        # トップページを開く
        driver.get('https://kouen.sports.metro.tokyo.lg.jp/web/index.jsp')

        # 日付を入力
        day_start_element = driver.find_element(By.ID, 'daystart-home')
        day_start_element.send_keys(datetime.datetime.now().strftime('%Y-%m-%d'))

        # 種目を選択
        purpose_select = Select(driver.find_element(By.ID, 'purpose-home'))
        purpose_select.select_by_value('1000_1030')  # テニス（人工芝）

        # 公園を選択（公園名は適宜変更してください）
        park_select = Select(driver.find_element(By.ID, 'bname-home'))
        park_select.select_by_visible_text('小金井公園')

        # 検索ボタンをクリック
        search_button = driver.find_element(By.ID, 'btn-go')
        search_button.click()

        # 検索結果ページのHTMLを取得
        html = driver.page_source

        driver.quit()
        return html
    except Exception as e:
        print(f"Error fetching search results: {e}")
        if 'driver' in locals():
            driver.quit()
        sys.exit(1)

def check_availability(html):
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        # 検索結果ページのHTMLを解析して空きスロットを取得
        courts = soup.find_all('div', class_='available')  # 'available' クラスを持つ要素を取得
        available = []

        now = datetime.datetime.now()
        current_weekend = [now + datetime.timedelta(days=(5 - now.weekday())), 
                           now + datetime.timedelta(days=(6 - now.weekday()))]
        
        print(f"Checking for slots on: {current_weekend}")

        for court in courts:
            court_name = court.find('div', class_='court-name').text.strip()  # コート名を取得
            for slot in court.find_all('div', class_='time-slot'):  # 'time-slot' クラスを持つ要素を取得
                slot_time_str = slot.find('span', class_='time').text.strip()
                slot_time = datetime.datetime.strptime(slot_time_str, '%Y-%m-%d %H:%M')
                if slot_time.weekday() in [5, 6] and 13 <= slot_time.hour < 19 and 'available' in slot['class']:
                    if slot_time.date() in [d.date() for d in current_weekend]:
                        available.append((court_name, slot_time))
                        print(f"Found available slot: {court_name} at {slot_time}")
        
        return available
    except Exception as e:
        print(f"Error checking availability: {e}")
        sys.exit(1)

def send_line_notification(message):
    try:
        import requests
        line_token = os.getenv('LINE_NOTIFY_TOKEN')
        if not line_token:
            print("LINE_NOTIFY_TOKEN is not set")
            sys.exit(1)
        
        headers = {
            'Authorization': f'Bearer {line_token}',
        }
        data = {
            'message': message,
        }
        response = requests.post(
            'https://notify-api.line.me/api/notify',
            headers=headers,
            data=data
        )
        response.raise_for_status()
        print("LINE notification sent successfully")
    except Exception as e:
        print(f"Error sending LINE notification: {e}")
        sys.exit(1)

def save_html_to_file(html, filename):
    try:
        with open(filename, 'w', encoding='utf-8') as file:  # UTF-8 エンコーディングで保存
            file.write(html)
    except Exception as e:
        print(f"Error saving HTML to file: {e}")
        sys.exit(1)

def main():
    search_results_html = get_search_results()
    save_html_to_file(search_results_html, 'search_results.html')
    print("Search results HTML saved to search_results.html")

    available_slots = check_availability(search_results_html)
    if available_slots:
        message = f"空き状況:\n" + "\n".join([f"{slot[0]} at {slot[1].strftime('%Y-%m-%d %H:%M')}" for slot in available_slots])
        send_line_notification(message)
    else:
        print("No available slots found")

if __name__ == "__main__":
    main()
