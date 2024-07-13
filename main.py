import requests
from bs4 import BeautifulSoup
import datetime
import os

# 小金井公園のページURL
url = 'https://kouen.sports.metro.tokyo.lg.jp/web/index.jsp'

def check_availability():
    response = requests.get(url)
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

available_slots = check_availability()

if available_slots:
    line_token = os.getenv('LINE_NOTIFY_TOKEN')
    message = f"空き状況:\n" + "\n".join([f"{slot[0]} at {slot[1].strftime('%Y-%m-%d %H:%M')}" for slot in available_slots])
    
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
