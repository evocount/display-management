from string import Template


def get_mode_dict_from_list(modes_resouce):
    """
    Takes in a list of modes and returns a dictionary of them indexed by their IDs
    ..........
    Parameters
    ----------
    modes_resouce : list
        a list of modes
    """
    modes_dict = {}
    for mode in modes_resouce:
        modes_dict[mode.id] = mode

    return modes_dict


def get_screen_sizes_from_list(screen_sizes):
    """
    Takes in a list of screen sizes and returns a dictionary of them indexed by their IDs
    ..........
    Parameters
    ----------
    screen_sizes : list
        a list of screen sizes
    """
    sizes_dict = {}
    for idx, size in enumerate(screen_sizes):
        sizes_dict[idx] = size

    return sizes_dict


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
    output_modes = {}
    for mode_id in mode_ids:
        output_modes[mode_id] = modes[mode_id]

    return output_modes


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
    """
    formatted_mode = {}
    mode_data = mode._data
    dot_clock = mode_data["dot_clock"]
    h_total = mode_data["h_total"]
    v_total = mode_data["v_total"]
    refresh_rate = dot_clock / (h_total * v_total)
    formatted_mode["id"] = mode_data["id"]
    formatted_mode["width"] = mode_data["width"]
    formatted_mode["height"] = mode_data["height"]
    formatted_mode["refresh_rate"] = refresh_rate

    return formatted_mode


def format_size(size):
    """
    Takes in a size object and returns a dictionary containing the size's width and height
    ..........
    Parameters
    ----------
    size : Size
        the size object
    """
    formatted_size = {}
    size_data = size._data
    formatted_size["width"] = size_data["width_in_pixels"]
    formatted_size["height"] = size_data["height_in_pixels"]

    return formatted_size
