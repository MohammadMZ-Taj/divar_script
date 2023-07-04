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
# tartibe data avaz shode dorosesh kon
# not_sent data ok she
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
    if config['houseconfig']['credit']['max'] != 0 and config['houseconfig']['credit']['min'] != 0:
        out['credit'] = min_max_value(config['houseconfig']['credit']['min'], config['houseconfig']['credit']['max'])
    if config['houseconfig']['rent']['max'] != 0 and config['houseconfig']['rent']['min'] != 0:
        out['rent'] = min_max_value(config['houseconfig']['rent']['min'], config['houseconfig']['rent']['max'])
    if config['houseconfig']['size']['max'] != 0 and config['houseconfig']['size']['min'] != 0:
        out['size'] = min_max_value(config['houseconfig']['size']['min'], config['houseconfig']['size']['max'])
    if config['houseconfig']['rooms'] != "":
        out['rooms'] = {'value' : config['houseconfig']['rooms']} 
    
    return out

def get_data():
    print('getting data from divar')
    out = [['token', 'title', 'top_description_text', 'middle_description_text', 'bottom_description_text', 'image_count', 'image_url']]
    index = 0
    while True:
        print('getting page : ',index)
        payload = {"page":index,
                   "json_schema" : payload_json_schema()}
        json_payload = json.dumps(payload)
        header = {"Content-Type": "application/json"}
        response = requests.post(const['api_url'], data=json_payload, headers=header)
        page = response.json()
        postlist = page['web_widgets']['post_list']
        if not postlist:
            break
        for item in postlist:
            if item['widget_type'] != 'POST_ROW':
                continue
            # data = [item['data'][x] for x in item['data'] if x in ['token', 'title', 'top_description_text', 'middle_description_text', 'bottom_description_text', 'image_count']]
            temp = item['data']
            data = [temp['token'], temp['title'], temp['top_description_text'], temp['middle_description_text'], temp['bottom_description_text'], temp['image_count']]
            if item['data']['image_count'] > 0 :
                data.append(item['data']['image_url'][1]['src'])
            else:
                # placeholder for image url cuz its a list
                data.append("")
            out.append(data)
        index += 1
        time.sleep(1)
    print(f'found {len(out)-1} items')
    return out

def save_data(list):
    print('saving data...')
    with open(config['save_file'] , "w")as csvfile:
        writer = csv.writer(csvfile)
        for item in list:
            writer.writerow(item)

def create_save_if_not_exist():
    if not os.path.exists(config['save_file']):
        with open(config['save_file'], 'w') as createsave:
            createwriter = csv.writer(createsave)
            createwriter.writerow(['token', 'title', 'top_description_text', 'middle_description_text', 'bottom_description_text', 'image_count', 'image_url'])

def get_data_diffrence(data):
    data1 = pd.DataFrame(data[1:],columns=data[0])
    data2 = pd.read_csv(config['save_file'])
    result1 = data1[~data1['token'].isin(data2['token'])]
    return result1.values.tolist()

def house_info(data):
    return f"title : {data[1]}\n\n{data[2]}\n{data[3]}\n{data[4]}\nnumber of images in website : {data[5]}\n\nlink to the item : https://divar.ir/v/{data[0]}"

def send_message(chat_id, text):
    for i in range(5):
        url = f"https://api.telegram.org/bot{config['bot_api_key']}/sendMessage"
        payload = {"chat_id" : chat_id, "text" : text}
        json_payload = json.dumps(payload)
        header = {"Content-Type": "application/json"}
        try:
            response = requests.post(url, data=json_payload, headers=header, proxies=config['proxies'])
        except Exception:
            return False
        if response.status_code == 200:
            return True
    return False

def send_photo(chat_id, photo_url, caption):
    for i in range(5):
        url = f"https://api.telegram.org/bot{config['bot_api_key']}/sendPhoto"
        payload = {"chat_id" : chat_id, "photo" : photo_url, "caption" : caption}
        json_payload = json.dumps(payload)
        header = {"Content-Type": "application/json"}
        try:
            response = requests.post(url, data=json_payload, headers=header, proxies=config['proxies'])
        except Exception:
            return False
        if response.status_code == 200:
            return True
    return False

def save_not_sent(itemlist):
    with open(config['not_sent_file'] , "w")as csvfile:
        writer = csv.writer(csvfile)
        for item in itemlist:
            writer.writerow(item)

def notify_user(chat_id, row):
    if row[5] >= 1:
        status= send_photo(chat_id, row[6], house_info(row))
    else:
        status= send_message(chat_id, house_info(row))
    return status

def notify_all(chat_id,data):
    print(f'sending {len(data)} items to user {chat_id}')
    not_sent = []
    for i, row in enumerate(data):
        # if i >= 19:
        #     print('waitng for 60sec befor sending more messages')
        #     time.sleep(60)
        sent = notify_user(chat_id , row)
        if not sent:
            print(f"coudnt sent to user {chat_id} this message :{row}")
            not_sent.append([chat_id] + row)
    print('saving not sent messages')
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
    get_not_sent_data()
    create_save_if_not_exist()
    data = get_data()

    for chat_id in config['chat_ids']:
        notify_all(chat_id, get_data_diffrence(data))
    save_data(data)

if __name__=='__main__':
    main()