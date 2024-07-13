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
        form = soup.find('form', {'name': 'rsvMainForm'})
        action_url = form['action']
        search_url = requests.compat.urljoin(url, action_url)

        # フォームデータの準備
        form_data = {}
        for input_tag in form.find_all('input'):
            if input_tag.get('name'):
                form_data[input_tag.get('name')] = input_tag.get('value')

        # 必要なフィールドの設定
        form_data['shisetsuCategory'] = '1'  # 種目：テニス（人工芝）
        form_data['park'] = '102'            # 公園：小金井公園
        form_data['command'] = 'list'
        
        search_response = session.post(search_url, data=form_data)
        search_response.raise_for_status()
        
        return search_response.text
    except Exception as e:
        print(f"Error fetching search results: {e}")
        sys.exit(1)

def check_availability(html):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # 必要なデータを効率的に取得（HTML構造に依存）
        courts = soup.find_all('court')
        available = []

        now = datetime.datetime.now()
        current_weekend = [now + datetime.timedelta(days=(5 - now.weekday())), 
                           now + datetime.timedelta(days=(6 - now.weekday()))]
        
        print(f"Checking for slots on: {current_weekend}")

        for court in courts:
            for slot in court.find_all('time_slot'):
                slot_time = datetime.datetime.strptime(slot['time'], '%Y-%m-%d %H:%M')
                if slot_time.weekday() in [5, 6] and 13 <= slot_time.hour < 19 and slot['status'] == 'available':
                    if slot_time.date() in [d.date() for d in current_weekend]:
                        available.append((court['name'], slot_time))
                        print(f"Found available slot: {court['name']} at {slot_time}")
        
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

def main():
    search_results_html = get_search_results()
    available_slots = check_availability(search_results_html)
    if available_slots:
        message = f"空き状況:\n" + "\n".join([f"{slot[0]} at {slot[1].strftime('%Y-%m-%d %H:%M')}" for slot in available_slots])
        send_line_notification(message)
    else:
        print("No available slots found")

if __name__ == "__main__":
    main()
