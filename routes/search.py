from app import app
from helpers.parser import searchParser
from orm import VideoModel

from helpers.edit import get_df, create_list_of_frames

from icecream import ic
import os


@app.route("/video/<int:id>/search", methods=["POST"])
def search_cars(id: int):
    ic()
    data = searchParser.parse_args()
    ic()
    model = VideoModel.getById(id)

    if model is None:
        return {"message": "No such media"}, 404

    df = get_df(os.path.join(model.getPath(), "data_fixed.csv"))
    # df["car_id"] = df["car_id"].astype(int)
    unique_values = df[
        df["lp_text"].fillna("").str.contains(data["searchPattern"], regex=True)
    ]["car_id"].unique()

    ret = []
    ic(unique_values)
    for number in unique_values:
        df_ = df[df["car_id"] == number]
        lp = df_["lp_text"].values[0]
        frames = df_["frame_number"].tolist()
        ret.append(
            {
                "car_id": int(number),
                "lp_text": lp,
                "frames": create_list_of_frames(frames),
            }
        )

    return {"cars": ret}, 200
