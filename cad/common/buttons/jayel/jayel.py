from dataclasses import dataclass

from build123d import *


@dataclass
class JayelSwitch:
    """
    Width and height define the base dimensions of the underlying cutout
    that the switch needs to fit into.
    """

    width: float
    height: float
    wall_thickness: float = 1.0
    corner_radius: float = 0.5

    @property
    def diffuser_width(self):
        return self.width - self.wall_thickness * 2

    @property
    def diffuser_height(self):
        return (self.height - self.wall_thickness * 3) / 2

    @property
    def diffuser_offset(self):
        return self.diffuser_height / 2 + self.wall_thickness / 2

    def sleeve(
        self,
        stock_thickness,
        ledge_offset=0.5,
        ledge_thickness=1.0,
    ):
        outer_width = self.width + self.wall_thickness * 2
        outer_height = self.height + self.wall_thickness * 2
        ledge_width = outer_width + ledge_offset * 2
        ledge_height = outer_height + ledge_offset * 2

        with BuildPart() as builder:
            with BuildSketch():
                RectangleRounded(ledge_width, ledge_height, self.corner_radius)
                RectangleRounded(
                    self.width, self.height, self.corner_radius, mode=Mode.SUBTRACT
                )

            extrude(amount=-ledge_thickness)

            with BuildSketch(builder.faces().sort_by(Axis.Z)[0]):
                RectangleRounded(outer_width, outer_height, self.corner_radius)
                RectangleRounded(
                    self.width, self.height, self.corner_radius, mode=Mode.SUBTRACT
                )

            extrude(amount=stock_thickness - ledge_thickness)

        return builder

    def slider(
        self,
        stock_thickness=5,
        diffuser_stock_thickness=3,
        diffuser_ledge=0.5,
    ):
        lower_slot_width = self.diffuser_width - diffuser_ledge * 2
        lower_slot_height = self.diffuser_height - diffuser_ledge * 2
        with BuildPart() as builder:
            with BuildSketch():
                RectangleRounded(self.width, self.height, self.corner_radius)
                with Locations((0, self.diffuser_offset), (0, -self.diffuser_offset)):
                    RectangleRounded(
                        self.diffuser_width,
                        self.diffuser_height,
                        self.corner_radius,
                        mode=Mode.SUBTRACT,
                    )
            extrude(amount=-diffuser_stock_thickness)

            with BuildSketch(builder.faces().sort_by(Axis.Z)[0]):
                RectangleRounded(self.width, self.height, self.corner_radius)
                with Locations((0, self.diffuser_offset), (0, -self.diffuser_offset)):
                    RectangleRounded(
                        lower_slot_width,
                        lower_slot_height,
                        self.corner_radius,
                        mode=Mode.SUBTRACT,
                    )
            extrude(amount=stock_thickness - diffuser_stock_thickness)

        return builder

    def cover(self, stock_thickness=1):
        with BuildPart() as builder:
            with BuildSketch():
                RectangleRounded(self.width, self.height, self.corner_radius)
            extrude(amount=-stock_thickness)
        return builder

    def diffuser(self, stock_thickness=3, text=None):
        with BuildPart() as builder:
            with BuildSketch():
                RectangleRounded(
                    self.diffuser_width, self.diffuser_height, self.corner_radius
                )
            extrude(amount=-stock_thickness)
            if text:
                with BuildSketch():
                    Text(text, 5)
                extrude(amount=-0.1, mode=Mode.SUBTRACT)
        return builder

    def assembly(self, upper_text=None, lower_text=None):
        sleeve = self.sleeve(3)
        sleeve.part.color = Color("gray20")
        slider = self.slider(5)
        slider.part.move(Location((0, 0, -1)))
        slider.part.color = Color("gray40")
        cover = self.cover(1)
        cover.part.color = Color(name="white", alpha=0.9)
        upper_diffuser = self.diffuser(text=upper_text)
        upper_diffuser.part.move(Location((0, self.diffuser_offset, -1)))
        upper_diffuser.part.color = Color("gray80")
        lower_diffuser = self.diffuser(text=lower_text)
        lower_diffuser.part.move(Location((0, -self.diffuser_offset, -1)))
        lower_diffuser.part.color = Color("gray80")
        builders = [sleeve, slider, cover, upper_diffuser, lower_diffuser]

        parts = [builder.part for builder in builders]
        return Compound(children=parts)


j = JayelSwitch(20, 20)
from cq_viewer import show_object

show_object(j.assembly("FAIL", "MED"))
