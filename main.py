import requests
import os
import sys

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
    # テストメッセージを送信
    test_message = "これはテストメッセージです。LINE通知が正しく動作しているか確認してください。"
    send_line_notification(test_message)

if __name__ == "__main__":
    main()
