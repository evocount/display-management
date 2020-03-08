from Xlib import display
from Xlib.ext import randr

default_display = display.Display()
def get_mode_dict_from_list(mode_list):
    dict = {}
    for mode in mode_list:
        dict[mode.id] = mode
    return dict
    
def get_connected_outputs(screen_number=None):
    #query required resources
    root = default_display.screen().root
    resources = root.xrandr_get_screen_resources()
    resources_data = resources._data
    output_modes = get_mode_dict_from_list(resources_data['modes'])
    outputs = {}

    #filter connected outputs
    for output in resources_data['outputs']:
        output_data = default_display.xrandr_get_output_info(output, resources_data['config_timestamp'])._data
        
        if output_data['connection'] == randr.Connected:
            #map all mode xids to the corresponding actual modes
            output_data['modes'] = {mode_xid: output_modes[mode_xid] for mode_xid in output_data['modes']}
            outputs[output] = output_data

    return outputs

#sets output props(roughly corresponds to setting resolution, refresh rate and coordinates)
def set_output_props(output_xid, mode_xid, x_pos=0, y_pos=0, rotation=randr.Rotate_0):
    output = get_connected_outputs()[output_xid]
    #TODO: Handle not connected output
    #TODO: Check if allowed mode
    #TODO: Check if crtc exists
    crtc = output['crtc']
    timestamp = default_display.screen().root.xrandr_get_screen_resources()._data['config_timestamp'];
    default_display.xrandr_set_crtc_config(crtc, timestamp, x_pos, y_pos, mode_xid, rotation, [output_xid])

#
def set_screen_props(screen_size_id, rotation=randr.Rotate_0, refresh_rate=0):
    root = default_display.screen().root
    config_timestamp = root.xrandr_get_screen_resources()._data['config_timestamp']
    root.xrandr_set_screen_config(screen_size_id, rotation, config_timestamp)

def set_screen_size(width, height):
    default_display.screen().root.xrandr_set_screen_size(widht, height)

def get_screen_info():
    return default_display.screen().root.xrandr_get_screen_info()

#sets the default
def set_primary_output(output_xid):
    default_display.screen().root.xrandr_set_output_primary(output_xid)

def get_primary_output():
    default_display.screen().root.xrandr_get_output_primary()

