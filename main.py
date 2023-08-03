from divar_scrapper import get_all_data, exclude_new_data

from db_crud import read_records, save_record, update_record
from db_model import Record
from constants import CONST


def start_app(bot=None, chat_id=None):
    # get old data which not sent
    not_send_data = read_records(send_status=False)
    send_data = []

    data = get_all_data()

    new_data = exclude_new_data(data)

    if bot and chat_id:
        from telebot import send_result
        not_send = send_result(bot, chat_id, not_send_data, '...')
        send_data = [d for d in not_send_data if d not in not_send]
        not_send_data = not_send
        not_send_data.extend(send_result(bot, chat_id, new_data, 'finish'))
        send_data.extend([d for d in new_data if d not in not_send_data])

    for d in send_data:
        if type(d) == Record:
            update_record(d.token, True)
        else:
            save_record(**d, is_sent=True)

    for d in not_send_data:
        if type(d) != Record:
            save_record(**d, is_sent=False)

    return new_data


if __name__ == '__main__':
    from telebot import client
    client.start()
    start_app(bot=client, chat_id=CONST["chat_id"])
