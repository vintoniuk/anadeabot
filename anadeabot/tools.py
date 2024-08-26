from langchain_core.tools import tool

from anadeabot import options
from anadeabot.decorators import registry
from anadeabot.helpers import enum_to_list

option_tools, get_options_tool = registry()


@get_options_tool
@tool
def get_color_options() -> list[str]:
    """Call this tool if you need to know available options for COLOR of a T-shirt.
    The color is the main color of a fabric a T-shirt is made of, that is the
    background color, not taking into account color of decorations."""
    return enum_to_list(options.TShirtColor) + ['custom']


@get_options_tool
@tool
def get_size_options() -> list[str]:
    """Call this tool if you need to know available options for SIZE of a T-shirt.
    The size of a T-shirt determines whether a person will fit into the clothing or
    whether it is too small or too large for a particular person. For example,
    children need smaller sizes like XS or S, but adults need sizes such as M, L.
    For people with big bodies a T-shirt of size XL or XLL may be necessary."""
    return enum_to_list(options.TShirtSize)


@get_options_tool
@tool
def get_style_options() -> list[str]:
    """Call this tool if you need to know available options for STYLE of a T-shirt.
    The style of a T-shirt determines whether it has sleeves or not, or which fabric
    it is made of, and whether it is appropriate for female or male body."""
    return enum_to_list(options.TShirtStyle)


@get_options_tool
@tool
def get_gender_options() -> list[str]:
    """Call this tool if you need to know available options for GENDER of a T-shirt.
    The gender means whether the T-shirt is suitable for a man or a woman or similar
    in this manner. Whether a T-shirt is suitable for a specific gender can depend
    on its color, size, style, or a picture on the clothing."""
    return enum_to_list(options.TShirtGender)


@get_options_tool
@tool
def get_printing_options_options() -> list[str]:
    """Call this tool if you need to know available PRINTING OPTIONS of a T-shirt.
    A printing option or a method of printing is the method of putting a picture
    onto a fabric. It determines the material the image is made of or quality
    of an image. Embroidery for example produces very stylish pictures made of
    special threads, and direct-to-garment printing sprays ink on the fabric."""
    return enum_to_list(options.TShirtPrintingOptions)
