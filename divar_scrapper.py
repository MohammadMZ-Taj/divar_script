import requests
import time
import json
from bs4 import BeautifulSoup

from config import CONFIG
from constants import CONST
from db_crud import read_records


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


def get_0_page_url():
    url = ""

    if CONFIG['house_config']['credit']['max'] != 0 or CONFIG['house_config']['credit']['min'] != 0:
        url += f"credit=" \
               f"{get_string_range(CONFIG['house_config']['credit']['min'], CONFIG['house_config']['credit']['max'])}&"

    if CONFIG['house_config']['rent']['max'] != 0 or CONFIG['house_config']['rent']['min'] != 0:
        url += f"rent={get_string_range(CONFIG['house_config']['rent']['min'], CONFIG['house_config']['rent']['max'])}&"

    if CONFIG['house_config']['size']['max'] != 0 or CONFIG['house_config']['size']['min'] != 0:
        url += f"size={get_string_range(CONFIG['house_config']['size']['min'], CONFIG['house_config']['size']['max'])}&"

    if CONFIG['house_config']['rooms'] != "":
        url += f"rooms={get_room_numbers(CONFIG['house_config']['rooms'])}&"

    if url != "" and url[-1] == '&':
        return url[:-1]

    return url


def payload_json_schema():
    out = {
        "category": {"value": "house-villa-rent"},
        "sort": {"value": "sort_date"},
        "cities": ["6"]
    }

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


def get_more_post_info(token):
    print(f'getting additional info for {token}')

    result = {
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

    for tag in top_info:
        sub_items = tag.find_all('span')

        if sub_items[0].text == 'متراژ':
            result['area'] = sub_items[1].text
        if sub_items[0].text == 'ساخت':
            result['year_of_construction'] = sub_items[1].text

    info = soup.find_all('div', class_='kt-base-row kt-base-row--large kt-unexpandable-row')

    for item in info:
        if item.find("p", class_='kt-base-row__title kt-unexpandable-row__title').text == 'متراژ زمین':
            result['land_area'] = item.find("p", class_='kt-unexpandable-row__value').text
            break

    return result


def get_all_home_data():
    all_home_data = []
    last_post_date = 0
    page_number = 0

    print('getting data from divar ...')

    while True:
        print(f'reading page: {page_number}')

        if page_number > 0:
            payload = {"page": page_number, "json_schema": payload_json_schema()}

            if last_post_date != 0:
                payload['last-post-date'] = last_post_date

            json_payload = json.dumps(payload)
            request_header = {"Content-Type": "application/json"}
            response = requests.post(CONST['api_url'], data=json_payload, headers=request_header)

        else:
            response = requests.get(CONST['api_url_0_page'] + get_0_page_url())

        page = response.json()
        last_post_date = page['last_post_date']
        post_list = page['web_widgets']['post_list']

        if not post_list:
            break

        for post in post_list:
            if post['widget_type'] == 'POST_ROW':
                post_data = {entry: post['data'][entry] for entry in ['token',
                                                                      'title',
                                                                      'top_description_text',
                                                                      'middle_description_text',
                                                                      'bottom_description_text',
                                                                      'image_count']
                             }

                if post['data']['image_count'] > 0:  # if post has image
                    post_data['image_url'] = post['data']['image_url'][1]['src']

                # getting area, land area and year of construction
                more_info = get_more_post_info(post_data['token'])
                post_data.update(more_info)
                all_home_data.append(post_data)

        page_number += 1

    print(f'{len(all_home_data)} post(s) found.')

    return all_home_data


def exclude_new_data(received_data):
    new_data = []
    all_tokens = [record.token for record in read_records()]

    for d in received_data:
        # check if token (d first index) in stored records
        if d['token'] not in all_tokens:
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
