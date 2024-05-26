from flask import send_file, send_from_directory
from flask_cors import cross_origin
from app import app
from orm import ImageModel, VideoModel
from helpers.upload import allowed_img, allowed_video, create_needed_folder
from werkzeug.utils import secure_filename
from icecream import ic
from helpers.parser import uploadParser
from helpers.config import config
from redis_functions import processImage, processVideo
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
    ic(path)
    return send_from_directory(path, "preview.png"), 200


@app.route("/image_preview/<id>", methods=["GET"])
def get_image_preview(id: int):
    # ic(id)
    path = ImageModel.getPathById(id)
    # Надо найти в path original.[png|jpg|jpeg]
    for file in os.listdir(path):
        if "original" in file:
            return send_from_directory(path, file), 200
    return {"message": "No preview"}, 404


@app.route("/video/<id>", methods=["GET"])
def get_video(id: int):
    model = VideoModel.getById(id)
    if type(model) is not VideoModel:
        return {"message": "No such video"}, 404
    if not os.path.exists(
        os.path.join(model.getPath(), f"original_filtered{model.extension}")
    ):
        ic()
        return send_file(
            os.path.join(model.getPath(), f"original{model.extension}"),
            mimetype="video/mp4",
            as_attachment=False,
        )
    return send_file(
        os.path.join(model.getPath(), f"original_filtered{model.extension}"),
        mimetype="video/mp4",
        as_attachment=False,
    )


@app.route("/test1-video", methods=["GET"])
def test_video():
    return send_file("test.mp4", mimetype="video/mp4", as_attachment=False)


@app.route("/test2-video", methods=["GET"])
def test2_video():
    return send_file("output.mp4", mimetype="video/mp4", as_attachment=False)


@app.route("/image/<id>", methods=["GET"])
def get_image(id: int):
    model = ImageModel.getById(id)
    if type(model) is not ImageModel:
        return {"message": "No such image"}, 404
    if not os.path.exists(
        os.path.join(model.getPath(), f"origina_filtered{model.extension}")
    ):
        return send_from_directory(model.getPath(), f"original{model.extension}"), 200
    return (
        send_from_directory(model.getPath(), f"origina_filtered{model.extension}"),
        200,
    )


@app.route("/upload", methods=["POST"])
@cross_origin()
def upload_media():
    data = uploadParser.parse_args()
    file = data["file"]
    filename, extension = os.path.splitext(file.filename)
    ic(data["name"])
    ic(filename)
    ic(extension)
    filename = secure_filename(filename)
    name = secure_filename(data["name"])
    ic(name)
    if allowed_img(file.filename):
        # Сохраним в папку config['images_folders']/<название файла>_<номер id>/original.<расширение>
        model = ImageModel.create(name, filename, extension)
        path = f"{config['images_folders']}/{filename}_{model.id}"
        create_needed_folder(path)
        file.save(f"{path}/original{extension}")
        processImage.queue(model)
        return {"message": "Image uploaded"}, 201

    if allowed_video(file.filename):
        # Сохраним в папку config['videos_folders']/<название файла>_<номер id>/original.<расширение>
        model = VideoModel.create(name, filename, extension)
        path = f"{config['videos_folders']}/{filename}_{model.id}"
        create_needed_folder(path)
        file.save(f"{path}/original{extension}")
        model.createPreview()
        processVideo.queue(model)
        return {"message": "Video uploaded"}, 201
    return {"message": "Wrong file type"}, 400


@app.route("/<type>_<int:id>/status", methods=["GET"])
def get_status(type: str, id: int):
    if type == "Video":
        return {"status": VideoModel.getStatusById(id)}, 200
    elif type == "Image":
        return {"status": ImageModel.getStatusById(id)}, 200
    return {"message": "Bad type of media"}, 400


with app.app_context():
    model = VideoModel.getById(8)
    if type(model) is VideoModel:
        model.updateStatus("Done")
