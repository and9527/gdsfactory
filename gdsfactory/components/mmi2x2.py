import gdsfactory as gf
from gdsfactory.add_padding import add_padding
from gdsfactory.component import Component
from gdsfactory.components.taper import taper as taper_function
from gdsfactory.cross_section import strip
from gdsfactory.types import ComponentFactory, CrossSectionFactory


@gf.cell
def mmi2x2(
    width: float = 0.5,
    width_taper: float = 1.0,
    length_taper: float = 10.0,
    length_mmi: float = 5.5,
    width_mmi: float = 2.5,
    gap_mmi: float = 0.25,
    taper: ComponentFactory = taper_function,
    cross_section: CrossSectionFactory = strip,
    **kwargs
) -> Component:
    r"""Mmi 2x2.

    Args:
        width: input and output straight width
        width_taper: interface between input straights and mmi region
        length_taper: into the mmi region
        length_mmi: in x direction
        width_mmi: in y direction
        gap_mmi: (width_taper + gap between tapered wg)/2
        taper: taper function
        cross_section:
        **kwargs: cross_section settings


    .. code::

                   length_mmi
                    <------>
                    ________
                   |        |
                __/          \__
            W1  __            __  E1
                  \          /_ _ _ _
                  |         | _ _ _ _| gap_mmi
                __/          \__
            W0  __            __  E0
                  \          /
                   |________|

                 <->
            length_taper

    """
    cross_section = gf.partial(cross_section, **kwargs)
    x = cross_section()
    cladding_offset = x.info["cladding_offset"]
    layers_cladding = x.info["layers_cladding"]
    layer = x.info["layer"]

    component = gf.Component()
    w_mmi = width_mmi
    w_taper = width_taper

    taper = taper(
        length=length_taper, width1=width, width2=w_taper, cross_section=cross_section
    )

    a = gap_mmi / 2 + width_taper / 2
    mmi = gf.components.rectangle(
        size=(length_mmi, w_mmi),
        layer=layer,
        centered=True,
        ports={
            "E": [(+length_mmi / 2, -a, w_taper), (+length_mmi / 2, +a, w_taper)],
            "W": [(-length_mmi / 2, -a, w_taper), (-length_mmi / 2, +a, w_taper)],
        },
    )

    mmi_section = component.add_ref(mmi)

    for port_name, port in mmi_section.ports.items():
        taper_ref = component << taper
        taper_ref.connect(port="2", destination=port)
        component.add_port(name=port_name, port=taper_ref.ports["1"])
        component.absorb(taper_ref)

    component.simulation_settings = dict(port_width=1.5e-6)
    component.absorb(mmi_section)

    layers_cladding = layers_cladding or []
    if layers_cladding:
        add_padding(
            component,
            default=cladding_offset,
            right=0,
            left=0,
            top=cladding_offset,
            bottom=cladding_offset,
            layers=layers_cladding,
        )
    return component


if __name__ == "__main__":
    c = mmi2x2(layer=(2, 0))
    c.show()
    c.pprint()
