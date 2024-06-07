import cv2
import pandas as pd
import numpy as np
import os
import ffmpegcv
from helpers.edit import get_contrast_color, optimize_font_scale
from icecream import ic


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


def apply_and_save_video(video_path: str, csv_path: str, thickness=10, line_length=20):
    """
    Применяет фильтры из csv к видео.
    Стуктрура csv файла - {
    "frame_number": int - номер кадра,
    "car_id": int
    "car_bbox": list (4 числа) - координаты машины
    "lp_bbox": list (4 числа) - координаты номера машины
    "lp_text": str - номер
    "lp_bbox_score": float - вероятность наличия номера
    "lp_text_score": float - вероятность правильного распознавания
    }
    """

    df = pd.read_csv(
        csv_path,
        converters={
            "lp_bbox": fix_list,
            "car_bbox": fix_list,
        },
    )
    font = cv2.FONT_HERSHEY_DUPLEX

    capture = cv2.VideoCapture(video_path)

    # fps = capture.get(cv2.CAP_PROP_FPS)
    # width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    # height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    frame_number = -1
    ret = True
    path, ext = os.path.splitext(video_path)
    output_video = ffmpegcv.VideoWriterNV(path + f"_filtered{ext}", "h264")
    # output_video = cv2.VideoWriter(
    #     path + f"_filtered{ext}",
    #     cv2.VideoWriter.fourcc(*"DIVX"),
    #     fps,
    #     (width, height),
    # )
    df["lp_text"] = df["lp_text"].fillna("")
    while ret:
        ret, frame = capture.read()
        frame_number += 1
        if ret:
            # Достаним все записи для этого кадра
            df_ = df[df["frame_number"] == frame_number]
            if len(df_) > 0:
                # Проитерируемся по номерам машин (car_id)
                for car_id in df_["car_id"]:
                    # print(car_id)
                    # print(df_[df_["car_id"] == car_id]["car_bbox"])
                    df_car_id = df_[df_["car_id"] == car_id]
                    # print(df_car_id)
                    # print(df_car_id["car_bbox"].values.tolist()[0])
                    car_bbox = list(map(int, df_car_id["car_bbox"].values.tolist()[0]))
                    # print(car_bbox)
                    lp_bbox = list(map(int, df_car_id["lp_bbox"].values.tolist()[0]))

                    # Вырежем номер
                    # lp_croped = frame[lp_bbox[1] : lp_bbox[3], lp_bbox[0] : lp_bbox[2]]
                    # Достанем номер машины из df
                    number = str(
                        df_[df_["car_id"] == car_id]["lp_text"].values.tolist()[0]
                    )
                    if number == "":
                        continue
                    # print(number)
                    # print(
                    #     (car_bbox[0], car_bbox[1]),
                    # )
                    # ic(lp_bbox)
                    max_height = min(lp_bbox[3] - lp_bbox[1], lp_bbox[1])
                    max_width = lp_bbox[2] - lp_bbox[0]
                    # Узнаем размеры текста
                    scale = optimize_font_scale(
                        number, font, max_width, max_height, thickness
                    )
                    # Закрасим область над номером в белый
                    frame[
                        lp_bbox[1] - max_height - thickness : lp_bbox[1] - thickness,
                        lp_bbox[0] : lp_bbox[2],
                    ] = (255, 255, 255)
                    # Выделем машину
                    ## Вверх-лево
                    cv2.line(
                        frame,
                        (car_bbox[0], car_bbox[1]),
                        (car_bbox[0], car_bbox[1] + line_length),
                        (0, 0, 255),
                        thickness,
                    )
                    cv2.line(
                        frame,
                        (car_bbox[0], car_bbox[1]),
                        (car_bbox[0] + line_length, car_bbox[1]),
                        (0, 0, 255),
                        thickness,
                    )

                    ## Низ-право
                    cv2.line(
                        frame,
                        (car_bbox[2], car_bbox[3]),
                        (car_bbox[2], car_bbox[3] - line_length),
                        (0, 0, 255),
                        thickness,
                    )
                    cv2.line(
                        frame,
                        (car_bbox[2], car_bbox[3]),
                        (car_bbox[2] - line_length, car_bbox[3]),
                        (0, 0, 255),
                        thickness,
                    )

                    ## Низ-лево
                    cv2.line(
                        frame,
                        (car_bbox[0], car_bbox[3]),
                        (car_bbox[0], car_bbox[3] - line_length),
                        (0, 0, 255),
                        thickness,
                    )
                    cv2.line(
                        frame,
                        (car_bbox[0], car_bbox[3]),
                        (car_bbox[0] + line_length, car_bbox[3]),
                        (0, 0, 255),
                        thickness,
                    )

                    ## Верх-право
                    cv2.line(
                        frame,
                        (car_bbox[2], car_bbox[1]),
                        (car_bbox[2], car_bbox[1] + line_length),
                        (0, 0, 255),
                        thickness,
                    )

                    cv2.line(
                        frame,
                        (car_bbox[2], car_bbox[1]),
                        (car_bbox[2] - line_length, car_bbox[1]),
                        (0, 0, 255),
                        thickness,
                    )

                    # Выделим номер и напишем расшифровку текстом
                    cv2.rectangle(
                        frame,
                        (lp_bbox[0], lp_bbox[1]),
                        (lp_bbox[2], lp_bbox[3]),
                        (0, 255, 0),
                        thickness,
                    )

                    cv2.putText(
                        frame,
                        number,
                        (lp_bbox[0], lp_bbox[1] - thickness),
                        cv2.FONT_HERSHEY_DUPLEX,
                        scale,
                        get_contrast_color(
                            frame[car_bbox[1] : car_bbox[3], car_bbox[0] : car_bbox[2]]
                        ),
                        4,
                        cv2.LINE_AA,
                    )

                    # Сохраняем видео
            output_video.write(frame)

    output_video.release()
    capture.release()


def apply_and_save_image(image_path: str, csv_path: str, thickness=10, line_length=20):
    """
    Применяет фильтры из csv к изображению.
    Стуктрура csv файла - {
    "car_id": int
    "car_bbox": list (4 числа) - координаты машины
    "lp_bbox": list (4 числа) - координаты номера машины
    "lp_text": str - номер
    "lp_bbox_score": float - вероятность наличия номера
    "lp_text_score": float - вероятность правильного распознавания
    }
    """
    image = cv2.imread(image_path)
    df = pd.read_csv(csv_path, converters={"car_bbox": fix_list, "lp_bbox": fix_list})
    font = cv2.FONT_HERSHEY_DUPLEX
    # Применяем фильтры
    for index, row in df.iterrows():
        # ic(row["car_bbox"])
        car_bbox = list(map(int, row["car_bbox"]))
        lp_bbox = list(map(int, row["lp_bbox"]))

        number = str(row["lp_text"])
        if number == "":
            continue
        # ic(row)

        max_height = min(lp_bbox[3] - lp_bbox[1], lp_bbox[1])
        max_width = lp_bbox[2] - lp_bbox[0]

        # Узнаем размеры текста
        scale = optimize_font_scale(number, font, max_width, max_height, thickness)
        # Закрасим область над номером в белый
        image[
            lp_bbox[1] - max_height - thickness : lp_bbox[1] - thickness,
            lp_bbox[0] : lp_bbox[2],
        ] = (255, 255, 255)
        ## Вверх-лево
        cv2.line(
            image,
            (car_bbox[0], car_bbox[1]),
            (car_bbox[0], car_bbox[1] + line_length),
            (0, 0, 255),
            thickness,
        )
        cv2.line(
            image,
            (car_bbox[0], car_bbox[1]),
            (car_bbox[0] + line_length, car_bbox[1]),
            (0, 0, 255),
            thickness,
        )

        ## Низ-право
        cv2.line(
            image,
            (car_bbox[2], car_bbox[3]),
            (car_bbox[2], car_bbox[3] - line_length),
            (0, 0, 255),
            thickness,
        )
        cv2.line(
            image,
            (car_bbox[2], car_bbox[3]),
            (car_bbox[2] - line_length, car_bbox[3]),
            (0, 0, 255),
            thickness,
        )

        ## Низ-лево
        cv2.line(
            image,
            (car_bbox[0], car_bbox[3]),
            (car_bbox[0], car_bbox[3] - line_length),
            (0, 0, 255),
            thickness,
        )
        cv2.line(
            image,
            (car_bbox[0], car_bbox[3]),
            (car_bbox[0] + line_length, car_bbox[3]),
            (0, 0, 255),
            thickness,
        )

        ## Верх-право
        cv2.line(
            image,
            (car_bbox[2], car_bbox[1]),
            (car_bbox[2], car_bbox[1] + line_length),
            (0, 0, 255),
            thickness,
        )

        cv2.line(
            image,
            (car_bbox[2], car_bbox[1]),
            (car_bbox[2] - line_length, car_bbox[1]),
            (0, 0, 255),
            thickness,
        )

        # Выделим номер и напишем расшифровку текстом
        cv2.rectangle(
            image,
            (lp_bbox[0], lp_bbox[1]),
            (lp_bbox[2], lp_bbox[3]),
            (0, 255, 0),
            thickness,
        )

        cv2.putText(
            image,
            number,
            (lp_bbox[0], lp_bbox[1] - thickness),
            cv2.FONT_HERSHEY_DUPLEX,
            scale,
            # get_contrast_color(
            #     image[car_bbox[1] : car_bbox[3], car_bbox[0] : car_bbox[2]]
            # ),
            (0, 0, 255),
            1,
            cv2.LINE_AA,
        )
    path, ext = os.path.splitext(image_path)
    cv2.imwrite(path + f"_filtered{ext}", image)


if __name__ == "__main__":
    apply_and_save_video("test.mp4", "test_int.csv")
