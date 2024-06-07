from app import app
from orm import VideoModel
from redis_functions import changePlateNumber
import cv2
import os
from helpers.edit import check_number, get_df, get_contrast_color
from flask import Response
from helpers.parser import editParser, updateParser
from icecream import ic


def get_frame(model: VideoModel, frame_number: int):
    path = os.path.join(model.getPath(), f"original{model.extension}")
    video = cv2.VideoCapture(path)
    video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = video.read()
    video.release()
    if not ret:
        raise Exception("Failed to load frame")
    return frame


@app.route("/video-edit/<int:video_id>/get-frames", methods=["GET"])
def get_video_frames(video_id: int):
    model = VideoModel.getById(video_id)
    if model is None:
        raise Exception("No such video")
    path = os.path.join(model.getPath(), f"original{model.extension}")
    video = cv2.VideoCapture(path)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    video.release()
    return {"max": frame_count}, 200


@app.route("/video-edit/<int:video_id>/<int:frame_number>/get-ids", methods=["GET"])
def get_video_car_ids(video_id: int, frame_number: int):
    model = VideoModel.getById(video_id)
    if model is None:
        raise Exception("No such video")
    df = get_df(os.path.join(model.getPath(), "data_fixed.csv"))
    df = df[df["frame_number"] == frame_number]
    return df["car_id"].tolist(), 200


@app.route("/video-edit/<int:video_id>/<int:frame_number>/preview", methods=["GET"])
def get_video_preview(video_id: int, frame_number: int):
    model = VideoModel.getById(video_id)
    if model is None:
        raise Exception("No such video")
    frame = get_frame(model, frame_number)
    font = cv2.FONT_HERSHEY_DUPLEX
    df = get_df(os.path.join(model.getPath(), "data_fixed.csv"))
    # Достанем все записи соответсвующие текущему кадру
    df = df[df["frame_number"] == frame_number]
    # Теперь выделим все записи номеров на кадре
    for car_id in df["car_id"]:
        # Записи для текущего машины
        df_car_id = df[df["car_id"] == car_id]
        lp_bbox = list(map(int, df_car_id["lp_bbox"].values.tolist()[0]))

        number = str(df_car_id["lp_text"].values.tolist()[0])

        size = cv2.getTextSize(car_id, font, 2, 1)
        cv2.rectangle(
            frame,
            (lp_bbox[0], lp_bbox[1] - size[1]),
            (lp_bbox[0], lp_bbox[3] - size[1]),
            (255, 255, 255),
            -1,
        )

        cv2.putText(
            frame,
            str(int(car_id)),
            (lp_bbox[0], lp_bbox[1]),
            cv2.FONT_HERSHEY_DUPLEX,
            2,
            get_contrast_color(frame[lp_bbox[1] : lp_bbox[3], lp_bbox[0] : lp_bbox[2]]),
            1,
            cv2.LINE_AA,
        )

    _, buffer = cv2.imencode(".jpg", frame)
    return Response(buffer.tobytes(), mimetype="image/jpg")


@app.route(
    "/video-edit/<int:video_id>/<int:frame_number>/<int:car_id>", methods=["POST"]
)
def get_video_car(video_id: int, frame_number: int, car_id: int):
    data = editParser.parse_args()
    model = VideoModel.getById(video_id)
    if model is None:
        raise Exception("No such video")
    frame = get_frame(model, frame_number)
    df = get_df(os.path.join(model.getPath(), "data_fixed.csv"))
    df = df[df["frame_number"] == frame_number][df["car_id"] == car_id]
    lp_bbox = list(map(int, df["lp_bbox"].values.tolist()[0]))
    # Вырежем номер
    frame = frame[lp_bbox[1] : lp_bbox[3], lp_bbox[0] : lp_bbox[2]]
    # cv2.imwrite("testing.jpg", frame)
    # Применим фильтры, если надо
    ic(data)
    if data["grayMode"]:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if data["thresholdMode"]:
            _, frame = cv2.threshold(
                frame, data["thresholdValue"], 255, cv2.THRESH_BINARY
            )

    _, buffer = cv2.imencode(".jpg", frame)
    return Response(buffer.tobytes(), mimetype="image/jpg")


@app.route("/video-edit/<int:video_id>/<int:car_id>/update", methods=["POST"])
def update_video(video_id: int, car_id: int):
    data = updateParser.parse_args()
    if not check_number(data["plate_number"]):
        return {"message": "Bad number"}, 400
    model = VideoModel.getById(video_id)
    if model is None:
        raise Exception("No such video")
    changePlateNumber.queue(car_id, data["plate_number"], model)
    return {"message": "Starts updating"}, 200


@app.route("/video-edit/<int:video_id>/<int:car_id>/get-plate-number", methods=["GET"])
def get_video_plate_number(video_id: int, car_id: int):
    model = VideoModel.getById(video_id)
    if model is None:
        raise Exception("No such video")
    df = get_df(os.path.join(model.getPath(), "data_fixed.csv"))
    df = df[df["car_id"] == car_id]
    return {"number": str(df["lp_text"].values.tolist()[0])}, 200
