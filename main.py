# from numpy.random import rand
from ultralytics import YOLO

# from sort.sort import Sort
import numpy as np
import cv2
from recognition_utils import get_car, read_license_plate, write_to_csv, get_car_yolo
from icecream import ic
import os

# import torch
# TODO заменить Sort на DeepSort
# torch.cuda.set_device(0)

models_plates_names = [
    "./models/platesRec/yolov9_50e.pt",
    "./models/platesRec/yolov9_100e.pt",
    "./models/platesRec/yolov9_5e_v2.pt",
]


selected_model = models_plates_names[1]

vehicles = [2, 3, 5, 7]
model_plates = YOLO(selected_model)


def read_video(video_path: str, results_path=None):
    """
    Считывает видеофайл
    """
    ic(os.curdir)
    results = {}
    ic(video_path)
    capture = cv2.VideoCapture(video_path)
    ic()
    # tracker = Sort()
    model_car = YOLO("./models/carRecogn/yolov9c.pt")
    ret = True
    frame_number = -1
    while ret:
        frame_number += 1
        ret, frame = capture.read()
        # ic("inside")
        if ret:
            # ic("good ret")
            # if frame_number > 890 or frame_number < 763:
            #     continue
            # if frame_number != 16:
            #     continue
            results[frame_number] = {}
            # Обнаруживаем машины
            detections = model_car.track(frame, persist=True, classes=vehicles)[0]
            # print(detections)
            detections_ = []
            boxes = detections.boxes
            if boxes is None:
                continue
            track_ids = boxes.id.int().cpu().tolist()
            conf = boxes.conf.cpu().tolist()
            boxes = boxes.xyxy.int().cpu().tolist()
            for box, id, conf in zip(boxes, track_ids, conf):
                x1, y1, x2, y2 = box
                score = conf
                car_id = id
                detections_.append((x1, y1, x2, y2, score, car_id))

            # Отслеживаем машины
            # vehicles_id = tracker.update(np.asarray(detections_))
            vehicles_id = detections_
            license_plates = model_plates.predict(frame)[0]
            for license_plate in license_plates.boxes.data.tolist():
                x1, y1, x2, y2, score, _ = license_plate

                xcar1, ycar1, xcar2, ycar2, car_id = get_car_yolo(
                    license_plate, vehicles_id
                )

                if car_id != -1:
                    # Обрезаем изображение
                    license_plate_cropped = frame[int(y1) : int(y2), int(x1) : int(x2)]

                    # Переводим в оттенки серого
                    license_plate_gray = cv2.cvtColor(
                        license_plate_cropped, cv2.COLOR_BGR2GRAY
                    )

                    sharp_filter = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])

                    license_plate_gray = cv2.filter2D(
                        license_plate_gray, ddepth=-1, kernel=sharp_filter
                    )

                    # cv2.imwrite(
                    #     f"./test/test_orig_{frame_number}_orig_{rand()}.png",
                    #     license_plate_cropped,
                    # )
                    # cv2.imwrite(
                    #     f"./test/test_{frame_number}_orig_{rand()}.png",
                    #     license_plate_gray,
                    # )
                    for low_thresh in range(142, 150):
                        _, license_plate_gray_thresh = cv2.threshold(
                            license_plate_gray, low_thresh, 255, cv2.THRESH_BINARY
                        )
                        # license_plate_gray_thresh = license_plate_gray
                        # _, license_plate_gray_thresh = cv2.threshold(
                        #     license_plate_gray, 147, 255, cv2.THRESH_BINARY
                        # )
                        # cv2.imwrite(
                        #     f"./test/test_{frame_number}_{low_thresh}_{rand()}.png",
                        #     license_plate_gray_thresh,
                        # )

                        # Читаем номер пластины
                        license_plate_text, text_score = read_license_plate(
                            license_plate_gray_thresh
                        )

                        if license_plate_text is not None:
                            results[frame_number][car_id] = {
                                "car": {"bbox": [xcar1, ycar1, xcar2, ycar2]},
                                "license_plate": {
                                    "bbox": [x1, y1, x2, y2],
                                    "text": license_plate_text,
                                    "bbox_score": score,
                                    "text_score": text_score,
                                },
                            }
                            break
                    if license_plate_text is None:
                        results[frame_number][car_id] = {
                            "car": {"bbox": [xcar1, ycar1, xcar2, ycar2]},
                            "license_plate": {
                                "bbox": [x1, y1, x2, y2],
                                "text": "",
                                "bbox_score": score,
                                "text_score": 0,
                            },
                        }

    if results_path is None:
        results_path = os.path.splitext(video_path)[0] + ".csv"
    print(results)
    write_to_csv(results, results_path)


def read_image(image_path: str, results_path=None):
    im = cv2.imread(image_path)
    results = {}
    # tracker = Sort()
    model_car = YOLO("./models/carRecogn/yolov9c.pt")
    detections = model_car.predict(im)[0]
    detections_ = []
    for car in detections.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = car
        if int(class_id) in vehicles:
            detections_.append((x1, y1, x2, y2, score))
    vehicles_id = detections_
    license_plates = model_plates.predict(im)[0]
    for license_plate in license_plates.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = license_plate
        xcar1, ycar1, xcar2, ycar2, car_id = get_car(license_plate, vehicles_id)

        if car_id != -1:
            # Обрезаем изображение
            license_plate_cropped = im[int(y1) : int(y2), int(x1) : int(x2)]

            # Переводим в оттенки серого
            license_plate_gray = cv2.cvtColor(license_plate_cropped, cv2.COLOR_BGR2GRAY)

            sharp_filter = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])

            license_plate_gray = cv2.filter2D(
                license_plate_gray, ddepth=-1, kernel=sharp_filter
            )

            # cv2.imwrite(
            #     f"./test/test_orig_{frame_number}_orig_{rand()}.png",
            #     license_plate_cropped,
            # )
            # cv2.imwrite(
            #     f"./test/test_{frame_number}_orig_{rand()}.png",
            #     license_plate_gray,
            # )
            for low_thresh in range(142, 150):
                _, license_plate_gray_thresh = cv2.threshold(
                    license_plate_gray, low_thresh, 255, cv2.THRESH_BINARY
                )
                # license_plate_gray_thresh = license_plate_gray
                # _, license_plate_gray_thresh = cv2.threshold(
                #     license_plate_gray, 147, 255, cv2.THRESH_BINARY
                # )
                # cv2.imwrite(
                #     f"./test/test_{frame_number}_{low_thresh}_{rand()}.png",
                #     license_plate_gray_thresh,
                # )

                # Читаем номер пластины
                license_plate_text, text_score = read_license_plate(
                    license_plate_gray_thresh
                )

                if license_plate_text is not None:
                    results[car_id] = {
                        "car": {"bbox": [xcar1, ycar1, xcar2, ycar2]},
                        "license_plate": {
                            "bbox": [x1, y1, x2, y2],
                            "text": license_plate_text,
                            "bbox_score": score,
                            "text_score": text_score,
                        },
                    }
                    break
            if license_plate_text is None:
                results[car_id] = {
                    "car": {"bbox": [xcar1, ycar1, xcar2, ycar2]},
                    "license_plate": {
                        "bbox": [x1, y1, x2, y2],
                        "text": "",
                        "bbox_score": score,
                        "text_score": 0,
                    },
                }
        if results_path is None:
            results_path = os.path.splitext(image_path)[0] + ".csv"
        write_to_csv(results, results_path, True)


if __name__ == "__main__":
    read_video("test.mp4")
