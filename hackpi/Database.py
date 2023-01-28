from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DatabasePath = str

Base = declarative_base()


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta,cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class SingletonClass(metaclass=SingletonMeta):
    pass


class Database(SingletonClass):
    def __init__(self, path: DatabasePath):
        self.__engine = create_engine(path)
        self.__session = sessionmaker(self.__engine, expire_on_commit=False, autoflush=False)

    def get_session(self):
        session = self.__session()

        try:
            yield session
        finally:
            session.close()

    def create_all(self):
        Base.metadata.create_all(self.__engine)
