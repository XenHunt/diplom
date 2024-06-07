from app import app
from orm import ImageModel
from redis_functions import changePlateNumber
import cv2
import os
from helpers.edit import check_number, get_df, get_contrast_color
from flask import Response
from helpers.parser import editParser, updateParser


@app.route("/image-edit/<int:image_id>/get-ids", methods=["GET"])
def get_imageedit_ids(image_id: int):
    model = ImageModel.getById(image_id)
    if model is None:
        raise Exception("No such image")
    df = get_df(os.path.join(model.getPath(), "data.csv"))
    return df["car_id"].values.tolist(), 200


@app.route("/image-edit/<int:image_id>/preview", methods=["GET"])
def get_imageedit_preview(image_id: int):
    model = ImageModel.getById(image_id)
    if model is None:
        raise Exception("No such image")
    df = get_df(os.path.join(model.getPath(), "data.csv"))
    image = cv2.imread(os.path.join(model.getPath(), f"original{model.extension}"))
    font = cv2.FONT_HERSHEY_DUPLEX
    for car_id in df["car_id"]:
        df_car_id = df[df["car_id"] == car_id]
        lp_bbox = list(map(int, df_car_id["lp_bbox"].values.tolist()[0]))

        number = str(df_car_id["lp_text"].values.tolist()[0])

        size = cv2.getTextSize(car_id, font, 2, 1)
        cv2.rectangle(
            image,
            (lp_bbox[0], lp_bbox[1] - size[1]),
            (lp_bbox[0], lp_bbox[3] - size[1]),
            (255, 255, 255),
            -1,
        )

        cv2.putText(
            image,
            str(car_id),
            (lp_bbox[0], lp_bbox[1]),
            cv2.FONT_HERSHEY_DUPLEX,
            2,
            get_contrast_color(image[lp_bbox[1] : lp_bbox[3], lp_bbox[0] : lp_bbox[2]]),
            1,
            cv2.LINE_AA,
        )

    _, buffer = cv2.imencode(".jpg", image)
    return Response(buffer.tobytes(), mimetype="image/jpg")


@app.route("/image-edit/<int:image_id>/<int:car_id>", methods=["POST"])
def get_imageedit_car(image_id: int, car_id: int):
    data = editParser.parse_args()
    model = ImageModel.getById(image_id)
    if model is None:
        raise Exception("No such image")
    df = get_df(os.path.join(model.getPath(), "data.csv"))
    df = df[df["car_id"] == car_id]
    if len(df) == 0:
        raise Exception("No such car")
    image = cv2.imread(os.path.join(model.getPath(), f"original{model.extension}"))
    lp_bbox = list(map(int, df["lp_bbox"].values.tolist()[0]))
    image = image[lp_bbox[1] : lp_bbox[3], lp_bbox[0] : lp_bbox[2]]

    if data["grayMode"]:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if data["thresholdMode"]:
            _, image = cv2.threshold(
                image, 0, data["thresholdValue"], cv2.THRESH_BINARY
            )

    _, buffer = cv2.imencode(".jpg", image)
    return Response(buffer.tobytes(), mimetype="image/jpg")


@app.route("/image-edit/<int:image_id>/<int:car_id>/update", methods=["POST"])
def update_image(image_id: int, car_id: int):
    data = updateParser.parse_args()
    if not check_number(data["plate_number"]):
        return {"message": "Bad number"}, 400
    model = ImageModel.getById(image_id)
    if model is None:
        raise Exception("No such image")
    changePlateNumber.queue(car_id, data["plate_number"], model)
    return {"message": "Starts updating"}, 200


@app.route("/image-edit/<int:image_id>/<int:car_id>/get-plate-number", methods=["GET"])
def get_image_plate_number(image_id: int, car_id: int):
    model = ImageModel.getById(image_id)
    if model is None:
        raise Exception("No such image")
    df = get_df(os.path.join(model.getPath(), "data.csv"))
    df = df[df["car_id"] == car_id]
    if len(df) == 0:
        raise Exception("No such car")
    return {"number": df["lp_text"].values.tolist()[0]}, 200
