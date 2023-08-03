from db_model import Record, Base
from engine_session import get_session

engine, session = get_session()
Base.metadata.create_all(bind=engine)


def read_records(send_status=None):
    if send_status is None:
        return session.query(Record).all()
    return session.query(Record).filter(Record.is_sent == send_status).all()


def update_record(record_token, new_state):
    record = session.query(Record).filter(Record.token == record_token)[0]
    record.is_sent = new_state
    session.commit()


def save_record(token, title, top_description_text, middle_description_text, bottom_description_text, image_count,
                land_area, area, year_of_construction, is_sent, image_url=None):
    try:
        record = Record(token, title, top_description_text, middle_description_text, bottom_description_text,
                        image_count,
                        image_url, land_area, area, year_of_construction, is_sent)
        session.add(record)
        session.commit()
    except Exception as e:
        print(f"{type(e)} at save_record : {e}")


def find_record(token):
    return session.query(Record).filter(Record.token == token)
