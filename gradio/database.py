from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

# Создадим базу данных для изображений и видео (sqlite)

engine = create_engine("sqlite:///data.db")

Base = declarative_base()


class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True)
    date_upload = Column(DateTime, default=func.now())
    date_modify = Column(DateTime, default=func.now())
    name = Column(String(255))
    path = Column(String(255))

    def __init__(self, name, path):
        self.name = name
        self.path = path

    def update(self):
        """
        Записывает в базу данных измененую информацию об обекте
        """
        self.date_modify = func.now()
        with sessionmaker(bind=engine)() as session:
            session.commit()

    def delete(self):
        """
        Удаляет из базы данных обект
        """
        with sessionmaker(bind=engine)() as session:
            session.delete(self)


class Video(Base):
    __tablename__ = "videos"
    id = Column(Integer, primary_key=True)
    date_upload = Column(DateTime, default=func.now())
    date_modify = Column(DateTime, default=func.now())
    name = Column(String(255))
    path = Column(String(255))

    def __init__(self, name, path):
        self.name = name
        self.path = path

    def update(self):
        """
        Записывает в базу данных измененую информацию об обекте
        """
        self.date_modify = func.now()
        with sessionmaker(bind=engine)() as session:
            session.commit()

    def delete(self):
        """
        Удаляет из базы данных обект
        """
        with sessionmaker(bind=engine)() as session:
            session.delete(self)
