# from config import CONFIG
from divar_scrapper import get_all_data, exclude_new_data
# from telegram_connection import notify_all
from db_crud import read_records, save_record, update_record


def start_app(bot=None, chat_id=None):
    # get old data which not sent
    not_send_data = read_records(send_status=False)

    data = get_all_data()

    new_data = exclude_new_data(data)

    if bot:
        from telebot import send_result
        not_send_data = send_result(bot, chat_id, not_send_data)
        not_send_data.extend(send_result(bot, chat_id, new_data))

    # get all record tokens
    record_tokens = [r.token for r in read_records()]

    # iterate on all gotten data
    for d in data:
        # if data doesn't already exist in db create a record for this data (assuming it is sent)
        if d['token'] not in record_tokens:
            save_record(**d, is_sent=True)
            record_tokens.append(d['token'])

    # iterate on not sent data
    for d in not_send_data:
        try:
            if d[1]['token'] in record_tokens:
                update_record(d[1]['token'], new_state=False)
        except Exception:
            if d.token in record_tokens:
                update_record(d.token, new_state=False)
    return new_data
