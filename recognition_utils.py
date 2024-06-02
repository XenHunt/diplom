from deep_sort_realtime.deep_sort.track import Track
import easyocr
import string
import pyarrow
import pandas as pd
import numpy as np
import os

path = os.path.dirname(os.path.abspath(__file__)) + "/models/OCRPlates"

reader = easyocr.Reader(
    ["en"],
    model_storage_directory=path + "/model",
    user_network_directory=path + "/user_network",
    recog_network="ocr_plates",
)


def __is_symbol__(text: str):
    return text in string.ascii_uppercase or text in dict_int_to_char.keys()


def __is_digit__(text: str):
    return (
        text in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        or text in dict_char_to_int.keys()
    )


dict_char_to_int = {
    "O": "0",
    "I": "1",
    "J": "3",
    "A": "4",
    "G": "6",
    "S": "5",
    "T": "7",
}

dict_int_to_char = {
    "0": "O",
    "1": "I",
    "3": "J",
    "4": "A",
    "6": "G",
    "5": "S",
    "7": "T",
}


def check_plate(text: str):
    """
    Проверяет правильность формата номера
    """

    if len(text) not in [8, 9]:
        return False

    if (
        __is_symbol__(text[0])
        and __is_digit__(text[1])
        and __is_digit__(text[2])
        and __is_digit__(text[3])
        and __is_symbol__(text[4])
        and __is_symbol__(text[5])
        and __is_digit__(text[6])
        and __is_digit__(text[7])
        and (len(text) == 8 or __is_digit__(text[8]))
    ):
        return True
    return False


def fix_plate(license_plate: str):
    """
    Чинит символы в номере машины
    """

    def fix_element(elem: str, mapping: list):
        _elem = ""

        for i in range(len(elem)):
            if elem[i] in mapping[i].keys():
                _elem += mapping[i][elem[i]]
            else:
                _elem += elem[i]

        return _elem

    license_plate = fix_element(
        license_plate,
        [
            dict_int_to_char,
            dict_char_to_int,
            dict_char_to_int,
            dict_char_to_int,
            dict_int_to_char,
            dict_int_to_char,
            dict_char_to_int,
            dict_char_to_int,
            dict_char_to_int,
        ],
    )

    return license_plate


def read_license_plate(license_plate_img):
    """
    Читает номера автомобиля на вырезанном изображении
    """

    detections = reader.readtext(license_plate_img, allowlist="1234567890ABEKMHOPCTYX")

    # print("reading_plate")
    for detection in detections:
        _, text, score = detection

        text = text.upper().replace(" ", "")
        # print(text)
        # Проверяем на серию
        if check_plate(text):
            return fix_plate(text), score
    return None, None


def get_car(license_plate, cars):
    """
    Получаем машину, к которой относится её номер
    """
    x1, y1, x2, y2, score, class_id = license_plate

    foundIt = False
    for j in range(len(cars)):
        # print(cars[j])
        xcar1, ycar1, xcar2, ycar2, _ = cars[j]
        if x1 > xcar1 and y1 > ycar1 and x2 < xcar2 and y2 < ycar2:
            car_indx = j
            foundIt = True
            break
    if foundIt:
        print(cars[car_indx])
        return cars[car_indx]

    return -1, -1, -1, -1, -1


def get_car_deep(license_plate, tracks: list[Track]):
    """
    Получаем машину, к которой относится её номер
    """
    x1, y1, x2, y2, score, class_id = license_plate

    foundIt = False
    for track in tracks:
        if not track.is_confirmed():
            continue
        bbox = track.to_tlwh(orig=True, orig_strict=True)
        if bbox is None:
            continue
        xcar1, ycar1, xcar2, ycar2 = bbox
        xcar2, ycar2 = xcar1 + xcar2, ycar1 + ycar2
        track_id = track.track_id
        if x1 > xcar1 and y1 > ycar1 and x2 < xcar2 and y2 < ycar2:
            car_indx = track_id
            foundIt = True
            break
    if foundIt:
        return xcar1, ycar1, xcar2, ycar2, car_indx

    return -1, -1, -1, -1, -1


def get_car_yolo(license_plate, tracks):
    """
    Получаем машину, к которой относится её номер
    """
    x1, y1, x2, y2, score, class_id = license_plate

    foundIt = False
    for track in tracks:
        xcar1, ycar1, xcar2, ycar2, _, car_indx = track
        if x1 > xcar1 and y1 > ycar1 and x2 < xcar2 and y2 < ycar2:
            foundIt = True
            break

    if foundIt:
        return xcar1, ycar1, xcar2, ycar2, car_indx

    return -1, -1, -1, -1, -1


def write_to_csv(results: dict, results_path: str, isimg=False):
    if not isimg:
        results_ = {
            "frame_number": [],
            "car_id": [],
            "car_bbox": [],
            "lp_bbox": [],
            "lp_text": [],
            "lp_bbox_score": [],
            "lp_text_score": [],
        }
        for frame_number in np.sort(list(results.keys())):
            for car_id in np.sort(list(results[frame_number].keys())):
                car_bbox = results[frame_number][car_id]["car"]["bbox"]
                lp_bbox = results[frame_number][car_id]["license_plate"]["bbox"]
                lp_text = results[frame_number][car_id]["license_plate"]["text"]
                lp_bbox_score = results[frame_number][car_id]["license_plate"][
                    "bbox_score"
                ]
                lp_text_score = results[frame_number][car_id]["license_plate"][
                    "text_score"
                ]

                results_["frame_number"].append(frame_number)
                results_["car_id"].append(car_id)
                results_["car_bbox"].append(car_bbox)
                results_["lp_bbox"].append(lp_bbox)
                results_["lp_text"].append(lp_text)
                results_["lp_bbox_score"].append(lp_bbox_score)
                results_["lp_text_score"].append(lp_text_score)
    else:

        results_ = {
            "car_id": [],
            "car_bbox": [],
            "lp_bbox": [],
            "lp_text": [],
            "lp_bbox_score": [],
            "lp_text_score": [],
        }
        for car_id in np.sort(list(results.keys())):
            car_bbox = results[car_id]["car"]["bbox"]
            lp_bbox = results[car_id]["license_plate"]["bbox"]
            lp_text = results[car_id]["license_plate"]["text"]
            lp_bbox_score = results[car_id]["license_plate"]["bbox_score"]
            lp_text_score = results[car_id]["license_plate"]["text_score"]

            results_["car_id"].append(car_id)
            results_["car_bbox"].append(car_bbox)
            results_["lp_bbox"].append(lp_bbox)
            results_["lp_text"].append(lp_text)
            results_["lp_bbox_score"].append(lp_bbox_score)
            results_["lp_text_score"].append(lp_text_score)

    pyarrow.Table.from_pydict(results_).to_pandas(types_mapper=pd.ArrowDtype).to_csv(
        results_path, index=False
    )
