from ultralytics import YOLO
from sort.sort import Sort
import numpy as np
import cv2
from recognition_utils import get_car, read_license_plate, write_to_csv
import torch

torch.cuda.set_device(0)

models_plates_names = [
    "./models/platesRec/yolov9_50e.pt",
    "./models/platesRec/yolov9_100e.pt",
]
model_car_name = "./models/carRecogn/yolov9c.pt"


selected_model = models_plates_names[1]

vehicles = [2, 3, 5, 7]
model_car = YOLO(model_car_name)
model_plates = YOLO(selected_model)


def read_video(video_path: str, results_path=None):
    """
    Считывает видеофайл
    """

    results = {}
    capture = cv2.VideoCapture(video_path)
    tracker = Sort()
    ret = True
    frame_number = -1
    while ret:
        frame_number += 1
        ret, frame = capture.read()
        if ret:
            results[frame_number] = {}
            # Обнаруживаем машины
            detections = model_car.predict(frame)[0]
            detections_ = []
            for detection in detections.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = detection
                if int(class_id) in vehicles:
                    detections_.append((x1, y1, x2, y2, score))

            # Отслеживаем машины
            vehicles_id = tracker.update(np.asarray(detections_))
            license_plates = model_plates.predict(frame)[0]
            for license_plate in license_plates.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = license_plate

                xcar1, ycar1, xcar2, ycar2, car_id = get_car(license_plate, vehicles_id)

                if car_id != -1:
                    # Обрезаем изображение
                    license_plate_cropped = frame[int(y1) : int(y2), int(x1) : int(x2)]

                    # Переводим в оттенки серого
                    license_plate_gray = cv2.cvtColor(
                        license_plate_cropped, cv2.COLOR_BGR2GRAY
                    )
                    _, license_plate_gray_thresh = cv2.threshold(
                        license_plate_gray, 64, 255, cv2.THRESH_BINARY
                    )

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

    if results_path is None:
        for number in range(len(video_path) - 1, -1, -1):
            if video_path == ".":
                break
            elif video_path == "/":
                number = -1
                break
        if number != -1:
            results_path = video_path[:number]
        else:
            results_path = video_path
    write_to_csv(results, results_path)


if __name__ == "__main__":
    read_video("test.mp4")
