from pyrogram import Client
from pyrogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton, CallbackQuery
from time import sleep
from teleconfig import *
from main import start_app
from config import CONFIG

client = Client(name=NAME, bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH, proxy=PROXY)


def filters():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton('max_credit: ' + str(CONFIG['house_config']['credit']['max']), 'cx'),
          InlineKeyboardButton('min_credit: ' + str(CONFIG['house_config']['credit']['min']), 'cn')],
         [InlineKeyboardButton('max_rent: ' + str(CONFIG['house_config']['rent']['max']), 'rx'),
          InlineKeyboardButton('min_rent: ' + str(CONFIG['house_config']['rent']['min']), 'rn')],
         [InlineKeyboardButton('rooms_No: ' + str(CONFIG['house_config']['rooms']), 'r')],
         [InlineKeyboardButton('max_size: ' + str(CONFIG['house_config']['size']['max']), 'sx'),
          InlineKeyboardButton('min_size: ' + str(CONFIG['house_config']['size']['min']), 'sn')],
         [InlineKeyboardButton('Submit', 's')]
         ])


about = 'A simple python script which collects house information (in Shiraz) from divar.ir'
save_query = []


@client.on_message()
def handle_message(bot: Client, message: Message):
    chat_id = message.chat.id
    # if message.chat.type != message.chat.type.PRIVATE:
    #     return
    if message.text:
        if message.text.startswith('/start'):
            bot.send_message(chat_id, 'Welcome to divar script',
                             reply_markup=ReplyKeyboardMarkup([['set filter'], ['about'], ['exit']],
                                                              resize_keyboard=True))
        elif message.text == 'set filter':
            bot.send_message(chat_id, 'click on the buttons to change filters', reply_markup=filters())
        elif message.text == 'about':
            bot.send_message(chat_id, about,
                             reply_markup=ReplyKeyboardMarkup([['set filter'], ['exit']], resize_keyboard=True))
        elif message.text == 'exit':
            bot.send_message(chat_id, 'have a nice time!\n/start', reply_markup=ReplyKeyboardRemove())
        elif (message.text.isdigit() or message.text == 'more') and save_query:
            if save_query[0] == 'cx':
                CONFIG['house_config']['credit']['max'] = int(message.text)
            elif save_query[0] == 'cn':
                CONFIG['house_config']['credit']['min'] = int(message.text)
            elif save_query[0] == 'rx':
                CONFIG['house_config']['rent']['max'] = int(message.text)
            elif save_query[0] == 'rn':
                CONFIG['house_config']['rent']['min'] = int(message.text)
            elif save_query[0] == 'r':
                if message.text == 'more' or int(message.text) > 4:
                    CONFIG['house_config']['rooms'] = 'بیشتر'
                else:
                    CONFIG['house_config']['rooms'] = int(message.text)
            elif save_query[0] == 'sx':
                CONFIG['house_config']['size']['max'] = int(message.text)
            elif save_query[0] == 'sn':
                CONFIG['house_config']['size']['min'] = int(message.text)
            bot.send_message(chat_id, 'click on the buttons to change filters', reply_markup=filters())
            save_query.clear()
        else:
            bot.send_message(chat_id, 'invalid message')


@client.on_callback_query()
def handle_callback_query(bot: Client, query: CallbackQuery):
    chat_id = query.message.chat.id
    if query.data == 'cx':
        bot.send_message(chat_id, 'enter max_credit: ', reply_markup=ReplyKeyboardRemove())
    elif query.data == 'cn':
        bot.send_message(chat_id, 'enter min_credit: ', reply_markup=ReplyKeyboardRemove())
    elif query.data == 'rx':
        bot.send_message(chat_id, 'enter max_rent: ', reply_markup=ReplyKeyboardRemove())
    elif query.data == 'rn':
        bot.send_message(chat_id, 'enter min_rent: ', reply_markup=ReplyKeyboardRemove())
    elif query.data == 'r':
        bot.send_message(chat_id, 'enter rooms_No: ',
                         reply_markup=ReplyKeyboardMarkup([['0', '1', '2'], ['3', '4', 'more']], resize_keyboard=True))
    elif query.data == 'sx':
        bot.send_message(chat_id, 'enter max_size: ', reply_markup=ReplyKeyboardRemove())
    elif query.data == 'sn':
        bot.send_message(chat_id, 'enter min_size: ', reply_markup=ReplyKeyboardRemove())
    elif query.data == 's':
        bot.send_message(chat_id, 'wait...', reply_markup=ReplyKeyboardRemove())
        start_app(bot, chat_id)
    save_query.clear()
    save_query.append(query.data)


def send_result(bot, chat_id, data, message):
    not_send = []
    send_data = []

    for d in data:
        try:
            if 'title' not in d:
                d['title'] = ''
            if 'top_description_text' not in d:
                d['top_description_text'] = ''
            if 'middle_description_text' not in d:
                d['middle_description_text'] = ''
            if 'bottom_description_text' not in d:
                d['bottom_description_text'] = ''
            if 'land_area' not in d:
                d['land_area'] = 'unknown'
            if 'area' not in d:
                d['area'] = 'unknown'
            if 'year_of_construction' not in d:
                d['year_of_construction'] = 'unknown'
            if 'image_url' not in d:
                d['image_url'] = ''
            text = d['title'] + '\n' + d['top_description_text'] + '\n' + d['middle_description_text'] + '\n' + d[
                'bottom_description_text'] + '\n' + 'متراژ زمین: ' + d['land_area'] + '\n' + 'متراژ: ' + d[
                       'area'] + '\n' + 'ساخت: ' + d['year_of_construction'] + '\n' + 'https://divar.ir/v/' + d[
                       'token'] + '\n' + d['image_url']
        except Exception:
            text = d.title + '\n' + d.top_description_text + '\n' + d.middle_description_text + '\n' + \
                   d.bottom_description_text + '\n' + 'متراژ زمین: ' + d.land_area + '\n' + 'متراژ: ' + \
                   d.area + '\n' + 'ساخت: ' + d.year_of_construction + '\n' + 'https://divar.ir/v/' + \
                   d.token + '\n' + d.image_url
        try:
            bot.send_message(chat_id, text)
            send_data.append(d)
        except Exception:
            sleep(3)
            not_send.append(d)
        sleep(1)
    try:
        bot.send_message(chat_id, message,
                         reply_markup=ReplyKeyboardMarkup([['set filter'], ['about'], ['exit']], resize_keyboard=True))
    except Exception as e:
        print(e)
    return not_send, send_data


if __name__ == '__main__':
    client.run()
