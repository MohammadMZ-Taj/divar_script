import requests
import json
import time
from bs4 import BeautifulSoup
from db_crud import read_records, save_record, update_record

with open('constants.json', 'r') as readconst:
    const = json.load(readconst)
with open('config.json', 'r', encoding='utf-8') as readconfig:
    config = json.load(readconfig)

sent_messages = 1


def get_district_code():
    out = []
    for district in config['houseconfig']['districts']:
        if district in const['district_codes']:
            out.append(const['district_codes'][district])
        else:
            print(district + ' was not found')
            raise ValueError
    return out


def min_max_value(min, max):
    if max > min:
        return {"max": max, "min": min}
    else:
        return {"min": min}


def payload_json_schema():
    out = {"category": {"value": "house-villa-rent"},
           "sort": {"value": "sort_date"},
           "cities": ["6"]}

    if config['houseconfig']['districts']:
        out['districts'] = {"vacancies": get_district_code()}
    if config['houseconfig']['credit']['max'] != 0 or config['houseconfig']['credit']['min'] != 0:
        out['credit'] = min_max_value(config['houseconfig']['credit']['min'], config['houseconfig']['credit']['max'])
    if config['houseconfig']['rent']['max'] != 0 or config['houseconfig']['rent']['min'] != 0:
        out['rent'] = min_max_value(config['houseconfig']['rent']['min'], config['houseconfig']['rent']['max'])
    if config['houseconfig']['size']['max'] != 0 or config['houseconfig']['size']['min'] != 0:
        out['size'] = min_max_value(config['houseconfig']['size']['min'], config['houseconfig']['size']['max'])
    if config['houseconfig']['rooms'] != "":
        out['rooms'] = {'value': config['houseconfig']['rooms']}

    return out


def min_max_value_string(min, max):
    if max > min:
        return f"{min}-{max}"
    else:
        return f"{min}-"


def rooms_to_eng(string):
    if string == 'بدون اتاق':
        return 'noroom'
    elif string == 'یک':
        return '1'
    elif string == 'دو':
        return '2'
    elif string == 'سه':
        return '3'
    elif string == 'چهار':
        return '4'
    elif string == 'بیشتر':
        return 'more'


def page_0_url():
    out = ""
    if config['houseconfig']['credit']['max'] != 0 or config['houseconfig']['credit']['min'] != 0:
        out += f"credit={min_max_value_string(config['houseconfig']['credit']['min'], config['houseconfig']['credit']['max'])}&"
    if config['houseconfig']['rent']['max'] != 0 or config['houseconfig']['rent']['min'] != 0:
        out += f"rent={min_max_value_string(config['houseconfig']['rent']['min'], config['houseconfig']['rent']['max'])}&"
    if config['houseconfig']['size']['max'] != 0 or config['houseconfig']['size']['min'] != 0:
        out += f"size={min_max_value_string(config['houseconfig']['size']['min'], config['houseconfig']['size']['max'])}&"
    if config['houseconfig']['rooms'] != "":
        out += f"rooms={rooms_to_eng(config['houseconfig']['rooms'])}&"
    if out != "" and out[-1] == '&':
        return out[:-1]
    return out


def get_more_info(token):
    print(f'getting additional info for {token}')
    out = {'land_area': '',
           'area': '',
           'year_of_construction': ''}
    for _ in range(5):
        response = requests.get(const['page_url'] + token)
        if response.status_code == 200:
            break
        time.sleep(1)
    soup = BeautifulSoup(response.content, "html.parser")
    top_info = soup.find_all('div', class_='kt-group-row-item kt-group-row-item--info-row')
    for item in top_info:
        subitems = item.find_all('span')
        if subitems[0].text == 'متراژ':
            out['area'] = subitems[1].text
        if subitems[0].text == 'ساخت':
            out['year_of_construction'] = subitems[1].text
    info = soup.find_all('div', class_='kt-base-row kt-base-row--large kt-unexpandable-row')
    for item in info:
        if item.find("p", class_='kt-base-row__title kt-unexpandable-row__title').text == 'متراژ زمین':
            out['land_area'] = item.find("p", class_='kt-unexpandable-row__value').text
            break
    return out


def get_data():
    print('getting data from divar')
    out = []
    last_post_date = 0
    index = 0
    while True:
        print('getting page : ', index)
        if index > 0:
            payload = {"page": index,
                       "json_schema": payload_json_schema()}
            if last_post_date != 0:
                payload['last-post-date'] = last_post_date
            json_payload = json.dumps(payload)
            header = {"Content-Type": "application/json"}
            response = requests.post(const['api_url'], data=json_payload, headers=header)
        else:
            response = requests.get(const['api_url_page0'] + page_0_url())
        page = response.json()
        last_post_date = page['last_post_date']
        postlist = page['web_widgets']['post_list']
        if not postlist:
            break
        for item in postlist:
            if item['widget_type'] != 'POST_ROW':
                continue
            data = {x: item['data'][x] for x in
                    ['token', 'title', 'top_description_text', 'middle_description_text', 'bottom_description_text',
                     'image_count']}
            if item['data']['image_count'] > 0:
                data['image_url'] = item['data']['image_url'][1]['src']
            else:
                # placeholder for image url cuz it was a list
                data['image_url'] = ""
            data.update(get_more_info(data['token']))
            out.append(data)
        index += 1
    print(f'found {len(out)} items')
    return out


def save_data(list):
    print('saving data...')
    for record in list:
        save_record(*record, is_sent=False)


def get_data_diffrence(data):
    new_data = []
    all_records_tokens = [record.token for record in read_records(get_all=True)]
    for d in data:
        # check if token (d first index) in stored records
        if not d['token'] in all_records_tokens:
            new_data.append(d)
    return new_data


def house_info(data):
    text = f"**{data['title']}**\n\n{data['top_description_text']}\n{data['middle_description_text']}\n{data['bottom_description_text']}\n"
    if int(data['image_count']) > 0:
        text += f"تعداد عکس : {data['image_count']}\n"
    if data['land_area'] != "":
        text += f"متراژ زمین : {data['land_area']}\n"
    if data['area'] != "":
        text += f"متراژ خانه : {data['area']}\n"
    if data['year_of_construction'] != "":
        text += f"سال ساخت : {data['year_of_construction']}\n"
    text += f"\n{const['page_url']}{data['token']}"
    return text


def send_message(chat_id, text):
    for i in range(5):
        url = f"https://api.telegram.org/bot{config['bot_api_key']}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        json_payload = json.dumps(payload)
        header = {"Content-Type": "application/json"}
        try:
            response = requests.post(url, data=json_payload, headers=header, proxies=config['proxies'])
            if response.status_code == 200:
                return True
        except Exception:
            pass
    return False


def send_photo(chat_id, photo_url, caption):
    for i in range(5):
        url = f"https://api.telegram.org/bot{config['bot_api_key']}/sendPhoto"
        payload = {"chat_id": chat_id, "photo": photo_url, "caption": caption}
        json_payload = json.dumps(payload)
        header = {"Content-Type": "application/json"}
        try:
            response = requests.post(url, data=json_payload, headers=header, proxies=config['proxies'])
            if response.status_code == 200:
                return True
        except Exception:
            pass

    return False


def notify_user(chat_id, row):
    global sent_messages
    if sent_messages % 20 == 0:
        print('waitng for 60sec befor sending more messages')
        time.sleep(60)
    sent_messages += 1
    print(row)
    if int(row['image_count']) >= 1:
        status = send_photo(chat_id, row['image_url'], house_info(row))
    else:
        status = send_message(chat_id, house_info(row))
    return status


def notify_all(chat_id, data):
    print(f'sending {len(data)} items to user {chat_id}')
    not_sent = []
    for row in data:
        sent = notify_user(chat_id, row)
        if not sent:
            print(f"coudnt sent to user {chat_id} this message :{row}")
            not_sent.append([chat_id, row])

    return not_sent


def main():
    # save old data which not sent
    not_sent_data = read_records(sent_status=False)
    # get new data from divar
    data = get_data()

    for chat_id in config['chat_ids']:
        not_sent_data += (notify_all(chat_id, get_data_diffrence(data)))

    # get record tokens stored in db
    record_tokens = [r.token for r in read_records(get_all=True)]

    # iterate on all gotten data
    for d in data:
        if d['token'] in record_tokens:  # if data already exits in db update its sent status to True
            update_record(d['token'], new_state=True)
        else:  # and if data doesn't exist, create a record for this data (assuming it is sent)
            save_record(**d, is_sent=True)

    # iterate on not sent data
    for d in not_sent_data:
        if d[1]['token'] in record_tokens:
            # if it is already stored in db and now we understood it isn't sent, update its sent status to False
            update_record(d[1]['token'], new_state=False)
        else:  # else it isn't stored in db , store it with False status
            save_record(**d[1], is_sent=False)


if __name__ == '__main__':
    main()
