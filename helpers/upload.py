import os

allowed_extensions_video = ["mp4", "avi"]
allowed_extensions_image = ["jpg", "jpeg", "png"]


def allowed_video(filename):
    return any(filename.endswith(ext) for ext in allowed_extensions_video)


def allowed_img(filename):
    return any(filename.endswith(ext) for ext in allowed_extensions_image)


def create_needed_folder(path: str):
    """
    Создает папки по пути path
    :param path: путь до папки - <путь где хранятся все меди файлы>/<название папки для файла>
    """
    splitted_path = path.split("/")

    for i in range(1, len(splitted_path) + 1):
        path = "/".join(splitted_path[0:i])
        if not os.path.exists(path):
            os.mkdir(path)
