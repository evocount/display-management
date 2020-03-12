from Xlib.ext import randr
from .utils import get_modes_from_ids, format_mode
from .xentity import XEntity
from .rotation import Rotation


class Output(XEntity):
    """
    Represents an output port (real or virtual) defined for an X screen
    .......
    Methods
    -------
    get_available_modes_info()
    set_mode(mode_id)
    set_position(x,y)
    set_rotation(rotation)
    get_info()

    Static Methods
    --------------
    load_from_identifier(display,screen,output_id,screen_modes,config_timestamp)
    """

    def __init__(
        self,
        id,
        display,
        screen,
        output,
        is_connected,
        modes,
        active_mode_id,
        target_crtc_id,
        x,
        y,
        rotation,
        config_timestamp,
    ):
        """
        Parameters
        ----------
        id : int
            The ID of the output.
        display : XDisplay
            The underlying X display object which contains this output.
        screen : XScreen
            The underlying X screen object which contains this output.
        is_connected : bool
            Whether this output is connected or not.
        modes : dict
            The modes allowed for this output indexed by their IDs.
        active_mode_id : int
            The ID of the mode which is currently assigned to this output.
        target_crtc_id : int
            The crtc that this output is connected to in case it is connected.
        x : int
            The x position of the output.
        y : int
            The y position of the output.
        rotation : int
            The current rotation mode of the screen.
        config_timestamp : int
            The time at which the screen which contains this object was last changed. 
        """
        super().__init__(id)
        self.__display = display
        self.__screen = screen
        self.__output = output
        self.__is_connected = is_connected
        self.__modes = modes
        self.__active_mode_id = active_mode_id
        self.__target_crtc_id = target_crtc_id
        self.__x = x
        self.__y = y
        self.__rotation = rotation
        self.__config_timestamp = config_timestamp

    def get_available_modes_info(self):
        """
        Returns info about all available modes for this screen.
        ......
        Returns
        list
            A list of available modes
        """
        return [format_mode(mode_id, mode) for mode_id, mode in self.__modes.items()]

    def set_mode(self, mode_id):
        """
        Sets the mode of the output to the one referenced by the mode_id
        ..........
        Parameters
        ----------
        mode_id : int
            The ID of the mode to set
        """
        result = self.__display.xrandr_set_crtc_config(
            self.__target_crtc_id,
            self.__config_timestamp,
            self.__x,
            self.__y,
            mode_id,
            self.__rotation,
            [self._id],
        )
        self.__config_timestamp = result._data["new_timestamp"]
        self.__active_mode_id = mode_id

    def set_position(self, x=None, y=None):
        """
        Sets the position of the output.
        ..........
        Parameters
        ----------
        x : int, optional
            The x coordinate (default is current x coord).
        y : int, optional
            The y coordinate (default is current y coord).
        """
        if x is None:
            x = self.__x
        if y is None:
            y = self.__y
        result = self.__display.xrandr_set_crtc_config(
            self.__target_crtc_id,
            self.__config_timestamp,
            x,
            y,
            self.__active_mode_id,
            self.__rotation,
            [self._id],
        )
        self.__config_timestamp = result._data["new_timestamp"]
        self.__x = x
        self.__y = y

    def set_rotation(self, rotation=Rotation.NO_ROTATION):
        """
        Sets the rotation of the output.
        ..........
        Parameters
        ----------
            rotation : Rotation, optional
                The rotation mode (default is no rotation)
        """
        result = self.__display.xrandr_set_crtc_config(
            self.__target_crtc_id,
            self.__config_timestamp,
            self.__x,
            self.__y,
            self.__active_mode_id,
            rotation,
            [self._id],
        )
        self.__config_timestamp = result._data["new_timestamp"]
        self.__rotation = rotation

    def get_info(self):
        """
        Returns a dictionary containing all relevant information about this output's resources.
        ........
        Returns
        -------
        dict
            Format:
            {
                "id": int
                "current_mode_id": int,
                "available_mode_ids": [int],
                "is_connected": bool
            }
        """
        output_info = {
            "id": self._id,
            "current_mode_id": self.__active_mode_id
            if self.__active_mode_id is not None
            else None,
            "available_mode_ids": list(self.__modes.keys()),
            "is_connected": self.__is_connected,
        }

        return output_info

    @staticmethod
    def load_from_identifier(
        display, screen, output_id, screen_modes, config_timestamp
    ):
        """
        Loads the outputs identified by the output_id and returns the corresponding Output object.
        ..........
        Parameters
        ----------
        display : XDisplay
            The x display which contains this output.
        screen : XScreen
            The x screen which contains this output.
        output_id : int
            The ID of the output to load.
        screen_modes : dict
            A dictionary of the allowed modes from the parent screen for this output.
        config_timestamp : int
            The time at which the last change to the screen containing this output changed

        Returns
        -------
        Output
            The output object
        """
        output = display.xrandr_get_output_info(output_id, config_timestamp)
        output_data = output._data
        is_connected = output_data["connection"] == randr.Connected
        output_modes = get_modes_from_ids(output_data["modes"], screen_modes)
        target_crtc_id = output_data["crtc"]
        target_crtc_info = (
            display.xrandr_get_crtc_info(target_crtc_id, config_timestamp)
            if is_connected
            else None
        )
        target_crtc_info_data = (
            target_crtc_info._data if target_crtc_info is not None else None
        )
        x = target_crtc_info_data["x"] if is_connected else None
        y = target_crtc_info_data["y"] if is_connected else None
        rotation = target_crtc_info_data["rotation"] if is_connected else None
        active_mode_id = target_crtc_info._data["mode"] if is_connected else None
        return Output(
            output_id,
            display,
            screen,
            output,
            is_connected,
            output_modes,
            active_mode_id,
            target_crtc_id,
            x,
            y,
            rotation,
            config_timestamp,
        )
