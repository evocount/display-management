from string import Template
from .model_descriptors.screen_size import ScreenSize
from .model_descriptors.mode_info import ModeInfo
from .model_descriptors.edid_descriptor import EDIDDescriptor


def get_mode_dict_from_list(modes_resouces):
    """
    Takes in a list of modes and returns a dictionary of them indexed by their IDs
    ..........
    Parameters
    ----------
    modes_resouces : list
        a list of modes
    """
    return {mode.id: mode for mode in modes_resouces}


def get_modes_from_ids(mode_ids, modes):
    """
    Takes in a list of mode ids and a list of modes and returns a dictionary 
    of the provided mode ids with their correpsonding mode objects.
    ..........
    Parameters
    ----------
    mode_ids : list
        a list of mode IDs
    modes : dict
        a dictionary of modes indexed by their ids
    """
    return {mode_id: modes[mode_id] for mode_id in mode_ids}


#################################################
# External Functions (Used on interface level) #
#################################################


def get_screen_sizes_from_list(screen_sizes):
    """
    Takes in a list of screen sizes and returns a dictionary of them indexed by their IDs
    ..........
    Parameters
    ----------
    screen_sizes : list
        a list of screen sizes
    """
    return {idx: format_size(size) for idx, size in enumerate(screen_sizes)}


def format_mode(mode_id, mode):
    """
    Takes in a mode id and a mode object and return a dictionary containing the mode's width, height and refresh rate
    ..........
    Parameters
    ----------
    mode_id : int
        the id of the mode
    mode : mode_object
        the mode object

    Returns
    -------
    ModeInfo
        A descriptor of the mode info
    """
    dot_clock = mode._data["dot_clock"]
    h_total = mode._data["h_total"]
    v_total = mode._data["v_total"]
    refresh_rate = dot_clock / (h_total * v_total)

    return ModeInfo(
        id=mode._data["id"],
        width=mode._data["width"],
        height=mode._data["height"],
        refresh_rate=refresh_rate,
    )


def format_size(size):
    """
    Takes in a size object and returns a dictionary containing the size's width and height
    ..........
    Parameters
    ----------
    size : Size
        the size object

    Returns
    -------
    ScreenSize
        A descriptor of the screen size
    """
    return ScreenSize(
        width=size._data["width_in_pixels"], height=size._data["height_in_pixels"]
    )


def decode_edid(edid_data):
    # TODO: implement decoding logic and use it
    manufacturer_id = None
    manufacturer_product_code = None
    manufacturer_serial_number = None
    aspect_ratio = None
    return EDIDDescriptor(
        manufacturer_id=manufacturer_id,
        manufacturer_product_code=manufacturer_product_code,
        manufacturer_serial_number=manufacturer_serial_number,
        aspect_ratio=aspect_ratio,
    )
