from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from local_settings import postgresql as settings


def get_engine(user, password, host, port, db):
    url = f'postgresql://{user}:{password}@{host}:{port}/{db}'
    if not database_exists(url):
        create_database(url)
    engine = create_engine(url, pool_size=1, echo=False)
    return engine


def get_engine_from_settings():
    return get_engine(settings['user'], settings['password'], settings['host'], settings['port'], settings['db'])


def get_session():
    engine = get_engine_from_settings()
    session = sessionmaker(bind=engine)()
    return engine, session
