from string import Template
from .model_descriptors.screen_size import ScreenSize
from .model_descriptors.mode_info import ModeInfo
from .model_descriptors.edid_descriptor import EDIDDescriptor
from subprocess import check_output
from functools import reduce
import re

MODE_FLAG_CODES = {
    "+hsync": 0x00000001,
    "-hsync": 0x00000002,
    "+vsync": 0x00000004,
    "-vsync": 0x00000008,
    "interlace": 0x00000010,
    "doublescan": 0x00000020,
    "csync": 0x00000040,
    "+csync": 0x00000080,
    "-csync": 0x00000100,
}


def get_mode_dict_from_list(modes_resouces):
    """
    Takes in a list of modes and returns a dictionary of them indexed by their IDs

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

    Parameters
    ----------
    mode_ids : list
        a list of mode IDs
    modes : dict
        a dictionary of modes indexed by their ids
    """
    return {mode_id: modes[mode_id] for mode_id in mode_ids}


def get_mode(width, height, refresh_rate, name, mode_id, interlace=False):
    """
    Generates a VESA CVT modeline from the given width height and refresh rate

    Parameters
    ----------
    width : int
        The width of the modeline
    height : int
        The height of the modeline
    refresh_rate : float
        The refresh rate of the modeline
    name : str
        The name of the mode
    mode_id : int
        The id to use for the mode
    interlace : bool
        Determines if the mode is interlaced

    Returns
    -------
    dict
        The generated modeline info
    """
    cvt_lines = check_output(["cvt", str(width), str(height), str(refresh_rate)])
    cvt_lines = str(cvt_lines).split("\\n")
    modeline_info = parse_modeline(
        cvt_lines[-2], name, mode_id, ["Interlace"] if interlace else []
    )
    return modeline_info


def parse_modeline(modeline, name, mode_id, additional_flags):
    """
    Parses the given modeline and returns a dictionary of properties
    """
    params = re.split(" +", modeline)
    mode = {
        "id": mode_id,
        "width": int(params[3]),
        "height": int(params[7]),
        "dot_clock": int(float(params[2]) * (10 ** 6)),
        "h_sync_start": int(params[4]),
        "h_sync_end": int(params[5]),
        "h_total": int(params[6]),
        "h_skew": 0,
        "v_sync_start": int(params[8]),
        "v_sync_end": int(params[9]),
        "v_total": int(params[10]),
        "name_length": len(name),
    }
    flags = []
    for i in range(11, len(params)):
        flags.append(params[i])
    for flag in additional_flags:
        flags.append(flag)

    mode["flags"] = reduce(
        lambda acc, val: acc | val, [MODE_FLAG_CODES[flag.lower()] for flag in flags]
    )

    return mode


###################################################
# External Functions (Used on an interface level) #
###################################################


def get_screen_sizes_from_list(screen_sizes):
    """
    Takes in a list of screen sizes and returns a dictionary of them indexed by their IDs

    Parameters
    ----------
    screen_sizes : list
        a list of screen sizes
    """
    return {idx: format_size(size) for idx, size in enumerate(screen_sizes)}


def format_mode(mode_id, mode):
    """
    Takes in a mode id and a mode object and return a dictionary containing the mode's width, height and refresh rate

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


def format_edid(edid_data):
    """
    Takes in EDID info and returns an EDIDDescriptor describing the relevant info of the monitor

    Parameters
    ----------
    edid_data : Edid
        The edid object describing the monitor

    Returns
    -------
    EDIDDescriptor
        The descriptor of relevant info of the edid
    """
    manufacturer = edid_data.manufacturer
    manufacturer_product_code = edid_data.product
    manufacturer_serial_number = edid_data.serial
    width = edid_data.width
    height = edid_data.height

    return EDIDDescriptor(
        manufacturer=manufacturer,
        manufacturer_product_code=manufacturer_product_code,
        manufacturer_serial_number=manufacturer_serial_number,
        width=width,
        height=height,
    )
