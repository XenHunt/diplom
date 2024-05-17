from app import rq
from orm import ImageModel, VideoModel
from main import read_video, read_image
from fix_data import fix_csv_data
from apply_csv import apply_and_save_video, apply_and_save_image
import pandas as pd
import os


@rq.job()
def processVideo(vmodel: VideoModel):
    path = vmodel.getPath()
    vmodel.updateStatus("Reading")
    read_video(
        os.path.join(path, f"/original.{vmodel.extension}"),
        os.path.join(path, "data.csv"),
    )
    vmodel.updateStatus("Interpolating")
    fix_csv_data(os.path.join(path, "data.csv"))
    vmodel.updateStatus("Applying")
    apply_and_save_video(
        os.path.join(path, f"original.{vmodel.extension}"),
        os.path.join(path, "data_fixed.csv"),
    )
    vmodel.updateStatus("Done")


@rq.job()
def processImage(imodel: ImageModel):
    path = imodel.getPath()
    imodel.updateStatus("Reading")
    read_image(
        os.path.join(path, f"original.{imodel.extension}"),
        os.path.join(path, "data.csv"),
    )
    imodel.updateStatus("Interpolating")
    fix_csv_data(os.path.join(path, "data.csv"))
    imodel.updateStatus("Applying")
    apply_and_save_image(
        os.path.join(path, f"original.{imodel.extension}"),
        os.path.join(path, "data_fixed.csv"),
    )
    imodel.updateStatus("Done")


@rq.job
def changePlateNumber(car_id: int, number: str, model: VideoModel | ImageModel):
    model.updateStatus("Changing")
    path = os.path.join(model.getPath(), "data_fixed.csv")
    df = pd.read_csv(path)
    df.loc[df["car_id"] == car_id, "plate_number"] = number
    df.to_csv(path, index=False)
    if type(model) is VideoModel:
        model.updateStatus("Reapplying")
        apply_and_save_video(
            os.path.join(model.getPath(), f"original.{model.extension}"),
            os.path.join(model.getPath(), "data_fixed.csv"),
        )
        model.updateStatus("Done")

    else:
        model.updateStatus("Reapplying")
        apply_and_save_image(
            os.path.join(model.getPath(), f"original.{model.extension}"),
            os.path.join(model.getPath(), "data_fixed.csv"),
        )
        model.updateStatus("Done")
