import build123d as b3d
import os


def save_dxf(obj: b3d.Shape, path: str):
    dirname = os.path.dirname(__file__)
    full_path = os.path.join(dirname, path)
    if not full_path.endswith(".dxf"):
        full_path += ".dxf"
    dir_path = os.path.dirname(full_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    obj.export_dxf(full_path)
