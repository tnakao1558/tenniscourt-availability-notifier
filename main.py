from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

# User-Agentのリスト
user_agents = [
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/B08C3901",
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299"
]

# ランダムにUser-Agentを選択
user_agent = random.choice(user_agents)

# webdriverの作成
options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--headless')
options.add_argument(f'user-agent={user_agent}') # User-Agentを設定
driver = webdriver.Chrome(options=options)

# 要素が見つからない場合は5秒待つように設定
driver.implicitly_wait(5)
# 要素が有効になるまで5秒待機
wait = WebDriverWait(driver, 5)

# 検索したいサイト
driver.get("https://kouen.sports.metro.tokyo.lg.jp/web/index.jsp")

# 検索したページのHTMLを表示
print(driver.page_source)

# webdriverの終了
driver.quit()