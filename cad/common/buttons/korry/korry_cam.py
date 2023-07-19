from cad.common.buttons.korry.korry import KorrySwitch
from cad.nc import save_gcode
from ocp_freecad_cam import Job, Endmill



def cam_sleeve(
    name,
    width,
    height,
    stock_thickness,
    corner_radius=3.175 / 2,
    left_ledge=True,
    right_ledge=True,
    show_object=None,
):
    j = KorrySwitch(width, height, corner_radius=corner_radius)
    sleeve = j.sleeve(stock_thickness, left_ledge=left_ledge, right_ledge=right_ledge)

    sorted_faces = sleeve.part.faces().group_by()
    top = sorted_faces[-1][0]
    bottom = sorted_faces[0][0]
    mid = sorted_faces[1]
    if not left_ledge or not right_ledge:
        mid += sorted_faces[3]

    if show_object:
        show_object(sleeve)
        show_object(mid)

    endmill_1mm = Endmill(diameter=1)
    job = (
        Job(bottom, sleeve.part, "grbl")
        .profile(mid, endmill_1mm)
        .profile(top, endmill_1mm, holes=True)
    )

    if show_object:
        pass
        job.show(show_object)

    output_name = [name, f"{width}x{height}x{stock_thickness}", f"r{corner_radius}"]
    if not left_ledge:
        output_name.append("no_left_ledge")
    if not right_ledge:
        output_name.append("no_right_ledge")
    save_gcode(job, "_".join(output_name))
    job.save_fcstd("korry_sleeve_debug.fcstd")


def cam_slider(
    name, width, height, stock_thickness, corner_radius=3.175 / 2, show_object=None
):
    j = KorrySwitch(width, height)
    slider = j.slider(stock_thickness)

    if show_object:
        show_object(slider)

    faces = slider.part.faces().group_by()
    top = faces[-1][0]
    bottom = faces[0][0]
    mid = faces[-2]

    endmill_1mm = Endmill(diameter=1)
    job = (
        Job(top, slider.part, "grbl")
        .profile(mid, endmill_1mm, side="in")
        .profile(bottom, endmill_1mm, holes=True)
    )

    if show_object:
        show_object(mid)
        job.show(show_object)

    output_name = [name, f"{width}x{height}x{stock_thickness}", f"r{corner_radius}"]

    save_gcode(job, "_".join(output_name))


if __name__ == "__cq_viewer__":
    from cq_viewer import show_object
else:
    show_object = None

#cam_sleeve("korry/sleeve", 19.5, 19.5, 4, left_ledge=True, right_ledge=True)
cam_sleeve(
    "korry/sleeve",
    19.86,
    19.5,
    4,
    left_ledge=False,
    right_ledge=True,
)
#cam_sleeve("korry/sleeve", 19.86, 19.5, 4, left_ledge=True, right_ledge=False)
#cam_sleeve("korry/sleeve", 19.86, 19.5, 4, left_ledge=False, right_ledge=False)
cam_slider("korry/slider", 19.5, 19.5, 3, show_object=show_object)
