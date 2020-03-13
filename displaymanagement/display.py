from Xlib import display
from Xlib.ext import randr
from .screen import Screen
from .entity import Entity


class Display(Entity):
    """
    Represents an X display which corresponds to an X server.
    Inherits from Entity
    .......
    Methods
    -------
    init_display()
    get_screen_count()
    load_screen()
    load_all_screens()
    get_info()

    Properties
    ----------
    Screens()
    """

    def __init__(self, id=":0"):
        """
        Parameters
        ----------
        id : str, optional
            The string id for this display to load (default is ":0").   
            Note: Corresponds to the DISPLAY environment variable.
        """
        # TODO: invalid display identifier
        super().__init__(id)
        self.__screens = []
        self.__display = None

    def init_display(self):
        """
        Loads the display resources(Excludes loading associated screens).
        """
        # TODO: check xrandr_get_screen_resource errors throw
        self.__display = display.Display(self._id)

    def get_screen_count(self):
        """
        Returns the number of screens associated with this display.
        """
        return self.__display.screen_count()

    def load_screen(self, screen_identifier=None):
        """
        Loads the screen resources identified by the screen_identifier for this display.
        ..........
        Parameters
        ----------
        screen_identifier : int, optional
            The screen ID for the screen to load (Default is None, the default screen for the display).
        """
        # TODO: Check if screen already in loaded screens
        screen = Screen.load_from_identifier(self.__display, screen_identifier)
        self.__screens.append(screen)

    def load_all_screens(self):
        """
        Loads all screens associated with this display.
        """
        self.__screens = []
        screen_count = self.get_screen_count()

        for i in range(screen_count):
            self.load_screen(i)

    @property
    def Screens(self):
        """
        Returns the list of all loaded screens associated with this display.
        .......
        Returns
        -------
        list
            A list of Screens
        """
        return self.__screens

    def get_info(self):
        """
        Returns a dictionary containing all relevant information about this display's loaded resources.
        ........
        Returns
        -------
        dict
            Format:
            {
                "id": str,
                "screen_count": int,
                "screens": [screen_info] 
            }
        """
        display_info = {
            "id": self._id,
            "screen_count": self.get_screen_count(),
            "screens": [screen.get_info() for screen in self.__screens],
        }

        return display_info
