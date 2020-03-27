from Xlib.ext import randr
from Xlib.ext.randr import PROPERTY_RANDR_EDID
from pyedid.edid import Edid
from .utils import get_modes_from_ids, format_mode, format_edid
from .rotation import Rotation
from .entity import Entity
from .model_descriptors.output_descriptor import OutputDescriptor
from .resources import get_pnp_info
from .exceptions import ResourceError, InvalidStateError


class Output(Entity):
    """
    Represents an output port (real or virtual) defined for an X screen
    Inherits from Entity

    Methods
    -------
    get_available_modes_info()
    set_mode(mode_id, crtc_id)
    set_position(x,y)
    set_rotation(rotation)
    disable()
    re_enable()
    get_edid()
    add_mode(mode_id)
    get_info()
    has_edid()

    Properties
    ----------
    Connected()
    CRTC_ID()

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

        Returns
        list
            A list of available modes
        """
        return [format_mode(mode_id, mode) for mode_id, mode in self.__modes.items()]

    def set_mode(self, mode_id, crtc_id=None):
        """
        Sets the mode of the output to the one referenced by the mode_id

        Parameters
        ----------
        mode_id : int
            The ID of the mode to set
        crtc_id : int, optional
            The crtc ID to connect to (default is None). If this output was previously not connected,
            this has to be specified
        """
        if crtc_id is None:
            crtc_id = self.__target_crtc_id

        if mode_id not in self.__modes:
            raise ResourceError(
                "Mode ID is not in the list of supported modes for this output, use add_mode to add it first."
            )

        result = self.__display.xrandr_set_crtc_config(
            crtc_id,
            self.__config_timestamp,
            self.__x,
            self.__y,
            mode_id,
            self.__rotation,
            [self._id],
        )
        self.__config_timestamp = result._data["new_timestamp"]
        self.__active_mode_id = mode_id
        self.__target_crtc_id = crtc_id
        self.__is_connected = True

    def set_position(self, x=None, y=None):
        """
        Sets the position of the output.

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
            rotation.value,
            [self._id],
        )
        self.__config_timestamp = result._data["new_timestamp"]
        self.__rotation = rotation.value

    def disable(self):
        """
        Disables output if connected
        """
        if self.__is_connected:
            result = self.__display.xrandr_set_crtc_config(
                self.__target_crtc_id,
                self.__config_timestamp,
                self.__x,
                self.__y,
                0,
                self.__rotation,
                [],
            )
            self.__config_timestamp = result._data["new_timestamp"]

    def re_enable(self):
        """
        If this output was connected before, connects to the last crtc_id it was
        connected to with the mode that it was connected with.
        """
        if self.__target_crtc_id is not None:
            self.set_mode(self.__active_mode_id, self.__target_crtc_id)

    def get_edid(self):
        """
        Returns the EDID of the monitor represented by the display

        Returns
        EDIDInfo
            The EDID info of the monitor associated with this output
        """
        if not self.has_edid():
            raise ResourceError("Connected monitor does not provide an EDID property")

        EDID_ATOM = self.__display.intern_atom(PROPERTY_RANDR_EDID)
        EDID_TYPE = 19
        EDID_LENGTH = 128
        edid_info = self.__display.xrandr_get_output_property(
            self._id, EDID_ATOM, EDID_TYPE, 0, EDID_LENGTH
        )

        edid = Edid(bytes(edid_info._data["value"]), get_pnp_info())
        return format_edid(edid)

    def has_edid(self):
        """
        Checks if the output's connected monitor exposes an EDID property.

        Returns
        bool
            Whether the connected monitor exposes an EDID property or not
        """
        if not self.__is_connected:
            raise InvalidStateError("Output is not connected to any monitor")

        EDID_ATOM = self.__display.intern_atom(PROPERTY_RANDR_EDID)
        EDID_TYPE = 19
        EDID_LENGTH = 128
        edid_info = self.__display.xrandr_get_output_property(
            self._id, EDID_ATOM, EDID_TYPE, 0, EDID_LENGTH
        )

        if edid_info._data["property_type"] == 0:
            return False

        return True

    def add_mode(self, mode_id):
        """
        Adds a mode to be used by this output if it is within the containing screen's modes and
        it is applicable for this output
        
        Parameters
        mode_id : int
            The mode id to add
        """
        self.__display.xrandr_add_output_mode(self._id, mode_id)

    @property
    def Connected(self):
        """
        Returns true if the output is connected.

        Returns
        bool
            The output connection status.
        """
        return self.__is_connected

    @property
    def CRTC_ID(self):
        """
        Returns the CRTC ID this output is connectd to or None if it is not connected
        
        Returns
        int
            The CRTC ID
        """
        return self.__target_crtc_id

    def get_info(self):
        """
        Returns a dictionary containing all relevant information about this output's resources.

        Returns
        -------
        OutputDescriptor
            The descriptor of the output
        """
        current_mode_id = (
            self.__active_mode_id if self.__active_mode_id is not None else None
        )
        return OutputDescriptor(
            id=self._id,
            current_mode_id=current_mode_id,
            available_mode_ids=list(self.__modes.keys()),
            is_connected=self.__is_connected,
        )

    @staticmethod
    def load_from_identifier(
        display, screen, output_id, screen_modes, config_timestamp
    ):
        """
        Loads the outputs identified by the output_id and returns the corresponding Output object.

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
