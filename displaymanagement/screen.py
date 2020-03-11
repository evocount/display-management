from Xlib import X
from Xlib.ext import randr
from .output import Output
from .utils import get_mode_dict_from_list, get_screen_sizes_from_list, format_mode, format_size
import json

class Screen:
    def __init__(self, screen, id, modes, outputs, crtc_ids, screen_size_id, config_timestamp):
        self.__screen = screen
        self.__id = id
        self.__modes = modes
        self.__outputs = outputs
        self.__crtc_ids = crtc_ids
        self.__screen_size_id = screen_size_id
        self.__config_timestamp = config_timestamp

    def get_sizes(self):
        screen_info = self.__screen.root.xrandr_get_screen_info()
        sizes = get_screen_sizes_from_list(screen_info._data['sizes'])
        return sizes

    def set_size(self, size_id):
        #TODO: check for non existent id
        result = self.__screen.root.xrandr_set_screen_config(size_id, randr.Rotate_0, self.__config_timestamp, 0)
        self.__config_timestamp = result._data['config_timestamp']
        self.__screen_size_id = size_id

    def set_refresh_rate(self, rate=0):
        result = self.__screen.root.xrandr_set_screen_config(self.__screen_size_id,
                randr.Rotate_0, self.__config_timestamp, 0)
        self.__config_timestamp = result._data['config_timestamp']

    @property
    def Outputs(self):
        return self.__outputs

    def get_info(self):
        sizes = self.get_sizes()
        screen_size = sizes[self.__screen_size_id] if len(sizes) > 0 else None
        screen_info = {
            "sizes": [format_size(size) for size in sizes.values()],
            "size": format_size(screen_size) if screen_size is not None else None,
            "id": self.__id,
            "outputs": [output.get_info() for output_id, output in self.__outputs.items()],
            "modes": [format_mode(mode_id, mode) for mode_id, mode in self.__modes.items()]
        }
        
        return screen_info

    def toJSON(self):
        screen_info = self.get_info()
        return json.dumps(screen_info)

    @staticmethod
    def load_from_identifier(display, screen_identifier):
        screen = display.screen(screen_identifier);
        resources = screen.root.xrandr_get_screen_resources()
        resources_data = resources._data
        modes = get_mode_dict_from_list(resources_data['modes'])
        output_ids = resources_data['outputs']
        crtc_ids = resources_data['crtcs']
        config_timestamp = resources_data['config_timestamp']
        outputs = {}

        for output_id in output_ids:
            outputs[output_id] = Output.load_from_identifier(display, screen, output_id, modes, config_timestamp)
            
        screen_info = screen.root.xrandr_get_screen_info()
        screen_size_id = screen_info._data['size_id']
        return Screen(screen, screen_identifier, modes, outputs, crtc_ids, screen_size_id, config_timestamp)
