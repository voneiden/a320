from build123d import *
from cq_viewer import show_object


class Switch8x8:
    def slider(self):
        # Lower square is 9.4 - 7.2 = 2.2 mm
        # 4x4 mm
        with BuildPart() as builder:
            with BuildSketch():
                Rectangle(4, 4)
            extrude(amount=2.2)
            plane = Plane.XZ
            plane.move(Location((0, 0, 2.2)))
            with BuildSketch(plane):
                with BuildLine() as pl:
                    Polyline(
                        (0, 0),
                        (-1.5, 0),
                        (-1.5, 1),
                        (-1, 1),
                        (-1, 2),
                        (-1.5, 2),
                        (-1.5, 3),
                        (-0.5, 3),
                        (-0.5, 2.5),
                        (0, 2.5),
                    )
                    mirror(pl.line, Plane.YZ)
                make_face()
            extrude(amount=1, both=True)  # TODO check amount
        builder.part.color = Color("steelblue")
        return builder

    def housing(self):
        with BuildPart() as builder:
            Box(8, 8, 8)
        builder.part.color = Color("gray20")
        return builder

    def assembly(self):
        slider = self.slider()
        housing = self.housing()
        housing.part.move(Location((0, 0, -4)))
        builders = [slider.part, housing.part]
        return Compound(children=builders)


if __name__ == "__main__":
    switch = Switch8x8()
    show_object(switch.assembly())
