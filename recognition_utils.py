import easyocr
import string
import pyarrow
import pandas as pd
import numpy as np

reader = easyocr.Reader(["en"], gpu=False)


def __is_symbol__(text: str):
    return text in string.ascii_uppercase or text in dict_int_to_char.keys()


def __is_digit__(text: str):
    return (
        text in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        or text in dict_char_to_int.keys()
    )


dict_char_to_int = {"O": "0", "I": "1", "J": "3", "A": "4", "G": "6", "S": "5"}

dict_int_to_char = {"0": "O", "1": "I", "3": "J", "4": "A", "6": "G", "5": "S"}


def license_series_format(text: str):
    """
    Проверяет формат серии машины (символ, 3 цифры и 2 символа - пример: E100EE)
    """

    if len(text) != 6:
        return False

    if (
        __is_symbol__(text[0])
        and __is_digit__(text[1])
        and __is_digit__(text[2])
        and __is_digit__(text[3])
        and __is_symbol__(text[4])
        and __is_symbol__(text[5])
    ):
        return True
    return False


def license_region_format(text: str):
    """
    Проверяет код региона (2-3 цифры - примеры: 22, 01, 123)
    """
    if len(text) < 2 or len(text) > 3:
        return False

    if len(text) == 2:
        if __is_digit__(text[0]) and __is_digit__(text[1]):
            return True
    else:
        if __is_digit__(text[0]) and __is_digit__(text[1]) and __is_digit__(text[2]):
            return True
    return False


def license_country_format(text: str):
    """
    Проверяет формат кода страны (3 буквы - примеры: RUS, ENG, USA)
    """

    if len(text) != 3:
        return False

    if __is_symbol__(text[0]) and __is_symbol__(text[1]) and __is_symbol__(text[2]):
        return True

    return False


def fix_plate(license_plate: dict):
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

    license_plate["series"] = fix_element(
        license_plate["series"],
        [
            dict_int_to_char,
            dict_char_to_int,
            dict_char_to_int,
            dict_char_to_int,
            dict_int_to_char,
            dict_int_to_char,
        ],
    )
    license_plate["region"] = fix_element(
        license_plate["region"], [dict_char_to_int, dict_char_to_int, dict_char_to_int]
    )
    license_plate["country"] = fix_element(
        license_plate["country"], [dict_int_to_char, dict_int_to_char, dict_int_to_char]
    )

    return license_plate


def read_license_plate(license_plate_img):
    """
    Читает номера автомобиля на вырезанном изображении
    """

    detections = reader.readtext(license_plate_img)

    license_plate = {"series": "", "region": "", "country": ""}

    scores = []

    for detection in detections:
        _, text, score = detection

        text = text.upper().replace(" ", "")

        # Проверяем на серию

        if license_series_format(text):
            license_plate["series"] = text
            scores.append(score)

        # Проверяем на код региона

        if license_region_format(text):
            license_plate["region"] = text
            scores.append(score)

        # Проверяем на название страны

        if license_country_format(text):
            license_plate["country"] = text
            scores.append(score)

        if all([_ != "" for _ in license_plate.values()]):
            return license_plate, sum(score) / len(score)

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
        return cars[car_indx]

    return -1, -1, -1, -1, -1


def write_to_csv(results: dict, results_path: str):
    results_ = {
        "frame_number": [],
        "car_id": [],
        "car_bbox": [],
        "lp_bbox": [],
        "lp_text_ser": [],
        "lp_text_reg": [],
        "lp_text_coun": [],
        "lp_bbox_score": [],
        "lp_text_score": [],
    }
    for frame_number in np.sort(list(results.keys())):
        for car_id in np.sort(list(results[frame_number].keys())):
            car_bbox = results[frame_number][car_id]["bbox"]
            lp_bbox = results[frame_number][car_id]["license_plate"]["bbox"]
            lp_text_ser = results[frame_number][car_id]["license_plate"]["text"][
                "series"
            ]
            lp_text_reg = results[frame_number][car_id]["license_plate"]["text"][
                "region"
            ]
            lp_text_coun = results[frame_number][car_id]["license_plate"]["text"][
                "country"
            ]
            lp_bbox_score = results[frame_number][car_id]["license_plate"]["bbox_score"]
            lp_text_score = results[frame_number][car_id]["license_plate"]["text_score"]

            results_["frame_number"].append(frame_number)
            results_["car_id"].append(car_id)
            results_["car_bbox"].append(car_bbox)
            results_["lp_bbox"].append(lp_bbox)
            results_["lp_text_ser"].append(lp_text_ser)
            results_["lp_text_reg"].append(lp_text_reg)
            results_["lp_text_coun"].append(lp_text_coun)
            results_["lp_bbox_score"].append(lp_bbox_score)
            results_["lp_text_score"].append(lp_text_score)

    pyarrow.Table.from_pydict(results_).to_pandas(types_mapper=pd.ArrowDtype).to_csv(
        results_path
    )
