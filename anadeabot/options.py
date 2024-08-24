from enum import StrEnum, auto


class TShirtColor(StrEnum):
    WHITE = auto()
    BLACK = auto()
    BLUE = auto()
    RED = auto()
    GREEN = auto()
    # CUSTOM = auto()


class TShirtStyle(StrEnum):
    CREW_NECK = 'Crew Neck'
    V_NECK = 'V-Neck'
    LONG_SLEEVE = 'Long Sleeve'
    TANK_TOP = 'Tank Top'


class TShirtGender(StrEnum):
    MALE = 'male'
    FEMALE = 'female'
    UNISEX = 'unisex'


class TShirtSize(StrEnum):
    XS = 'XS'
    S = 'S'
    M = 'M'
    L = 'L'
    XL = 'XL'
    XLL = 'XLL'


class TShirtPrintingOptions(StrEnum):
    SCREEN_PRINTING = 'Screen Printing'
    EMBROIDERY = 'Embroidery'
    HEAT_TRANSFER = 'Heat Transfer'
    DIRECT_TO_GARMENT = 'Direct-to-Garment'


class TShirtOption(StrEnum):
    COLOR = auto()
    STYLE = auto()
    GENDER = auto()
    SIZE = auto()
    PRINTING = auto()
