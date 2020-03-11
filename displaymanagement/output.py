from Xlib.ext import randr
from .utils import get_modes_from_ids, format_mode
import json

class Output:
    def __init__(self, display, screen, output, output_id, is_connected, 
            modes, active_mode_id, target_crtc_id, x, y, rotation, config_timestamp):
        self.__display = display
        self.__screen = screen
        self.__output = output
        self.__id = output_id
        self.__is_connected = is_connected
        self.__modes = modes
        self.__active_mode_id = active_mode_id
        self.__target_crtc_id = target_crtc_id
        self.__x = x
        self.__y = y
        self.__rotation = rotation
        self.__config_timestamp = config_timestamp

    def get_available_modes_info(self):
        return [format_mode(mode_id, mode) for mode_id, mode in self.__modes.items()]

    def set_mode(self, mode_id):
        result = self.__display.xrandr_set_crtc_config(self.__target_crtc_id, self.__config_timestamp, \
            self.__x, self.__y, mode_id, self.__rotation, [self.__id])
        self.__config_timestamp = result._data['new_timestamp']
        self.__active_mode_id = mode_id

    def set_position(self, x=None, y=None):
        if x is None: x = self.__x
        if y is None: y = self.__y
        result = self.__display.xrandr_set_crtc_config(self.__target_crtc_id, self.__config_timestamp, \
            x, y, self.__active_mode_id, self.__rotation, [self.__id])
        self.__config_timestamp = result._data['new_timestamp']
        self.__x = x
        self.__y = y

    def set_rotation(self, rotation=randr.Rotate_0):
        result = self.__display.xrandr_set_crtc_config(self.__target_crtc_id, self.__config_timestamp, \
            self.__x, self.__y, self.__active_mode_id, rotation, [self.__id])
        self.__config_timestamp = result._data['new_timestamp']
        self.__rotation = rotation

    def get_info(self):
        info = {
            "id": self.__id,
            "current_mode_id": self.__active_mode_id if self.__active_mode_id is not None else None,
            "available_mode_ids": list(self.__modes.keys()),
            "is_connected": self.__is_connected
        }

        return info

    def toJSON(self):
        output_info = self.get_info()
        return json.dumps(output_info)

    @staticmethod
    def load_from_identifier(display, screen, output_id, screen_modes, config_timestamp):
        output = display.xrandr_get_output_info(output_id, config_timestamp)
        output_data = output._data
        is_connected = (output_data['connection'] == randr.Connected)
        output_modes = get_modes_from_ids(output_data['modes'], screen_modes)
        target_crtc_id = output_data['crtc']
        target_crtc_info = display.xrandr_get_crtc_info(target_crtc_id, config_timestamp) if is_connected else None
        target_crtc_info_data = target_crtc_info._data if target_crtc_info is not None else None
        x = target_crtc_info_data['x'] if is_connected else None
        y = target_crtc_info_data['y'] if is_connected else None
        rotation = target_crtc_info_data['rotation'] if is_connected else None
        active_mode_id = target_crtc_info._data['mode'] if is_connected else None
        return Output(display, screen, output, output_id, is_connected, output_modes,
                active_mode_id, target_crtc_id, x, y, rotation, config_timestamp)
