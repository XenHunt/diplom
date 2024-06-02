import time
from app import rq
from orm import ImageModel, VideoModel
from main import read_video, read_image
from fix_data import fix_csv_data
from apply_csv import apply_and_save_video, apply_and_save_image
import pandas as pd
import os
from icecream import ic


@rq.job(timeout=-1)
def processVideo(vmodel: VideoModel):
    path = vmodel.getPath()
    vmodel.updateStatus("Reading")
    ic(vmodel.extension)
    ic(path)
    read_video(
        os.path.join(path, f"original{vmodel.extension}"),
        os.path.join(path, "data.csv"),
    )
    # Теперь надо проверить есть ли созданный data.csv
    if not os.path.exists(os.path.join(path, "data.csv")):
        vmodel.updateStatus("Done")
        return
    ic()
    vmodel.updateStatus("Interpolating")
    fix_csv_data(os.path.join(path, "data.csv"))
    ic()
    vmodel.updateStatus("Applying")
    apply_and_save_video(
        os.path.join(path, f"original{vmodel.extension}"),
        os.path.join(path, "data_fixed.csv"),
    )
    ic()
    vmodel.updateStatus("Done")


@rq.job(timeout=-1)
def processImage(imodel: ImageModel):
    ic("HERE")
    path = imodel.getPath()
    imodel.updateStatus("Reading")
    ic(os.path.join(path, f"original{imodel.extension}"))
    read_image(
        os.path.join(path, f"original{imodel.extension}"),
        os.path.join(path, "data.csv"),
    )

    # Теперь надо проверить есть ли созданный data.csv
    if not os.path.exists(os.path.join(path, "data.csv")):
        imodel.updateStatus("Done")
        return
    imodel.updateStatus("Interpolating")
    # fix_csv_data(os.path.join(path, "data.csv"))
    imodel.updateStatus("Applying")
    apply_and_save_image(
        os.path.join(path, f"original{imodel.extension}"),
        os.path.join(path, "data.csv"),
    )
    imodel.updateStatus("Done")


@rq.job(timeout=-1)
def changePlateNumber(car_id: int, number: str, model: VideoModel | ImageModel):
    def change(x):
        if x.car_id == car_id:
            x.lp_text = number
        return x

    model.updateStatus("Changing")
    path = os.path.join(model.getPath(), "data_fixed.csv")
    ic(path)
    df = pd.read_csv(path)
    df["lp_text"] = df.apply(change, axis=1)["lp_text"]
    # ic(df)
    # ic(df)
    df.to_csv(path, index=False)
    if type(model) is VideoModel:
        model.updateStatus("Reapplying")
        apply_and_save_video(
            os.path.join(model.getPath(), f"original.{model.extension}"),
            path,
        )
        model.updateStatus("Done")

    else:
        model.updateStatus("Reapplying")
        apply_and_save_image(
            os.path.join(model.getPath(), f"original.{model.extension}"),
            path,
        )
        model.updateStatus("Done")
