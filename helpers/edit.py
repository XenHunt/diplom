import pandas as pd
import numpy as np
from icecream import ic

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
    average_color = np.mean(img, axis=(0, 1))
    # Теперь вернем вектор с 255 - average_color[i]
    # ic([int(255 - c) for c in average_color])
    # return [int(c) for c in average_color]
    return (0, 0, 255)
