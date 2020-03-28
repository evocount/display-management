from Xlib import display
from Xlib.ext import randr
from .screen import Screen
from .entity import Entity
from .model_descriptors.display_descriptor import DisplayDescriptor
from .validation import is_valid_display_identifier
from .exceptions import ResourceError


class Display(Entity):
    """
    Represents an X display which corresponds to an X server.
    Inherits from Entity

    Methods
    -------
    init_display()
    get_screen_count()
    load_screen(screen_identifier, reload)
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
        super().__init__(id)
        self.__screens = {}
        self.__display = None
        self.init_display()
        self.load_all_screens()

    def init_display(self):
        """
        Loads the display resources(Excludes loading associated screens).
        """
        self.__display = display.Display(self._id)

    def get_screen_count(self):
        """
        Returns the number of screens associated with this display.
        """
        return self.__display.screen_count()

    def load_screen(self, screen_identifier=None, reload=False):
        """
        Loads the screen resources identified by the screen_identifier for this display.
        
        Parameters
        ----------
        screen_identifier : int, optional
            The screen ID for the screen to load (Default is None, the default screen for the display).
        reload : bool, optional
            Whether the screen should be reloaded if it exists.

        Throws
        ------
        ResourceError
            If the screen referenced by the screen_identifier argument
            does not exist.
        """
        # Throw a descriptive error if the screen number is out of range.
        screen_count = self.get_screen_count()
        if screen_identifier >= screen_count:
            raise ResourceError(
                "Invalid screen identifier. Display has only %s screen(s)"
                % screen_count
            )

        # if screen exists remove or short circuit depending on the reload param.
        if screen_identifier in self.__screens and not reload:
            return

        screen = Screen.load_from_identifier(self.__display, screen_identifier)
        self.__screens[screen_identifier] = screen

    def load_all_screens(self):
        """
        Loads all screens associated with this display.
        """
        self.__screens = {}
        screen_count = self.get_screen_count()

        for i in range(screen_count):
            self.load_screen(i)

    @property
    def Screens(self):
        """
        Returns a dcitionary of all loaded screens associated with this display.
        
        Returns
        -------
        dict
            A dictionary of Screens indexed by ids
        """
        return self.__screens

    def get_info(self):
        """
        Returns a dictionary containing all relevant information about this display's loaded resources.
        
        Returns
        -------
        DisplayDescriptor
            The descriptor of the display
        """
        return DisplayDescriptor(
            id=self._id,
            screen_count=self.get_screen_count(),
            screens=[screen.get_info() for screen in self.__screens.values()],
        )
