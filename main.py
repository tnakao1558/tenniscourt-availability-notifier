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
        chrome_options.add_argument('--window-size=1920x1080')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-3d-apis')
        chrome_options.add_argument('--disable-features=VizDisplayCompositor')
        chrome_options.add_argument('--log-level=3')
        chrome_options.add_argument('--enable-logging')
        chrome_options.add_argument('--v=1')

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        driver.get(url)
        
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, 'daystarthome'))).send_keys(
            datetime.datetime.now().strftime('%Y-%m-%d'))
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, 'purpose-home'))).send_keys('テニス（人工芝）')
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, 'bname-home'))).send_keys('小金井公園')
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, 'command'))).send_keys(Keys.RETURN)
        
        search_results_html = driver.page_source
        driver.quit()
        
        return search_results_html
    except Exception as e:
        print(f"Error fetching search results: {e}")
        driver.quit()
        sys.exit(1)

def check_availability(html):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        courts = soup.find_all('div', class_='available')  
        available = []

        now = datetime.datetime.now()
        current_weekend = [now + datetime.timedelta(days=(5 - now.weekday())), 
                           now + datetime.timedelta(days=(6 - now.weekday()))]
        
        print(f"Checking for slots on: {current_weekend}")

        for court in courts:
            court_name = court.find('div', class_='court-name').text.strip()  
            for slot in court.find_all('div', class_='time-slot'): 
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
