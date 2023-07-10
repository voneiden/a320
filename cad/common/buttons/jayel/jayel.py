from dataclasses import dataclass

from build123d import *
from cad.fonts import panel_font_path


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
    slider_stock_thickness: float = 5
    pcb_thickness: float = 1.6
    cover_stock_thickness: float = 1

    connector_length = 20
    connector_width = 5
    connector_stock_thickness = 3

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
        builder.part.color = Color("gray20")
        return builder

    def slider(
        self,
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
            extrude(amount=self.slider_stock_thickness - diffuser_stock_thickness)
        builder.part.color = Color("gray40")
        return builder

    def cover(self):
        with BuildPart() as builder:
            with BuildSketch():
                RectangleRounded(self.width, self.height, self.corner_radius)
            extrude(amount=-self.cover_stock_thickness)
        builder.part.color = Color(name="white", alpha=0.9)
        return builder

    def diffuser(self, stock_thickness=3, text=None, frame=False, triangle=False):
        with BuildPart() as builder:
            with BuildSketch():
                RectangleRounded(
                    self.diffuser_width, self.diffuser_height, self.corner_radius
                )
            extrude(amount=-stock_thickness)
            with BuildSketch(builder.faces().sort_by()[0]):
                RectangleRounded(
                    self.diffuser_width - 1.5,
                    self.diffuser_height - 1.5,
                    self.corner_radius,
                )
            extrude(amount=-stock_thickness / 2, mode=Mode.SUBTRACT)

            if text and not triangle:
                with BuildSketch():
                    Text(text, 5, font_path=panel_font_path)
                extrude(amount=-0.1, mode=Mode.SUBTRACT)
            if frame and not triangle:
                with BuildSketch():
                    frame_padding = 2
                    frame_outer_width = self.diffuser_width - frame_padding
                    frame_outer_height = self.diffuser_height - frame_padding
                    frame_line_width = 0.5
                    frame_inner_width = frame_outer_width - (frame_line_width * 2)
                    frame_inner_height = frame_outer_height - (frame_line_width * 2)
                    RectangleRounded(frame_outer_width, frame_outer_height, 1)
                    RectangleRounded(
                        frame_inner_width, frame_inner_height, 0.5, mode=Mode.SUBTRACT
                    )
                extrude(amount=-0.1, mode=Mode.SUBTRACT)

            if triangle:
                with BuildSketch():
                    with BuildLine() as tri:
                        tri_padding = 2
                        tri_horizontal = (self.diffuser_width - tri_padding) / 2
                        tri_vertical = (self.diffuser_height - tri_padding) / 2

                        Polyline(
                            (-tri_horizontal, tri_vertical),
                            (tri_horizontal, tri_vertical),
                            (0, -tri_vertical),
                            close=True,
                        )

                    make_face()

                    offset(amount=-1, mode=Mode.SUBTRACT)
                extrude(amount=-0.1, mode=Mode.SUBTRACT)
        builder.part.color = Color("gray80")
        return builder

    def pcb(self):
        """Mock model for the led circuit board"""
        with BuildPart() as builder:
            with BuildSketch():
                RectangleRounded(self.width, self.height, self.corner_radius)
            extrude(amount=-self.pcb_thickness)

        builder.part.color = Color("yellowgreen")
        return builder

    def connector(self):
        half_width = self.connector_width / 2
        with BuildPart() as builder:
            # Cylinder(2.5, 20, align=(Align.CENTER, Align.CENTER, Align.MIN))
            with BuildSketch(Plane.XZ):
                Rectangle(
                    self.connector_width,
                    self.connector_length,
                    align=(Align.CENTER, Align.MIN),
                )
                with BuildLine():
                    Polyline(
                        (-1.5, 0),
                        (-1.5, 1),
                        (-1.25, 1.5),
                        (-1.5, 2),
                        (-1.5, 3),
                        (1.5, 3),
                        (1.5, 2),
                        (1.25, 1.5),
                        (1.5, 1),
                        (1.5, 0),
                        close=True,
                    )
                make_face(mode=Mode.SUBTRACT)
            # extrude(amount=3, both=True, mode=Mode.SUBTRACT)
            extrude(amount=self.connector_stock_thickness / 2, both=True)
        builder.part.color = Color("gray30")
        return builder

    def assembly(self, upper_text=None, lower_text=None):
        from cad.pcb.switches.switch_8x8 import Switch8x8

        sleeve = self.sleeve(3)

        slider = self.slider()
        slider.part.move(Location((0, 0, -1)))
        cover = self.cover()
        upper_diffuser = self.diffuser(text=upper_text)
        upper_diffuser.part.move(Location((0, self.diffuser_offset, -1)))
        lower_diffuser = self.diffuser(text=lower_text, frame=True)
        lower_diffuser.part.move(Location((0, -self.diffuser_offset, -1)))
        pcb = self.pcb()
        pcb.part.move(
            Location(
                (0, 0, -(self.cover_stock_thickness + self.slider_stock_thickness))
            )
        )
        connector = self.connector()
        connector.part.move(
            Location(
                (
                    0,
                    0,
                    -(
                        self.cover_stock_thickness
                        + self.slider_stock_thickness
                        + self.connector_length
                    ),
                )
            )
        )
        switch = Switch8x8().assembly()
        switch.move(Location((0, 0, -28.2)))
        builders = [
            sleeve,
            slider,
            cover,
            upper_diffuser,
            lower_diffuser,
            pcb,
            connector,
        ]

        parts = [builder.part for builder in builders]
        return Compound(children=parts + [switch])


if __name__ == "__cq_viewer__":
    j = JayelSwitch(20, 20)
    from cq_viewer import show_object

    # show_object(j.assembly("DECEL", "ON"))
    show_object(j.assembly())
