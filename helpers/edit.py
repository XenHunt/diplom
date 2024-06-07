import pandas as pd
import numpy as np
from icecream import ic
import cv2
from scipy.optimize import bisect

numbs = {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"}
chars = {"A", "B", "E", "K", "M", "H", "O", "P", "C", "T", "X", "Y"}


def check_number(number: str):
    if len(number) not in [8, 9]:
        return False

    if (
        number[0] in chars
        and number[1] in numbs
        and number[2] in numbs
        and number[3] in numbs
        and number[4] in chars
        and number[5] in chars
        and number[6] in numbs
        and number[7] in numbs
    ):
        if len(number) == 9:
            return number[8] in numbs
        else:
            return True
    return False


def get_df(path: str):

    def fix_list(x: str):
        x_list = x.split()
        x_ = ""
        numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        # print(x_list)
        for symb in x_list:
            x_ += symb
            if "]" not in symb and any([num in symb for num in numbers]):
                x_ += ", "
            else:
                x_ += " "
            # print(x_)
        return np.array(eval(x_))

    df = pd.read_csv(path, converters={"lp_bbox": fix_list, "car_bbox": fix_list})
    df["lp_text"] = df["lp_text"].fillna("")
    return df


def create_search_pattern(pattern: str):
    ret = ""
    for index, char in enumerate(pattern):
        ic(ret)
        if char == "?":
            if index == 8:
                ret += "[0-9ABEKMHOPCTYX]?"
            else:
                ret += "[0-9ABEKMHOPCTYX]"
        else:
            ret += char
    ic(ret)
    return ret


def create_list_of_frames(frames: list):
    ret = []
    first = prev = frames[0]
    for frame in frames[1:]:
        if frame - prev > 1:
            if prev == first:
                ret.append(f"{first}")
            else:
                ret.append(f"{first}-{prev}")

            first = prev = frame

        else:
            prev = frame

    if prev == first:
        ret.append(f"{first}")
    else:
        ret.append(f"{first}-{prev}")

    ic(ret)

    return ret


def get_contrast_color(img):
    # average_color = np.mean(img, axis=(0, 1))
    # Теперь вернем вектор с 255 - average_color[i]
    # ic([int(255 - c) for c in average_color])
    # return [int(c) for c in average_color]
    return (0, 0, 0)


def optimize_font_scale(text, font, max_width, max_height, thickness=1):
    """
    Функция для оптимизации размера шрифта с использованием метода бисекции.
    """
    # Установка начальных значений
    lower_bound = 0.1
    upper_bound = 100

    # Определение функции для оптимизации

    # ic(max_width, max_height)

    def text_width(
        text: str, font: int, font_scale: float, thickness: int, img_width: int
    ):
        """
        Функция для оценки разницы между шириной текста и шириной изображения.
        """
        text_width, _ = cv2.getTextSize(text, font, font_scale, thickness)[0]
        # ic(img_width - text_width)
        return img_width - text_width

    def text_height(
        text: str, font: int, font_scale: float, thickness: int, img_height: int
    ):
        """
        Функция для оценки разницы между длинной текста и длинной изображения.
        """
        _, text_height = cv2.getTextSize(text, font, font_scale, thickness)[0]
        # ic(img_height - text_height)
        return img_height - text_height

    # Использование метода бисекции для нахождения оптимального значения
    optimized_font_scale_length = bisect(
        lambda x: text_height(text, font, x, thickness, max_height),
        lower_bound,
        upper_bound,
        xtol=1e-3,
        maxiter=100,
    )
    optimized_font_scale_width = bisect(
        lambda x: text_width(text, font, x, thickness, max_width),
        lower_bound,
        upper_bound,
        xtol=1e-3,
        maxiter=100,
    )

    return min(optimized_font_scale_length, optimized_font_scale_width)


if __name__ == "__main__":
    im_w = 300
    print(optimize_font_scale("Hello", cv2.FONT_HERSHEY_DUPLEX, 300, 300))
