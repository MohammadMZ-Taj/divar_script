from db_model import Record, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///mydb.db", echo=True)
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(bind=engine)


def read_record():
    return session.query(Record).all()


def save_record(token, title, top_description_text, middle_description_text, bottom_description_text, image_count,
              image_url, land_area, area, year_of_construction):
    try:
        record = Record(token, title, top_description_text, middle_description_text, bottom_description_text,
                        image_count,
                        image_url, land_area, area, year_of_construction)
        session.add(record)
        session.commit()
        return True
    except:
        return False
