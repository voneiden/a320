from build123d import *
from cq_viewer import show_object


def sleeve(
    width,
    height,
    stock_thickness,
    ledge=0.5,
    corner_radius=0.5,
    wall_thickness=0.5,
    ledge_thickness=1.0,
):
    outer_width = width + wall_thickness * 2
    outer_height = height + wall_thickness * 2
    ledge_width = outer_width + ledge * 2
    ledge_height = outer_height + ledge * 2

    with BuildPart() as sleeve_part:
        with BuildSketch():
            RectangleRounded(ledge_width, ledge_height, corner_radius)
            RectangleRounded(width, height, corner_radius, mode=Mode.SUBTRACT)

        extrude(amount=-ledge_thickness)

        with BuildSketch(sleeve_part.faces().sort_by(Axis.Z)[0]):
            RectangleRounded(outer_width, outer_height, corner_radius)
            RectangleRounded(width, height, corner_radius, mode=Mode.SUBTRACT)

        extrude(amount=stock_thickness - ledge_thickness)

    return sleeve_part


def slot_values(width, height, wall_thickness):
    slot_width = width - wall_thickness * 2
    slot_height = (height - wall_thickness * 3) / 2
    slot_offset = slot_height / 2 + wall_thickness / 2

    return slot_width, slot_height, slot_offset


def slider(
    width,
    height,
    slot_width,
    slot_height,
    slot_offset,
    stock_thickness=5,
    diffuser_thickness=3,
    diffuser_ledge=0.5,
    corner_radius=0.5,
):
    lower_slot_width = slot_width - diffuser_ledge * 2
    lower_slot_height = slot_height - diffuser_ledge * 2
    with BuildPart() as slider_part:
        with BuildSketch(Plane.XY.offset(-1)):
            RectangleRounded(width, height, corner_radius)
            with Locations((0, slot_offset), (0, -slot_offset)):
                RectangleRounded(
                    slot_width, slot_height, corner_radius, mode=Mode.SUBTRACT
                )
        extrude(amount=-diffuser_thickness)

        with BuildSketch(slider_part.faces().sort_by(Axis.Z)[0]):
            RectangleRounded(width, height, corner_radius)
            with Locations((0, slot_offset), (0, -slot_offset)):
                RectangleRounded(
                    lower_slot_width,
                    lower_slot_height,
                    corner_radius,
                    mode=Mode.SUBTRACT,
                )
        extrude(amount=stock_thickness - diffuser_thickness)

    return slider_part


def cover(width, height, cover_thickness=1, corner_radius=0.5):
    with BuildPart() as cover_part:
        with BuildSketch():
            RectangleRounded(width, height, corner_radius)
        extrude(amount=-1)
    return cover_part


def diffuser(
    diffuser_width, diffuser_height, corner_radius=0.5, stock_thickness=3, text=None
):
    with BuildPart() as diffuser_part:
        with BuildSketch():
            RectangleRounded(diffuser_width, diffuser_height, corner_radius)
        extrude(amount=-stock_thickness)
        if text:
            with BuildSketch():
                Text(text, 5)
            extrude(amount=-0.1, mode=Mode.SUBTRACT)
    return diffuser_part


slot_width, slot_height, slot_offset = slot_values(20, 20, 1)

sleeve_part = sleeve(20, 20, 3)
slider_part = slider(20, 20, slot_width, slot_height, slot_offset)
cover_part = cover(20, 20)
upper_diffuser = diffuser(slot_width, slot_height, text="FAIL")
upper_diffuser.part.move(Location((0, slot_offset, -1)))
lower_diffuser = diffuser(slot_width, slot_height, text="TEST")
lower_diffuser.part.move(Location((0, -slot_offset, -1)))
# diffuser_assembly_part = diffuser_assembly(20, 20)


show_object(sleeve_part, color="gray20")
show_object(slider_part, color="gray40")
# show_object(cover_part, color="white", transparency=0.8)
show_object(upper_diffuser, color="gray10")
show_object(lower_diffuser, color="gray80")
