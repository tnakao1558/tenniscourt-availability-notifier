import requests
from bs4 import BeautifulSoup
import datetime
import os
import sys

# 小金井公園のTOPページURL
url = 'https://kouen.sports.metro.tokyo.lg.jp/web/index.jsp'

def get_search_results():
    try:
        session = requests.Session()
        response = session.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # フォームの送信先URLを取得
        form = soup.find('form', {'name': 'form1'})
        if not form:
            print("Form not found")
            sys.exit(1)

        action_url = form.get('action')
        if not action_url:
            print("Action URL not found in form")
            sys.exit(1)

        search_url = requests.compat.urljoin(url, action_url)

        # フォームデータの準備
        form_data = {
            'daystarthome': datetime.datetime.now().strftime('%Y-%m-%d'),
            'purpose-home': '1000_1020',  # 種目：テニス（人工芝）
            'bname-home': '102',          # 公園：小金井公園
            'command': 'list'
        }
        
        search_response = session.post(search_url, data=form_data)
        search_response.raise_for_status()
        
        return search_response.text
    except Exception as e:
        print(f"Error fetching search results: {e}")
        sys.exit(1)

def check_availability(html):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # 検索結果ページのHTMLを解析して空きスロットを取得
        courts = soup.find_all('div', class_='available')  # 例として 'div' タグと 'available' クラスを使用しています。実際のタグ名とクラス名を使用してください。
        available = []

        now = datetime.datetime.now()
        current_weekend = [now + datetime.timedelta(days=(5 - now.weekday())), 
                           now + datetime.timedelta(days=(6 - now.weekday()))]
        
        print(f"Checking for slots on: {current_weekend}")

        for court in courts:
            court_name = court.find('div', class_='court-name').text.strip()  # コート名を取得
            for slot in court.find_all('div', class_='time-slot'):  # 例として 'div' タグと 'time-slot' クラスを使用しています。実際のタグ名とクラス名を使用してください。
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
        with open(filename, 'w', encoding='utf-8') as file:
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
