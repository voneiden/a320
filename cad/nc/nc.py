from ocp_freecad_cam import Job
import os


def save_gcode(job: Job, path: str):
    dirname = os.path.dirname(__file__)
    full_path = os.path.join(dirname, path)
    if not full_path.endswith(".nc"):
        full_path += ".nc"
    dir_path = os.path.dirname(full_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    with open(full_path, "w") as f:
        gcode_lines = job.to_gcode().split("\n")
        gcode = "\n".join(gcode_lines[:1] + gcode_lines[3:])

        f.write(gcode)
