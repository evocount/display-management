from pyedid.helpers.registry import Registry


PNP_REGISTRY = None


def load_pnp_info(file_dir="displaymanagement/resources/pnp_info.csv"):
    """
    Loads the PNP registry from a CSV file

    Parameters
    ----------
    file_dir : str, optional
        The directory of the file from which the PNP info is loaded
    """
    global PNP_REGISTRY
    PNP_REGISTRY = Registry.from_csv(file_dir)


def get_pnp_info():
    """
    Loads the default PNP info if none exist and returns it

    Returns
    -------
    dict
        A dictionary of the loaded PNP info
    """
    if PNP_REGISTRY is None:
        load_pnp_info()
    return PNP_REGISTRY
