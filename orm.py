from datetime import date
from app import db, app
from sqlalchemy import Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from helpers.config import config
import os
from icecream import ic
import cv2


class ImageModel(db.Model):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    original_name: Mapped[str] = mapped_column(String(50), nullable=False)
    date_uploaded: Mapped[date] = mapped_column(Date, default=date.today())
    date_updated: Mapped[date] = mapped_column(
        Date, default=date.today(), onupdate=date.today()
    )
    extension: Mapped[str] = mapped_column(String(6), nullable=False)
    status: Mapped[str] = mapped_column(String(15), default="Added")

    def __init__(self, name: str, or_name: str, extension: str):
        self.name = name
        self.original_name = or_name
        self.extension = extension

    @classmethod
    def getAll(cls):
        return cls.query.all()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def updateStatus(self, status: str):
        with app.app_context():
            row_changed = ImageModel.query.filter_by(id = self.id).update(dict(status=status))
            db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def getById(cls, id: int):
        model = cls.query.filter_by(id=id).first()
        if type(model) is ImageModel:
            return model
        else:
            return None

    def toJson(self):
        return {
            "id": self.id,
            "name": self.name,
            "dateUploaded": self.date_uploaded,
            "dateUpdated": self.date_updated,
            "previewUrl": f"/image_preview/{self.id}",
            "contentUrl": f"/image/{self.id}",
            "type": "Image",
        }

    @classmethod
    def create(cls, name: str, or_name: str, extension: str):
        model = ImageModel(name, or_name, extension)
        model.save()
        return model

    @classmethod
    def getPathById(cls, id: int):
        model = cls.getById(id)
        name = ""
        if type(model) is ImageModel:
            name = model.original_name
        else:
            raise Exception(f"No image with id - {id}!")
        # ic(name)
        return os.path.join(config["images_folders"], f"{name}_{id}")

    @classmethod
    def getStatusById(cls, id: int):
        model = cls.getById(id)
        if type(model) is ImageModel:
            return model.status
        else:
            raise Exception(f"No image with id - {id}!")

    def getPath(self):
        return os.path.join(config["images_folders"], f"{self.original_name}_{self.id}")


class VideoModel(db.Model):
    __tablename__ = "videos"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    original_name: Mapped[str] = mapped_column(String(50), nullable=False)

    date_uploaded: Mapped[date] = mapped_column(Date, default=date.today())
    date_updated: Mapped[date] = mapped_column(
        Date, default=date.today(), onupdate=date.today()
    )
    extension: Mapped[str] = mapped_column(String(6), nullable=False)
    status: Mapped[str] = mapped_column(String(15), default="Added")

    def __init__(self, name: str, or_name: str, extension: str):
        self.name = name
        self.original_name = or_name
        self.extension = extension

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

    def updateStatus(self, status: str):
        with app.app_context():
            row_changed = VideoModel.query.filter_by(id = self.id).update(dict(status=status))
            db.session.commit()

    @classmethod
    def getById(cls, id: int):
        model = cls.query.filter_by(id=id).first()
        if type(model) is VideoModel:
            return model
        return None

    def toJson(self):
        return {
            "id": self.id,
            "name": self.name,
            "dateUploaded": self.date_uploaded,
            "dateUpdated": self.date_updated,
            "previewUrl": f"/video_preview/{self.id}",
            "contentUrl": f"/video/{self.id}",
            "type": "Video",
        }

    @classmethod
    def create(cls, name: str, or_name: str, extension: str):
        model = VideoModel(name, or_name, extension)
        model.save()
        ic(model.extension)
        return model

    def createPreview(self):
        # Откроем видео
        path = self.getPath()
        ic(path)
        ic(os.path.join(path, f"original{self.extension}"))
        video = cv2.VideoCapture(os.path.join(path, f"original{self.extension}"))

        # Получим кадр
        ret, frame = video.read()

        # Сохраним его
        if ret:
            ic()
            cv2.imwrite(os.path.join(path, "preview.png"), frame)
        video.release()

    @classmethod
    def getPathById(cls, id: int):
        model = cls.getById(id)
        name = ""
        if type(model) is VideoModel:
            name = model.original_name
        else:
            raise Exception(f"No video with id - {id}")
        return os.path.join(config["videos_folders"], f"{name}_{id}")

    @classmethod
    def getStatusById(cls, id: int):
        model = cls.getById(id)
        if type(model) is VideoModel:
            return model.status
        else:
            raise Exception(f"No video with id - {id}")

    def getPath(self):
        return os.path.join(
            config["videos_folders"], f"{self.original_name}_{self.id}/"
        )


with app.app_context():
    db.create_all()
