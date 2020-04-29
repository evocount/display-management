import enum
from typing import Optional
from Xlib.error import XError
from Xlib.ext import randr
from Xlib.ext.randr import PROPERTY_RANDR_EDID
from pyedid.edid import Edid
from .utils import get_modes_from_ids, format_mode, format_edid
from .rotation import Rotation
from .entity import Entity
from .model_descriptors.output_descriptor import OutputDescriptor
from .model_descriptors.crtc_info import CRTCInfo
from .model_descriptors.crtc_config import CRTCConfig
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
    set_config(crtc_id, mode_id, x, y, rotation)
    disable()
    re_enable()
    get_edid()
    add_mode(mode_id)
    get_info()
    has_edid()
    relative_place(output, orientation)
    complete_crtc_config(config)

    Properties
    ----------
    Connected()
    CRTC_ID()
    CRTC_Info()
    CRTC_Config()

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
        self.__last_mode_id = active_mode_id
        self.__crtc_config = CRTCConfig(
            crtc=target_crtc_id,
            x=x,
            y=y,
            mode=active_mode_id,
            rotation=Rotation(rotation or Rotation.NO_ROTATION),
        )

        self.__config_timestamp = config_timestamp

    def get_available_modes_info(self):
        """
        Returns info about all available modes for this screen.

        Returns
        list
            A list of available modes
        """
        return [format_mode(mode_id, mode) for mode_id, mode in self.__modes.items()]

    def set_mode(self, mode_id: int, crtc_id: Optional[int] = None):
        """
        Sets the mode of the output to the one referenced by the mode_id

        Parameters
        ----------
        mode_id
            The ID of the mode to set
        crtc_id
            The crtc ID to connect to (default is None). If this output was previously not connected,
            this has to be specified

        Throws
        ------
        ResourceError
            If the mode_id provided is not in the list of supported mode ids for this output.
        """
        return self.set_config(CRTCConfig(mode=mode_id, crtc=crtc_id))

    def set_position(self, x: Optional[int] = None, y: Optional[int] = None):
        """
        Sets the position of the output.

        Parameters
        ----------
        x
            The x coordinate (default is current x coord)
        y
            The y coordinate (default is current y coord)
        """
        return self.set_config(CRTCConfig(x=x, y=y))

    def set_rotation(self, rotation: Optional[Rotation] = Rotation.NO_ROTATION):
        """
        Sets the rotation of the output.

        Parameters
        ----------
        rotation
            The rotation mode (default is no rotation)
        """
        return self.set_config(CRTCConfig(rotation=rotation))

    def disable(self):
        """
        Disables output if connected
        """
        return self.set_config(CRTCConfig(mode=0))

    def re_enable(self):
        """
        If this output was connected before, connects to the last crtc_id it was
        connected to with the mode that it was connected with.
        """
        if self.__crtc_config.crtc is not None and self.__last_mode_id:
            self.set_mode(self.__last_mode_id, self.__crtc_config.crtc)

    def set_config(self, config: CRTCConfig):
        """
        Sets crtc config.

        WARNING Does not adjust screen size! Use Screen.set_crtc_config instead
        to profit from automatic adjustment of screen size.

        Throws
        ------
        ResourceError
            If the mode_id provided is not in the list of supported mode ids for this output.
        """

        config = self.complete_crtc_config(config)

        if config.mode not in self.__modes and config.mode != 0:
            raise ResourceError(
                "Mode ID is not in the list of supported modes for this output, use add_mode to add it first."
            )

        result = self.__display.xrandr_set_crtc_config(
            config_timestamp=self.__config_timestamp,
            outputs=[self._id] if config.mode else [],
            **config.dict()
        )
        self.__config_timestamp = result._data["new_timestamp"]
        self.__last_mode_id = config.mode
        self.__crtc_config = config
        self.__is_connected = True

    def complete_crtc_config(self, config: CRTCConfig) -> CRTCConfig:
        """
        Returns crtc config where missing bits are filled with current config of this output.
        """
        fill = self.__crtc_config
        return CRTCConfig(
            crtc=fill.crtc if config.crtc is None else config.crtc,
            x=fill.x if config.x is None else config.x,
            y=fill.y if config.y is None else config.y,
            mode=fill.mode if config.mode is None else config.mode,
            rotation=fill.rotation if config.rotation is None else config.rotation,
        )

    def get_edid(self):
        """
        Returns the EDID of the monitor represented by the display

        Returns
        EDIDDescriptor
            The EDID info of the monitor associated with this output

        Throws
        ResourceError
            If the output does not have an EDID property exposed
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

        Throws
        InvalidStateError
            If output is not connected.
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

    def relative_place(self, output, orientation):
        """
        Places the output in a location relative to another output.

        Parameters
        output : Output
            The output to place relative to.
        orientation : Orientation
            The orientation relative to the other output

        Raises
        InvalidStateError
            If either this output or the one placed relative to are disconnected.
        """
        if not self.__is_connected:
            raise InvalidStateError("Output is not connected to any monitor")
        if not output.__is_connected:
            raise InvalidStateError(
                "Attempting to place this output relative to a disconnected output"
            )

        # TODO does not consider rotation

        other_output_crtc = output.CRTC_Info
        this_crtc = self.CRTC_Info
        new_x = None
        new_y = None
        if orientation == Orientation.LEFT_OF:
            new_x = other_output_crtc.x + other_output_crtc.width
            new_Y = other_output_crtc.y
        elif orientation == Orientation.RIGHT_OF:
            new_x = other_output_crtc.x - this_crtc.width
            new_Y = other_output_crtc.y
        elif orientation == Orientation.ABOVE:
            new_x = other_output_crtc.x
            new_Y = other_output_crtc.y + other_output_crtc.height
        elif orientation == Orientation.BELOW:
            new_x = other_output_crtc.x
            new_Y = other_output_crtc.y - this_crtc.height

        # TODO: check screen boundaries and adjust if possible
        self.set_position(new_x, new_y)

    @property
    def CRTC_Info(self) -> CRTCInfo:
        """
        CRTC information for this output or None if it is not connected.
        """
        if not self.__is_connected or not self.__crtc_config.crtc:
            return None

        mode_info = self.__display.xrandr_get_crtc_info(
            self.__crtc_config.crtc, self.__config_timestamp
        )._data
        self.__config_timestamp = mode_info["timestamp"]

        return CRTCInfo(mode_id=mode_info["mode"], **mode_info)

    @property
    def CRTC_Config(self) -> CRTCConfig:
        """
        Current CRTC config of this output.
        """
        return self.__crtc_config.copy()

    @property
    def Connected(self):
        """
        Whether this output is connected.

        Returns
        bool
            The output connection status.
        """
        return self.__is_connected

    @property
    def CRTC_ID(self):
        """
        CRTC ID this output is connected to or None if it is not connected

        Returns
        int
            The CRTC ID
        """
        return self.__crtc_config.crtc

    def get_info(self):
        """
        Returns a dictionary containing all relevant information about this output's resources.

        Returns
        -------
        OutputDescriptor
            The descriptor of the output
        """
        is_connected = self.__is_connected
        crtc_info = self.CRTC_Info

        return OutputDescriptor(
            id=self._id,
            name=self.__output._data["name"],
            current_mode_id=self.__crtc_config.mode,
            available_mode_ids=list(self.__modes.keys()),
            is_connected=is_connected,
            x=crtc_info.x if crtc_info is not None else None,
            y=crtc_info.y if crtc_info is not None else None,
            width=crtc_info.width if crtc_info is not None else None,
            height=crtc_info.height if crtc_info is not None else None,
            width_mm=self.__output._data["mm_width"],
            height_mm=self.__output._data["mm_height"],
            rotation=self.__crtc_config.rotation,
            # edid=self.get_edid() if is_connected and self.has_edid() else None,
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
            if is_connected and target_crtc_id
            else None
        )
        target_crtc_info_data = target_crtc_info._data if target_crtc_info else None
        x = target_crtc_info_data["x"] if target_crtc_info else None
        y = target_crtc_info_data["y"] if target_crtc_info else None
        rotation = target_crtc_info_data["rotation"] if target_crtc_info else None
        active_mode_id = target_crtc_info._data["mode"] if target_crtc_info else None
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


class Orientation(enum.Enum):
    """
    Represents the orientation of an output relative to another
    """

    LEFT_OF = 0
    RIGHT_OF = 1
    ABOVE = 2
    BELOW = 3
