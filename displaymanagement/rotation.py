import enum


class Rotation(enum.Enum):
    """
    Represents the possible orientations allowed 
    Note: mirrored from randr
    """

    NO_ROTATION = 1
    ROTATE_90 = 2
    ROTATE_180 = 4
    ROTATE_270 = 8
    REFLECT_X = 16
    REFLECT_Y = 32
