import requests
import time
import json

from config import CONFIG
from divar_scrapper import get_house_info_string

SEND_MESSAGES_COUNTER = 1


def send_message(chat_id, text):
    for i in range(5):
        url = f"https://api.telegram.org/bot{CONFIG['bot_api_key']}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        json_payload = json.dumps(payload)
        header = {"Content-Type": "application/json"}

        try:
            response = requests.post(url, data=json_payload, headers=header, proxies=CONFIG['proxies'])

            if response.status_code == 200:
                return True

        except Exception as e:
            print("--- ERROR at send message ---")
            print(e)
            print('you may not installed pysocks !')

    return False


def send_photo(chat_id, photo_url, caption):
    for i in range(5):
        url = f"https://api.telegram.org/bot{CONFIG['bot_api_key']}/sendPhoto"
        payload = {"chat_id": chat_id, "photo": photo_url, "caption": caption}
        json_payload = json.dumps(payload)
        header = {"Content-Type": "application/json"}

        try:
            response = requests.post(url, data=json_payload, headers=header, proxies=CONFIG['proxies'])

            if response.status_code == 200:
                return True
        except Exception as e:
            print("--- ERROR at send photo ---")
            print(e)
            print('you may not installed pysocks !')

    return False


def notify_user(chat_id, record):
    global SEND_MESSAGES_COUNTER

    if SEND_MESSAGES_COUNTER % 20 == 0:
        print('waiting for 5 seconds')
        time.sleep(5)

    SEND_MESSAGES_COUNTER += 1

    if int(record['image_count']) >= 1:   # if record has image
        status = send_photo(chat_id, record['image_url'], get_house_info_string(record))

    else:
        status = send_message(chat_id, get_house_info_string(record))

    return status


def notify_all(chat_id, records):
    print(f'sending {len(records)} record(s) to user {chat_id}')
    not_send = []

    for record in records:
        send_status = notify_user(chat_id, record)
        if not send_status:
            print(f"couldn't send to user {chat_id} this message :{record}")
            not_send.append([chat_id, record])

    return not_send
