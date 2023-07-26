from db_model import Record, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///mydb.db", echo=True)
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(bind=engine)


def read_records(sent_status=True, get_all=False):
    if get_all:
        return session.query(Record).all()
    return session.query(Record).filter(Record.is_sent == sent_status).all()


def update_record(record_token, new_state):
    record = session.query(Record).filter(Record.token == record_token).all()[0]
    record.is_sent = new_state
    session.commit()


def save_record(token, title, top_description_text, middle_description_text, bottom_description_text, image_count,
                image_url, land_area, area, year_of_construction, is_sent):
    try:
        record = Record(token, title, top_description_text, middle_description_text, bottom_description_text,
                        image_count,
                        image_url, land_area, area, year_of_construction, is_sent)
        session.add(record)
        session.commit()
        return True
    except:
        return False
