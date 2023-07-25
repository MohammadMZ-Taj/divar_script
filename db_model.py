from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Record(Base):
    __tablename__ = 'Records'

    token = Column("token", String, unique=True, primary_key=True)
    title = Column("title", String)
    top_description_text = Column("top description text", String)
    middle_description_text = Column("middle description text", String)
    bottom_description_text = Column("bottom description text", String)
    image_count = Column("image count", Integer)
    image_url = Column("image_url", String)
    land_area = Column("land area", String)
    area = Column("area", String)
    year_of_construction = Column("year_of_construction", String)
    is_sent = Column("is sent", Boolean, default=False)

    def __init__(self, token, title, top_description_text, middle_description_text, bottom_description_text,
                 image_count,
                 image_url, land_area, area, year_of_construction):
        self.token = token
        self.title = title
        self.top_description_text = top_description_text
        self.middle_description_text = middle_description_text
        self.bottom_description_text = bottom_description_text
        self.image_count = image_count
        self.image_url = image_url
        self.land_area = land_area
        self.area = area
        self.year_of_construction = year_of_construction
        self.is_sent = is_sent

    def __repr__(self):
        return f"{self.title}-{self.year_of_construction} ({self.top_description_text})"
