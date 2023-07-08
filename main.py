import requests
import json
import csv
import time
import pandas as pd
import os

with open('constants.json' , 'r') as readconst:
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

def min_max_value(min , max):
    if max>min:
        return {"max": max, "min": min}
    else:
        return {"min": min}

def payload_json_schema():
    out = { "category":{"value":"house-villa-rent"},
            "sort":{"value":"sort_date"},
            "cities":["6"]}
    
    if config['houseconfig']['districts']:
        out['districts'] = {"vacancies": get_district_code()}
    if config['houseconfig']['credit']['max'] != 0 or config['houseconfig']['credit']['min'] != 0:
        out['credit'] = min_max_value(config['houseconfig']['credit']['min'], config['houseconfig']['credit']['max'])
    if config['houseconfig']['rent']['max'] != 0 or config['houseconfig']['rent']['min'] != 0:
        out['rent'] = min_max_value(config['houseconfig']['rent']['min'], config['houseconfig']['rent']['max'])
    if config['houseconfig']['size']['max'] != 0 or config['houseconfig']['size']['min'] != 0:
        out['size'] = min_max_value(config['houseconfig']['size']['min'], config['houseconfig']['size']['max'])
    if config['houseconfig']['rooms'] != "":
        out['rooms'] = {'value' : config['houseconfig']['rooms']} 
    
    return out

def min_max_value_string(min, max):
    if max>min:
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

def get_data():
    print('getting data from divar')
    out = []
    index = 0
    while True:
        print('getting page : ',index)
        if index > 0:
            payload = {"page":index,
                       "json_schema" : payload_json_schema()}
            json_payload = json.dumps(payload)
            header = {"Content-Type": "application/json"}
            response = requests.post(const['api_url'], data=json_payload, headers=header)
        else:
            response = requests.get(const['api_url_page0']+page_0_url())
        page = response.json()
        postlist = page['web_widgets']['post_list']
        if not postlist:
            break
        for item in postlist:
            if item['widget_type'] != 'POST_ROW':
                continue
            data = {x:item['data'][x] for x in ['token', 'title', 'top_description_text', 'middle_description_text', 'bottom_description_text', 'image_count']}
            if item['data']['image_count'] > 0 :
                data['image_url'] = item['data']['image_url'][1]['src']
            else:
                # placeholder for image url cuz its a list
                data['image_url'] = ""
            out.append(data)
        index += 1
        time.sleep(1)
    print(f'found {len(out)} items')
    return out

def save_data(list):
    print('saving data...')
    with open(config['save_file'] , "w")as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(list[0])
        for item in list:
            writer.writerow(item.values())

def create_save_if_not_exist():
    if not os.path.exists(config['save_file']):
        with open(config['save_file'], 'w') as createsave:
            createwriter = csv.writer(createsave)
            createwriter.writerow(['token', 'title', 'top_description_text', 'middle_description_text', 'bottom_description_text', 'image_count', 'image_url'])

def get_data_diffrence(data):
    data1 = pd.DataFrame(data)
    data2 = pd.read_csv(config['save_file'])
    result1 = data1[~data1['token'].isin(data2['token'])]
    return result1.values.tolist()

def house_info(data):
    return f"title : {data[1]}\n\n{data[2]}\n{data[3]}\n{data[4]}\nnumber of images in website : {data[0]}\n\nlink to the item : https://divar.ir/v/{data[5]}"

def send_message(chat_id, text):
    for i in range(5):
        url = f"https://api.telegram.org/bot{config['bot_api_key']}/sendMessage"
        payload = {"chat_id" : chat_id, "text" : text}
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
        payload = {"chat_id" : chat_id, "photo" : photo_url, "caption" : caption}
        json_payload = json.dumps(payload)
        header = {"Content-Type": "application/json"}
        try:
            response = requests.post(url, data=json_payload, headers=header, proxies=config['proxies'])
            if response.status_code == 200:
                return True
        except Exception:
            pass

    return False

def save_not_sent(itemlist):
    print('saving not sent messages')
    if len(itemlist)>0:
        with open(config['not_sent_file'] , "w")as csvfile:
            writer = csv.writer(csvfile)
            for item in itemlist:
                writer.writerow(item)
    else:
        if os.path.exists(config['not_sent_file']):
            os.remove(config['not_sent_file'])

def notify_user(chat_id, row):
    global sent_messages
    if sent_messages%20 == 0:
        print('waitng for 60sec befor sending more messages')
        time.sleep(60)
    sent_messages += 1
    if int(row[5]) >= 1:
        status= send_photo(chat_id, row[6], house_info(row))
    else:
        status= send_message(chat_id, house_info(row))
    return status

def notify_all(chat_id,data):
    print(f'sending {len(data)} items to user {chat_id}')
    not_sent = []
    for row in data:
        sent = notify_user(chat_id , row)
        if not sent:
            print(f"coudnt sent to user {chat_id} this message :{row}")
            not_sent.append([chat_id] + row)
    
    return not_sent

def get_not_sent_data():
    out = []
    if os.path.exists(config['not_sent_file']):
        with open(config['not_sent_file'] , "r")as csvfile:
            reader = csv.reader(csvfile)
            for item in reader:
                out.append(item)
    return out

def main():
    not_sent_data = []
    for item in get_not_sent_data():
        if not notify_user(item[0], item[1:]):
            not_sent_data.append(item)
    data = get_data()
    create_save_if_not_exist()
    for chat_id in config['chat_ids']:
        not_sent_data += (notify_all(chat_id, get_data_diffrence(data)))
    save_not_sent(not_sent_data)
    save_data(data)

if __name__=='__main__':
    main()