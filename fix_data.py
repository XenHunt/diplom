import numpy as np
import pandas as pd
import os


def fix_csv_data(path: str):
    def fix_list(x: str):
        x_list = x.split()
        x_ = ""
        numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        print(x_list)
        for symb in x_list:
            x_ += symb
            if "]" not in symb and any([num in symb for num in numbers]):
                x_ += ","
            print(x_)
        return np.array(eval(x_))

    df = pd.read_csv(
        path,
        # engine="pyarrow",
        converters={
            "lp_bbox": fix_list,
            "car_bbox": fix_list,
        },
    )
    # print(df.columns)
    # Создадим результа, как таблицу df, но с пустыми строками
    result = pd.DataFrame(columns=df.columns)
    for car_id in np.unique(np.array(df["car_id"])):
        # Надо получить все строки с этим car_id
        df_ = df[df["car_id"] == car_id]

        # Вычислим номер машины как то значение у которого в сумме вероятность больше
        # print(np.unique(np.array(df_["lp_text"])))
        # Должны применять, если не все None:
        grouped = df_.groupby(["lp_text"])["lp_text_score"].sum()
        if not np.all(np.array(df_["lp_text"]) == None) and not len(grouped) == 0:
            print(len(grouped))
            label = grouped.idxmax()
        else:
            label = None
        # Заменим все предсказания на него

        df_["lp_text"] = label

        # Подготовим средние значения для lp_bbox_score и lp_text_score

        mean_lp_bbox_score = np.mean(df_["lp_bbox_score"])
        mean_lp_text_score = np.mean(df_["lp_text_score"])

        # Возьмем фреймы
        frames = df_[["frame_number"]]

        # Пройдем по ним
        results_steps = []
        for num in range(len(frames)):
            # if car_id != 47:
            #     continue
            result_step = df_.iloc[num]
            print("Right")
            print(result_step)
            if num > 0:
                # Теперь нам надо проинтерполировать значения
                x = (
                    frames.iloc[num - 1]["frame_number"],
                    frames.iloc[num]["frame_number"],
                )
                l_car_bbox = results_steps[-1]["car_bbox"]
                r_car_bbox = result_step["car_bbox"]
                print(l_car_bbox)

                l_lp_bbox = results_steps[-1]["lp_bbox"]
                r_lp_bbox = result_step["lp_bbox"]

                # Теперь задаим кадры, которых нету между двумя известными
                y = np.arange(x[0] + 1, x[1])
                print("Y:")
                print(y)
                # Проинтерполируем значения
                car_bbox = np.array(
                    [
                        np.interp(y, x, (l_car_bbox[0], r_car_bbox[0])),
                        np.interp(y, x, (l_car_bbox[1], r_car_bbox[1])),
                        np.interp(y, x, (l_car_bbox[2], r_car_bbox[2])),
                        np.interp(y, x, (l_car_bbox[3], r_car_bbox[3])),
                    ]
                ).T

                lp_bbox = np.array(
                    [
                        np.interp(y, x, (l_lp_bbox[0], r_lp_bbox[0])),
                        np.interp(y, x, (l_lp_bbox[1], r_lp_bbox[1])),
                        np.interp(y, x, (l_lp_bbox[2], r_lp_bbox[2])),
                        np.interp(y, x, (l_lp_bbox[3], r_lp_bbox[3])),
                    ]
                ).T

                # car_bbox1 = np.interp(y, x, [l_car_bbox1, r_car_bbox1])
                # car_bbox2 = np.interp(y, x, [l_car_bbox2, r_car_bbox2])
                # car_bbox3 = np.interp(y, x, [l_car_bbox3, r_car_bbox3])
                # car_bbox4 = np.interp(y, x, [l_car_bbox4, r_car_bbox4])

                # lp_bbox1 = np.interp(y, x, [l_lp_bbox1, r_lp_bbox1])
                # lp_bbox2 = np.interp(y, x, [l_lp_bbox2, r_lp_bbox2])
                # lp_bbox3 = np.interp(y, x, [l_lp_bbox3, r_lp_bbox3])
                # lp_bbox4 = np.interp(y, x, [l_lp_bbox4, r_lp_bbox4])

                # # Теперь соберем значения по строчно
                # car_bbox = np.array(
                #     [
                #         [car_bbox1[i], car_bbox2[i], car_bbox3[i], car_bbox4[i]]
                #         for i in range(len(car_bbox1))
                #     ]
                # )

                # lp_bbox = np.array(
                #     [
                #         [lp_bbox1[i], lp_bbox2[i], lp_bbox3[i], lp_bbox4[i]]
                #         for i in range(len(lp_bbox1))
                #     ]
                # )

                # Соберем результат как Series
                res = [
                    pd.Series(
                        {
                            "frame_number": y[i],
                            "car_id": car_id,
                            "car_bbox": car_bbox[i],
                            "lp_bbox": lp_bbox[i],
                            "lp_text": label,
                            "lp_bbox_score": mean_lp_bbox_score,
                            "lp_text_score": mean_lp_text_score,
                        }
                    )
                    for i in range(len(y))
                ]

                # res = [
                #     [
                #         y[i],
                #         car_id,
                #         car_bbox[i],
                #         lp_bbox[i],
                #         results_steps[-1][4],
                #         mean_lp_bbox_score,
                #         mean_lp_text_score,
                #     ]
                #     for i in range(len(y))
                # ]
                print("Res")
                print(res)
                results_steps.extend(res)

            # Запишим результат интерполирования
            results_steps.append(result_step)
        # print(results_steps)
        # print(" ".join([str(type(r)) for r in results_steps]))
        result = result._append(results_steps)
    result.to_csv(os.path.splitext(path)[0] + "_fixed.csv", index=False)


if __name__ == "__main__":
    fix_csv_data("./files/videos/test_7/data.csv")
