from flask_socketio import SocketIO, emit
from app import app
import base64
from orm import VideoModel

socketio = SocketIO(app, cors_allowed_origins="*")


@socketio.on("video_stream_send")
def get_video_stream(data):
    model = VideoModel.getById(data.get("id"))
    if model is None:
        return
    video_path = model.getPath() + f"fixed.{model.extension}"
    with open(video_path, "rb") as video_file:
        while True:
            chunk = video_file.read(1024)  # Читаем видеофайл частями
            if not chunk:
                break
            encoded_chunk = base64.b64encode(chunk).decode(
                "utf-8"
            )  # Кодируем часть видеофайла в base64
            emit(
                "video_chunk", {"data": encoded_chunk}
            )  # Отправляем закодированную часть видеофайла по веб-сокету


@socketio.on("connect")
def start_video_stream(data):
    model = VideoModel.getById(data.get("id"))
    if model is not None:
        return {"message": "Connection succesful"}, 201
    return {"message": "Video not found"}, 404


@socketio.on("disconnect")
def stop_video_stream(data):
    model = VideoModel.getById(data.get("id"))
    if model is not None:
        return {"message": "Connection closed"}, 201
    return {"message": "Video not found"}, 404
