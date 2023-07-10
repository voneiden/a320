import time
from copy import copy

from build123d import *
from ocp_freecad_cam.api import Tab

from cad.common.buttons.jayel.jayel import JayelSwitch
from cad.nc import save_gcode


class Autobrake:
    def diffusers(self):
        j = JayelSwitch(19.5, 19.5)
        decel = j.diffuser(text="DECEL").part
        on = j.diffuser(text="ON", frame=True).part
        unlk = j.diffuser(text="UNLK").part
        blank = j.diffuser().part
        tri = j.diffuser(triangle=True).part
        # layout = [
        #    [decel, on, unlk, tri, on],
        #    [decel, on, unlk, tri, blank],
        #    [decel, on, unlk, tri, blank]
        # ]
        layout = [
            [blank, blank, blank, blank, blank],
            [blank, blank, blank, blank, blank],
            [blank, blank, blank, blank, blank],
        ]

        h_spacing = 22
        v_spacing = 13
        parts = []
        for v, row in enumerate(layout):
            for h, part in enumerate(row):
                part_copy = part.copy()
                part_copy.move(Location((h_spacing * h, v_spacing * -v, 0)))
                parts.append(part_copy)

        return Compound(children=parts)


# __name__ = "__cq_viewer__"


def cnc_single_sleeve(left_ledge=True, right_ledge=True):
    from cq_viewer import show_object
    from ocp_freecad_cam import Job, Endmill

    j = JayelSwitch(19.5, 19.5)
    sleeve = j.sleeve(4, left_ledge=left_ledge, right_ledge=right_ledge)
    show_object(sleeve)

    endmill_1mm = Endmill(diameter=1)
    sorted_faces = sleeve.part.faces().group_by()
    top = sorted_faces[-1][0]
    bottom = sorted_faces[0][0]
    mid = sorted_faces[1]

    job = (
        Job(bottom, sleeve.part, "grbl")
        .profile(mid, endmill_1mm)
        .profile(top, endmill_1mm, holes=True)
    )

    job.show(show_object)
    name = ["autobrake/single_sleeve"]
    if not left_ledge:
        name.append("no_left_ledge")
    if not right_ledge:
        name.append("no_right_ledge")
    save_gcode(job, "_".join(name))


def cnc_single_slider():
    from cq_viewer import show_object
    from ocp_freecad_cam import Job, Endmill

    j = JayelSwitch(19.5, 19.5)
    slider = j.slider(4)
    show_object(slider)

    endmill_1mm = Endmill(diameter=1)

    faces = slider.part.faces().sort_by()
    top = faces[-1]
    bottom = faces[0]

    job = Job(top, slider.part, "grbl").profile(bottom, endmill_1mm, holes=True)

    job.show(show_object)
    save_gcode(job, "autobrake/single_slider")


if __name__ == "__cq_viewer__":
    cnc_single_sleeve(left_ledge=True, right_ledge=False)


def cnc_diffusers():
    from cq_viewer import show_object
    from ocp_freecad_cam import Job, Endmill

    autobrake = Autobrake()
    diffusers = autobrake.diffusers()
    diffusers_bbox = diffusers.bounding_box()

    diffusers_center = diffusers_bbox.center()
    diffusers_bottom = copy(diffusers_center)
    diffusers_bottom.Z = diffusers_bbox.min.Z

    bottom_plane = Plane(diffusers_bottom, x_dir=(1, 0, 0), z_dir=(0, 0, -1))

    # Should be divisible by 25
    # alignment_distance = Vector(0, 25, 0)
    # with BuildPart() as mounting_holes:
    #    with Locations(
    #            diffusers_center - alignment_distance,
    #            diffusers_center + alignment_distance
    #    ):
    #        Cylinder(5, 3)
    #        Hole(2.5)
    # mounting_hole_faces = (mounting_holes.faces() | GeomType.CYLINDER) << SortBy.AREA

    top_faces = diffusers.faces().group_by()[-1]

    # mounting_hole_job = (
    #    Job(bottom_plane, diffusers)
    #    .helix(mounting_hole_faces, endmill_3175mm)
    # )

    endmill_3175mm = Endmill(diameter=3.175)
    profile_job = (
        Job(diffusers.faces().sort_by()[0], diffusers)
        .pocket(diffusers.faces().group_by()[1], endmill_3175mm, pattern="offset")
        .profile(top_faces, endmill_3175mm, dressups=[Tab()])
    )

    show_object(diffusers)
    profile_job.show(show_object)
    with open("autobrake_diffusers.nc", "w") as f:
        f.write(profile_job.to_gcode())
