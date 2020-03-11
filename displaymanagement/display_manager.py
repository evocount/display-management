from Xlib import display
from Xlib.ext import randr
from .screen import Screen
import json

class DisplayManager:
    def __init__(self, display_identifier=":0"):
        #TODO: invalid display identifier
        self.__screens = []
        self.__display_identifier = display_identifier
        self.__display = None
        self.init_display()

    def init_display(self):
        #TODO: check xrandr_get_screen_resource errors throw
        self.__display = display.Display(self.__display_identifier)

    def get_screen_count(self):
        return self.__display.screen_count();

    def load_screen(self, screen_identifier=None):
        screen = Screen.load_from_identifier(self.__display, screen_identifier)
        self.__screens.append(screen)

    def load_all_screens(self):
        self.__screens = []
        screen_count = self.get_screen_count()

        for i in range(screen_count):
            self.load_screen(i)

    @property
    def Screens(self):
        return self.__screens

    def get_info(self):
        self.load_all_screens()

        display_info = {
            "id": self.__display_identifier,
            "screen_count": self.get_screen_count(),
            "screens": [screen.get_info() for screen in self.__screens]
        }

        return display_info

    def toJSON(self):
        display_info = self.get_info()
        return json.dumps(display_info)
        