import cv2
import pandas as pd
import numpy as np
import os


def apply_and_save(video_path: str, csv_path: str, thickness=10):
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

    def fix_list(x: str):
        x_list = x.split()
        x_ = ""
        numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        print(x_list)
        for symb in x_list:
            x_ += symb
            if "]" not in symb and any([num in symb for num in numbers]):
                x_ += ", "
            else:
                x_ += " "
            print(x_)
        return np.array(eval(x_))

    df = pd.read_csv(
        csv_path,
        converters={
            "lp_bbox": fix_list,
            "car_bbox": fix_list,
        },
    )

    capture = cv2.VideoCapture(video_path)

    fps = capture.get(cv2.CAP_PROP_FPS)
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    frame_number = -1
    ret = True
    output_video = cv2.VideoWriter(
        os.path.splitext(video_path)[0] + "_filtered.avi",
        cv2.VideoWriter.fourcc(*"DIVX"),
        fps,
        (width, height),
    )
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
                    print(df_car_id["car_bbox"].values.tolist()[0])
                    car_bbox = list(map(int, df_car_id["car_bbox"].values.tolist()[0]))
                    print(car_bbox)
                    lp_bbox = list(map(int, df_car_id["lp_bbox"].values.tolist()[0]))

                    # Вырежем номер
                    # lp_croped = frame[lp_bbox[1] : lp_bbox[3], lp_bbox[0] : lp_bbox[2]]
                    # Достанем номер машины из df
                    number = str(
                        df_[df_["car_id"] == car_id]["lp_text"].values.tolist()[0]
                    )
                    print(number)
                    print(
                        (car_bbox[0], car_bbox[1]),
                    )
                    # Выделем машину
                    ## Вверх-лево
                    cv2.line(
                        frame,
                        (car_bbox[0], car_bbox[1]),
                        (car_bbox[0], car_bbox[1] + 10),
                        (0, 0, 255),
                        thickness,
                    )
                    cv2.line(
                        frame,
                        (car_bbox[0], car_bbox[1]),
                        (car_bbox[0] + 10, car_bbox[1]),
                        (0, 0, 255),
                        thickness,
                    )

                    ## Низ-право
                    cv2.line(
                        frame,
                        (car_bbox[2], car_bbox[3]),
                        (car_bbox[2], car_bbox[3] - 10),
                        (0, 0, 255),
                        thickness,
                    )
                    cv2.line(
                        frame,
                        (car_bbox[2], car_bbox[3]),
                        (car_bbox[2] - 10, car_bbox[3]),
                        (0, 0, 255),
                        thickness,
                    )

                    ## Низ-лево
                    cv2.line(
                        frame,
                        (car_bbox[0], car_bbox[3]),
                        (car_bbox[0], car_bbox[3] - 10),
                        (0, 0, 255),
                        thickness,
                    )
                    cv2.line(
                        frame,
                        (car_bbox[0], car_bbox[3]),
                        (car_bbox[0] + 10, car_bbox[3]),
                        (0, 0, 255),
                        thickness,
                    )

                    ## Верх-право
                    cv2.line(
                        frame,
                        (car_bbox[2], car_bbox[1]),
                        (car_bbox[2], car_bbox[1] + 10),
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
                        (lp_bbox[0], lp_bbox[1] - (lp_bbox[3] - lp_bbox[1])),
                        cv2.FONT_HERSHEY_DUPLEX,
                        1.5,
                        (255, 0, 0),
                        1,
                        cv2.LINE_AA,
                    )

                    # Сохраняем видео
            output_video.write(frame)


if __name__ == "__main__":
    apply_and_save("test.mp4", "test_int.csv")
