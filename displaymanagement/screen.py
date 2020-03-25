from Xlib import X
from Xlib.ext import randr
from .output import Output
from .utils import (
    get_mode_dict_from_list,
    get_screen_sizes_from_list,
    format_mode,
    format_size,
    get_mode,
)
from .entity import Entity
from .model_descriptors.screen_descriptor import ScreenDescriptor
import random


class Screen(Entity):
    """
    Represents an X screen on a display.
    Inherits from Entity.

    Methods
    -------
    get_sizes()
    set_size(size_id)
    set_refresh_rate(rate)
    create_mode(self, name, width, height, refresh_rate, interlaced)
    get_info()
    
    Static Methods
    --------------
    load_from_identifier(display, screen_identifier)

    Properties
    ----------
    Outputs()
    """

    def __init__(
        self, id, screen, modes, outputs, crtc_ids, screen_size_id, config_timestamp
    ):
        """
        Parameters
        ----------
        id : int
            The ID of the screen.
        screen : XScreen
            The undelying x screen object.
        modes : dict
            A dictionary of modes supported by this screen indexed by their IDs.
        outputs : dict
            A dictionary of outputs connected for this screen indexed by their IDs.
        crtc_ids : list
            A list of crtc IDs.
        screen_size_ids : int
            The ID representing this screen size.
        config_timestamp : int
            A timestamp indicating when the last change on this screen occured.
        """
        super().__init__(id)
        self.__screen = screen
        self.__modes = modes
        self.__outputs = outputs
        self.__crtc_ids = crtc_ids
        self.__screen_size_id = screen_size_id
        self.__config_timestamp = config_timestamp

    def get_sizes(self):
        """
        Returns all possible sizes for this screen.
        """
        screen_info = self.__screen.root.xrandr_get_screen_info()
        sizes = get_screen_sizes_from_list(screen_info._data["sizes"])
        return sizes

    # BUG
    def set_size(self, size_id):
        """
        *BROKEN*
        Sets the size of the screen according to a size id from the list of possible sizes.

        Parameters
        ----------
        size_id : int
            The size id of the size to set.
        """
        # BUG: set_screen_config is possibly broken, or the params are incorrect
        # TODO: check for non existent id
        result = self.__screen.root.xrandr_set_screen_config(
            size_id, randr.Rotate_0, self.__config_timestamp, 0
        )
        self.__config_timestamp = result._data["config_timestamp"]
        self.__screen_size_id = size_id

    # BUG
    def set_refresh_rate(self, rate=0):
        """
        *BROKEN*
        Sets the refresh rate of the screen.

        Parameters
        ----------
        rate : int, optional
            The refresh rate to set(defaults to 0 which corresponds to autopicking the refresh rate).
        """
        # BUG: set_screen_config is possibly broken, or the params are incorrect
        result = self.__screen.root.xrandr_set_screen_config(
            self.__screen_size_id, randr.Rotate_0, self.__config_timestamp, 0
        )
        self.__config_timestamp = result._data["config_timestamp"]

    def create_mode(self, name, width, height, refresh_rate, interlaced=False):
        """
        Adds a mode to the list of modes of this screen and returns its ID

        Parameters
        ----------
        name : str
            The name of the mode
        width : int
            The widt of the mode
        height : int
            The height of the mode
        refresh_rate : float
            The refresh rate of the mode
        interlaced : bool
            If the mode is interlaced

        Returns
        -------
        int
            The id of the new mode
        """
        mode_id = random.randint(0, 0x7FFFFFFF)  # random id
        mode = get_mode(width, height, refresh_rate, name, mode_id, interlaced)
        self.__screen.root.xrandr_create_mode(mode, name)
        return mode_id

    @property
    def Outputs(self):
        """
        Returns a dictionary of all outputs associated with this screen indexed with their IDs.
        """
        return self.__outputs

    def get_info(self):
        """
        Returns a dictionary containing all relevant information about this screen's resources.

        Returns
        -------
        dict
        ScreenDescriptor
            The descriptor of the screen
        """
        sizes = self.get_sizes()
        screen_size = sizes[self.__screen_size_id] if len(sizes) > 0 else None
        return ScreenDescriptor(
            id=self._id,
            sizes=[size for size in sizes.values()],
            size=screen_size if screen_size is not None else None,
            outputs=[output.get_info() for output_id, output in self.__outputs.items()],
            modes=[
                format_mode(mode_id, mode) for mode_id, mode in self.__modes.items()
            ],
        )

    @staticmethod
    def load_from_identifier(display, screen_id):
        """
        Loads the screen specified by the screen_id and returns a corresponding screen object.

        Parameters
        ----------
        display : XDisplay
            The underlying X display which contains the referenced screen
        screen_id : int
            The ID of the screen
        
        Returns
        -------
        Screen
            The screen object
        """
        screen = display.screen(screen_id)
        resources = screen.root.xrandr_get_screen_resources()
        resources_data = resources._data
        modes = get_mode_dict_from_list(resources_data["modes"])
        output_ids = resources_data["outputs"]
        crtc_ids = resources_data["crtcs"]
        config_timestamp = resources_data["config_timestamp"]
        outputs = {}

        for output_id in output_ids:
            outputs[output_id] = Output.load_from_identifier(
                display, screen, output_id, modes, config_timestamp
            )

        screen_info = screen.root.xrandr_get_screen_info()
        screen_size_id = screen_info._data["size_id"]
        return Screen(
            screen_id,
            screen,
            modes,
            outputs,
            crtc_ids,
            screen_size_id,
            config_timestamp,
        )
