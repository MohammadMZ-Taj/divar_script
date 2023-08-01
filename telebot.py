from pyrogram import Client
from pyrogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton, CallbackQuery
from teleconfig import *
from main import CONFIG, start_app

client = Client(name=NAME, bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH, proxy=PROXY)

data = []


class MyUser:
    def __init__(self, user_id):
        self.id = user_id
        self.state = 0


def check_user(user_id: MyUser):
    for user in data:
        if user_id == user.id:
            return user
    new_user = MyUser(user_id)
    data.append(new_user)
    return new_user


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
        if message.text == '/start':
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
        bot.send_message(chat_id, 'enter max_credit: ')
    elif query.data == 'cn':
        bot.send_message(chat_id, 'enter min_credit: ')
    elif query.data == 'rx':
        bot.send_message(chat_id, 'enter max_rent: ')
    elif query.data == 'rn':
        bot.send_message(chat_id, 'enter min_rent: ')
    elif query.data == 'r':
        bot.send_message(chat_id, 'enter rooms_No: ',
                         reply_markup=ReplyKeyboardMarkup([['0', '1', '2'], ['3', '4', 'more']], resize_keyboard=True))
    elif query.data == 'sx':
        bot.send_message(chat_id, 'enter max_size: ')
    elif query.data == 'sn':
        bot.send_message(chat_id, 'enter min_size: ')
    elif query.data == 's':
        bot.send_message(chat_id, 'wait...', reply_markup=ReplyKeyboardRemove())
        records = start_app()
        for r in records:
            if 'title' not in r:
                r['title'] = ''
            if 'top_description_text' not in r:
                r['top_description_text'] = ''
            if 'middle_description_text' not in r:
                r['middle_description_text'] = ''
            if 'bottom_description_text' not in r:
                r['bottom_description_text'] = ''
            if 'land_area' not in r:
                r['land_area'] = 'unknown'
            if 'area' not in r:
                r['area'] = 'unknown'
            if 'year_of_construction' not in r:
                r['year_of_construction'] = 'unknown'
            if 'image_url' not in r:
                r['image_url'] = ''
            text = r['title'] + '\n' + r['top_description_text'] + '\n' + r['middle_description_text'] + '\n' + r[
                'bottom_description_text'] + '\n' + 'متراژ زمین: ' + r['land_area'] + '\n' + 'متراژ: ' + r[
                       'area'] + '\n' + 'ساخت: ' + r['year_of_construction'] + '\n' + 'https://divar.ir/v/' + r[
                       'token'] + '\n' + r['image_url']
            bot.send_message(chat_id, text)
        bot.send_message(chat_id, 'finish',
                         reply_markup=ReplyKeyboardMarkup([['set filter'], ['about'], ['exit']], resize_keyboard=True))
    save_query.clear()
    save_query.append(query.data)


if __name__ == '__main__':
    client.run()
