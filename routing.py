from flask import send_from_directory
from flask_cors import cross_origin
from app import app
from orm import ImageModel, VideoModel
from helpers.upload import allowed_img, allowed_video, create_needed_folder
from werkzeug.utils import secure_filename
from icecream import ic
from helpers.parser import uploadParser
from helpers.config import config
import os


@app.route("/all_media", methods=["GET"])
def get_all_media():
    """
    Возвращает все видео и изображения из бд
    returns:
        json - [media_type], где media_type = {"id", "name", "date_uploaded", "date_updated", "type" : "Video"|"Image"}
    """
    data = [model.toJson() for model in ImageModel.query.all() + VideoModel.query.all()]

    return data, 200


@app.route("/video_preview/<id>", methods=["GET"])
def get_video_preiview(id: int):
    path = VideoModel.getPathById(id)
    return send_from_directory(path, "preview.png"), 200


@app.route("/video/<id>", methods=["POST"])
def get_video(id: int):
    return "Hello"


@app.route("/image_preview/<id>", methods=["GET"])
def get_image_preview(id: int):
    # ic(id)
    path = ImageModel.getPathById(id)
    # Надо найти в path original.[png|jpg|jpeg]
    for file in os.listdir(path):
        if "original" in file:
            return send_from_directory(path, file), 200
    return {"message": "No preview"}, 404


@app.route("/image/<id>", methods=["GET"])
def get_image(id: int):
    return "Hello"


@app.route("/upload", methods=["POST"])
@cross_origin()
def upload_media():
    data = uploadParser.parse_args()
    file = data["file"]
    filename, extension = os.path.splitext(file.filename)
    ic(filename)
    ic(extension)
    filename = secure_filename(filename)
    name = secure_filename(data["name"])
    if allowed_img(file.filename):
        # Сохраним в папку config['images_folders']/<название файла>_<номер id>/original.<расширение>
        model = ImageModel.create(name, filename, extension)
        path = f"{config['images_folders']}/{filename}_{model.id}"
        create_needed_folder(path)
        file.save(f"{path}/original.{extension}")
        return {"message": "Image uploaded"}, 201

    if allowed_video(file.filename):
        # Сохраним в папку config['videos_folders']/<название файла>_<номер id>/original.<расширение>
        model = VideoModel.create(name, filename, extension)
        path = f"{config['videos_folders']}/{filename}_{model.id}"
        create_needed_folder(path)
        file.save(f"{path}/original.{extension}")
        model.createPreview()
        return {"message": "Video uploaded"}, 201
    return {"message": "Wrong file type"}, 400
