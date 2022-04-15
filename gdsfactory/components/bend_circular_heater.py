import gdsfactory as gf
from gdsfactory.add_padding import get_padding_points
from gdsfactory.component import Component
from gdsfactory.config import TECH
from gdsfactory.cross_section import strip
from gdsfactory.path import arc, extrude
from gdsfactory.snap import snap_to_grid
from gdsfactory.types import CrossSectionSpec


@gf.cell
def bend_circular_heater(
    radius: float = 10,
    angle: float = 90,
    npoints: int = 720,
    heater_to_wg_distance: float = 1.2,
    heater_width: float = 0.5,
    layer_heater=TECH.layer.HEATER,
    cross_section: CrossSectionSpec = strip,
    **kwargs
) -> Component:
    """Creates an arc of arclength ``theta`` starting at angle ``start_angle``

    Args:
        radius:
        angle: angle of arc (degrees)
        npoints: Number of points used per 360 degrees
        heater_to_wg_distance:
        heater_width:
        layer_heater:
        cross_section: specification (CrossSection, string, CrossSectionFactory, dict).
        kwargs: cross_section settings.
    """
    x = gf.get_cross_section(cross_section, radius=radius, **kwargs)
    width = x.width
    layer = x.layer

    x = gf.CrossSection()
    x.add(width=width, offset=0, layer=layer, ports=["in", "out"])

    offset = heater_to_wg_distance + width / 2
    x.add(
        width=heater_width,
        offset=+offset,
        layer=layer_heater,
    )
    x.add(
        width=heater_width,
        offset=-offset,
        layer=layer_heater,
    )
    p = arc(radius=radius, angle=angle, npoints=npoints)
    c = extrude(p, x)
    c.length = snap_to_grid(p.length())
    c.dx = abs(p.points[0][0] - p.points[-1][0])
    c.dy = abs(p.points[0][0] - p.points[-1][0])

    for layer, offset in zip(x.bbox_layers, x.bbox_offsets):
        points = get_padding_points(
            component=c,
            default=0,
            bottom=offset,
            top=offset,
        )
        c.add_polygon(points, layer=layer)
    return c


if __name__ == "__main__":
    c = bend_circular_heater(heater_width=1)
    print(c.ports)
    c.show()
