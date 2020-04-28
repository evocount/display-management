from typing import Optional
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
from .model_descriptors.screen_descriptor import ScreenDescriptor, ScreenSizeRange
from .model_descriptors.screen_size import ScreenSize
from .model_descriptors.crtc_info import CRTCInfo
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
    get_size_range()
    get_crtc_info()

    Static Methods
    --------------
    load_from_identifier(display, screen_identifier)

    Properties
    ----------
    Outputs()
    CRTC_IDs()
    """

    def __init__(
        self,
        id,
        screen,
        display,
        modes,
        outputs,
        crtc_ids,
        width,
        height,
        width_mm,
        height_mm,
        config_timestamp,
    ):
        """
        Parameters
        ----------
        id : int
            The ID of the screen.
        screen : XScreen
            The underlying x screen object.
        display : XDisplay
            The underlying X display object which contains this screen.
        modes : dict
            A dictionary of modes supported by this screen indexed by their IDs.
        outputs : dict
            A dictionary of outputs connected for this screen indexed by their IDs.
        crtc_ids : list
            A list of crtc IDs.
        width
            width of screen in pixels
        height
            height of screen in pixels
        width_mm
            width of screen in mm
        height_mm
            height of screen in mm
        config_timestamp : int
            A timestamp indicating when the last change on this screen occured.
        """
        super().__init__(id)
        self.__screen = screen
        self.__display = display
        self.__modes = modes
        self.__outputs = outputs
        self.__crtc_ids = crtc_ids
        self.__width = width
        self.__height = height
        self.__width_mm = width_mm
        self.__height_mm = height_mm
        self.__config_timestamp = config_timestamp

    def get_sizes(self):
        """
        Returns all possible sizes for this screen.
        """
        screen_info = self.__screen.root.xrandr_get_screen_info()
        sizes = get_screen_sizes_from_list(screen_info._data["sizes"])
        return sizes

    def get_size_range(self):
        """
        Returns the size range allowed for this screen.
        """
        range = self.__screen.root.xrandr_get_screen_size_range()
        return ScreenSizeRange(
            min_width=range._data["min_width"],
            max_width=range._data["max_width"],
            min_height=range._data["min_height"],
            max_height=range._data["max_height"],
        )

    def set_size(
        self,
        width: int,
        height: int,
        dpi: Optional[int] = None,
        width_mm: Optional[int] = None,
        height_mm: Optional[int] = None,
    ):
        """
        Sets the size of the screen.

        Parameters
        ----------
        width
            The width in pixels to set
        height
            The height in pixels to set
        dpi
            DPI to use for screen (??)
        width_mm
            The width in mm to set when dpi is not given
        height_mm
            The height in mm to set when dpi is not given
        """
        if dpi is not None:
            width_mm = int((25.4 * width) / dpi)
            height_mm = int((25.4 * height) / dpi)
        else:
            width_mm = width_mm or self.__width_mm
            height_mm = height_mm or self.__height_mm

        self.__screen.root.xrandr_set_screen_size(width, height, width_mm, height_mm)

        self.__width = width
        self.__height = height
        self.__width_mm = width_mm
        self.__height_mm = height_mm

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
        # xlib sets the mode id automatically
        mode = get_mode(width, height, refresh_rate, name, 0, interlaced)
        mode_id = self.__screen.root.xrandr_create_mode(mode, name)
        return mode_id._data["mode"]

    @property
    def Outputs(self):
        """
        Returns a dictionary of all outputs associated with this screen indexed with their IDs.
        """
        return self.__outputs

    @property
    def CRTC_IDs(self):
        """
        Returns the CRTC IDs associated with the video device driving this screen
        """
        return self.__crtc_ids

    def get_crtc_info(self, crtc_id: int) -> CRTCInfo:
        """
        Returns crtc info for given id.
        """
        mode_info = self.__display.xrandr_get_crtc_info(
            crtc_id, self.__config_timestamp
        )._data

        return CRTCInfo(mode_id=mode_info["mode"], **mode_info)

    def get_info(self):
        """
        Returns a dictionary containing all relevant information about this screen's resources.

        Returns
        -------
        dict
        ScreenDescriptor
            The descriptor of the screen
        """
        return ScreenDescriptor(
            id=self._id,
            size=ScreenSize(width=self.__width, height=self.__height),
            outputs=[output.get_info() for output_id, output in self.__outputs.items()],
            modes=[
                format_mode(mode_id, mode) for mode_id, mode in self.__modes.items()
            ],
            size_range=self.get_size_range(),
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

        return Screen(
            screen_id,
            screen,
            display,
            modes,
            outputs,
            crtc_ids,
            screen.width_in_pixels,
            screen.height_in_pixels,
            screen.width_in_mms,
            screen.height_in_mms,
            config_timestamp,
        )
