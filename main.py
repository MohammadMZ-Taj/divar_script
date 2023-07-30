import json
import requests
import time
from bs4 import BeautifulSoup

from db_crud import read_records, save_record, update_record

with open('constants.json', 'r') as read_const:
    CONST = json.load(read_const)

with open('config.json', 'r', encoding='utf-8') as read_config:
    CONFIG = json.load(read_config)

SEND_MESSAGES_COUNTER = 1


def get_district_code():
    out = []
    for district in CONFIG['house_config']['districts']:
        if district in CONST['district_codes']:
            out.append(CONST['district_codes'][district])
        else:
            print(district + ' was not found')
            raise ValueError
    return out


def get_dict_range(min_value, max_value):
    if max_value > min_value:
        return {"max": max_value, "min": min_value}
    else:
        return {"min": min_value}


def get_string_range(min_value, max_value):
    if max_value > min_value:
        return f"{min_value}-{max_value}"
    else:
        return f"{min_value}-"


def payload_json_schema():
    out = {"category": {"value": "house-villa-rent"},
           "sort": {"value": "sort_date"},
           "cities": ["6"]}

    if CONFIG['house_config']['districts']:
        out['districts'] = {"vacancies": get_district_code()}

    if CONFIG['house_config']['credit']['max'] != 0 or CONFIG['house_config']['credit']['min'] != 0:
        out['credit'] = get_dict_range(CONFIG['house_config']['credit']['min'], CONFIG['house_config']['credit']['max'])

    if CONFIG['house_config']['rent']['max'] != 0 or CONFIG['house_config']['rent']['min'] != 0:
        out['rent'] = get_dict_range(CONFIG['house_config']['rent']['min'], CONFIG['house_config']['rent']['max'])

    if CONFIG['house_config']['size']['max'] != 0 or CONFIG['house_config']['size']['min'] != 0:
        out['size'] = get_dict_range(CONFIG['house_config']['size']['min'], CONFIG['house_config']['size']['max'])

    if CONFIG['house_config']['rooms'] != "":
        out['rooms'] = {'value': CONFIG['house_config']['rooms']}

    return out


def get_room_numbers(persian_room_numbers):
    if persian_room_numbers == 'بدون اتاق':
        return '0'
    elif persian_room_numbers == 'یک':
        return '1'
    elif persian_room_numbers == 'دو':
        return '2'
    elif persian_room_numbers == 'سه':
        return '3'
    elif persian_room_numbers == 'چهار':
        return '4'
    elif persian_room_numbers == 'بیشتر':
        return 'more'
    else:
        return False


def page_0_url():
    out = ""

    if CONFIG['house_config']['credit']['max'] != 0 or CONFIG['house_config']['credit']['min'] != 0:
        out += f"credit=" \
               f"{get_string_range(CONFIG['house_config']['credit']['min'], CONFIG['house_config']['credit']['max'])}&"

    if CONFIG['house_config']['rent']['max'] != 0 or CONFIG['house_config']['rent']['min'] != 0:
        out += f"rent={get_string_range(CONFIG['house_config']['rent']['min'], CONFIG['house_config']['rent']['max'])}&"

    if CONFIG['house_config']['size']['max'] != 0 or CONFIG['house_config']['size']['min'] != 0:
        out += f"size={get_string_range(CONFIG['house_config']['size']['min'], CONFIG['house_config']['size']['max'])}&"

    if CONFIG['house_config']['rooms'] != "":
        out += f"rooms={get_room_numbers(CONFIG['house_config']['rooms'])}&"

    if out != "" and out[-1] == '&':
        return out[:-1]

    return out


def get_more_house_info(token):
    print(f'getting additional info for {token}')

    out = {
        'land_area': '',
        'area': '',
        'year_of_construction': '',
    }

    response = requests.get(CONST['page_url'] + token)
    for i in range(1, 5):
        if response.status_code == 200:
            break
        time.sleep(i)
        response = requests.get(CONST['page_url'] + token)

    soup = BeautifulSoup(response.content, "html.parser")
    top_info = soup.find_all('div', class_='kt-group-row-item kt-group-row-item--info-row')

    for item in top_info:
        sub_items = item.find_all('span')
        if sub_items[0].text == 'متراژ':
            out['area'] = sub_items[1].text
        if sub_items[0].text == 'ساخت':
            out['year_of_construction'] = sub_items[1].text

    info = soup.find_all('div', class_='kt-base-row kt-base-row--large kt-unexpandable-row')

    for item in info:
        if item.find("p", class_='kt-base-row__title kt-unexpandable-row__title').text == 'متراژ زمین':
            out['land_area'] = item.find("p", class_='kt-unexpandable-row__value').text
            break

    return out


def get_data():
    out = []
    last_post_date = 0
    index = 0

    print('getting data from divar')

    while True:
        print(f'reading page: {index}')

        if index > 0:
            payload = {"page": index, "json_schema": payload_json_schema()}

            if last_post_date != 0:
                payload['last-post-date'] = last_post_date

            json_payload = json.dumps(payload)
            header = {"Content-Type": "application/json"}
            response = requests.post(CONST['api_url'], data=json_payload, headers=header)

        else:
            response = requests.get(CONST['api_url_page0'] + page_0_url())

        page = response.json()
        last_post_date = page['last_post_date']
        post_list = page['web_widgets']['post_list']

        if not post_list:
            break

        for post in post_list:
            if post['widget_type'] != 'POST_ROW':
                continue

            data = {x: post['data'][x] for x in
                    ['token', 'title', 'top_description_text', 'middle_description_text', 'bottom_description_text',
                     'image_count']}

            if post['data']['image_count'] > 0:
                data['image_url'] = post['data']['image_url'][1]['src']

            else:
                # placeholder for image url cuz it was a list
                data['image_url'] = ""

            data.update(get_more_house_info(data['token']))
            out.append(data)

        index += 1

    print(f'found {len(out)} posts')

    return out


def save_data(data):
    print('saving data...')

    for record in data:
        save_record(*record, is_sent=False)


def get_new_data(received_data):
    new_data = []
    all_records_tokens = [record.token for record in read_records(get_all=True)]

    for d in received_data:
        # check if token (d first index) in stored records
        if d['token'] not in all_records_tokens:
            new_data.append(d)

    return new_data


def get_house_info_string(house_info):
    text = f"**{house_info['title']}**\n\n{house_info['top_description_text']}\n" \
           f"{house_info['middle_description_text']}\n{house_info['bottom_description_text']}\n"

    if int(house_info['image_count']) > 0:
        text += f"تعداد عکس : {house_info['image_count']}\n"

    if house_info['land_area'] != "":
        text += f"متراژ زمین : {house_info['land_area']}\n"

    if house_info['area'] != "":
        text += f"متراژ خانه : {house_info['area']}\n"

    if house_info['year_of_construction'] != "":
        text += f"سال ساخت : {house_info['year_of_construction']}\n"

    text += f"\n{CONST['page_url']}{house_info['token']}"

    return text


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
            print("--- ERROR at send message---")
            print(e)

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

    return False


def notify_user(chat_id, row):
    global SEND_MESSAGES_COUNTER

    if SEND_MESSAGES_COUNTER % 20 == 0:
        print('waiting for 60sec before sending more messages')
        time.sleep(60)

    SEND_MESSAGES_COUNTER += 1

    print(row)

    if int(row['image_count']) >= 1:
        status = send_photo(chat_id, row['image_url'], get_house_info_string(row))

    else:
        status = send_message(chat_id, get_house_info_string(row))

    return status


def notify_all(chat_id, data):
    print(f'sending {len(data)} items to user {chat_id}')
    not_sent = []

    for row in data:
        sent = notify_user(chat_id, row)
        if not sent:
            print(f"couldn't sent to user {chat_id} this message :{row}")
            not_sent.append([chat_id, row])

    return not_sent


def main():
    # save old data which not sent
    not_sent_data = read_records(sent_status=False)
    # get new data from divar
    data = get_data()

    new_data = get_new_data(data)
    for chat_id in CONFIG['chat_ids']:
        not_sent_data += notify_all(chat_id, new_data)  # returns [chat_id, {}]

    # get record tokens stored in db
    record_tokens = [r.token for r in read_records(get_all=True)]

    # iterate on all gotten data
    for d in data:
        # if data doesn't already exist in db create a record for this data (assuming it is sent)
        if d['token'] not in record_tokens:
            save_record(**d, is_sent=True)
            record_tokens.append(d['token'])

    # iterate on not sent data
    if not_sent_data:
        for d in not_sent_data:
            try:
                if d[1]['token'] in record_tokens:  # which added in line 316
                    update_record(d[1]['token'], new_state=False)
            except Exception:
                if d.token in record_tokens:
                    save_record(d.token, is_sent=False)


if __name__ == '__main__':
    main()
