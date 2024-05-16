from flask_cors import cross_origin
from app import app
from orm import ImageModel, VideoModel
from helpers.upload import allowed_img, allowed_video, create_needed_folder
from flask import request
import json
from werkzeug.utils import secure_filename
from icecream import ic
from helpers.parser import uploadParser

config = json.load(open("config.json"))


@app.route("/all_media", methods=["POST"])
def get_all_media():
    return "Hello"


@app.route("/video/<id>", methods=["POST"])
def get_video(id):
    return "Hello"


@app.route("/image/<id>", methods=["POST"])
def get_image(id):
    return "Hello"


@app.route("/upload", methods=["POST"])
@cross_origin()
def upload_media():
    ic()
    data = uploadParser.parse_args()
    ic()
    file = data["file"]
    ic(file)
    if allowed_img(file.filename):
        # Достанем изображение
        ic()
        filename = secure_filename(file.filename)
        name = request.form["name"]
        filename_without_ext = filename.split(".")[0]
        # Сохраним в папку config['images_folders']/<название файла>_<номер id>/original.<расширение>
        # model = ImageModel.create(filename)
        # create_needed_folder(
        #     "./"
        #     + config["images_folders"]
        #     + "/"
        #     + filename_without_ext
        #     + "_"
        #     + str(model.id)
        # )
        # file.save(
        #     f"{config['images_folders']}/{filename_without_ext}_{model.id}/original.{filename.split('.')[-1]}"
        # )
        ic()
        return {"message": "Image uploaded"}, 201

    if allowed_video(file.filename):
        # Достанем видео
        filename = secure_filename(file.filename)
        # Сохраним в папку config['videos_folders']/<название файла>_<номер id>/original.<расширение>
        model = VideoModel.create(filename)
        create_needed_folder(
            "./" + config["videos_folders"] + "/" + filename + "_" + str(model.id)
        )
        file.save(
            f"{config['videos_folders']}/{filename}_{model.id}/original.{filename.split('.')[-1]}"
        )
        return "Video"
    return "File is not Image or Video"
