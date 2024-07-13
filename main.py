import requests
from bs4 import BeautifulSoup
import datetime
import os
import sys

# 小金井公園のページURL
url = 'https://kouen.sports.metro.tokyo.lg.jp/web/index.jsp'

def check_availability():
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 必要なデータを効率的に取得（HTML構造に依存）
        courts = soup.find_all('court')
        available = []

        now = datetime.datetime.now()
        current_weekend = [now + datetime.timedelta(days=(5 - now.weekday())), 
                           now + datetime.timedelta(days=(6 - now.weekday()))]
        
        for court in courts:
            for slot in court.find_all('time_slot'):
                slot_time = datetime.datetime.strptime(slot['time'], '%Y-%m-%d %H:%M')
                if slot_time.weekday() in [5, 6] and 13 <= slot_time.hour < 19 and slot['status'] == 'available':
                    if slot_time.date() in [d.date() for d in current_weekend]:
                        available.append((court['name'], slot_time))
        
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
    except Exception as e:
        print(f"Error sending LINE notification: {e}")
        sys.exit(1)

def main():
    available_slots = check_availability()
    if available_slots:
        message = f"空き状況:\n" + "\n".join([f"{slot[0]} at {slot[1].strftime('%Y-%m-%d %H:%M')}" for slot in available_slots])
        send_line_notification(message)
    else:
        print("No available slots found")

if __name__ == "__main__":
    main()
