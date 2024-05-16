from datetime import date
from app import db, app
from sqlalchemy import Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class ImageModel(db.Model):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    date_uploaded: Mapped[date] = mapped_column(
        Date, default=date.today(), onupdate=date.today()
    )
    date_updated: Mapped[date] = mapped_column(
        Date, default=date.today(), onupdate=date.today()
    )

    def __init__(self, name: str):
        self.name = name

    @classmethod
    def getAll(cls):
        return cls.query.all()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def getById(cls, id: int):
        return db.queary.filter_by(id=id).first()

    @classmethod
    def create(cls, name: str):
        model = ImageModel(name)
        model.save()
        return model


class VideoModel(db.Model):
    __tablename__ = "videos"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    date_uploaded: Mapped[date] = mapped_column(
        Date, default=date.today(), onupdate=date.today()
    )
    date_updated: Mapped[date] = mapped_column(
        Date, default=date.today(), onupdate=date.today()
    )

    def __init__(self, name: str):
        self.name = name

    @classmethod
    def getAll(cls):
        return cls.query.all()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def getById(cls, id: int):
        return db.queary.filter_by(id=id).first()

    @classmethod
    def create(cls, name: str):
        model = VideoModel(name)
        model.save()
        return model


with app.app_context():
    db.create_all()
