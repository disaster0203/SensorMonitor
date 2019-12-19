class WindowSettings:
    """Container class for window settings.

    The following settings are provided:
    :param width: int = the width of the application window in pixels
    :param height: int = the height of the application window in pixels
    :param value_history_size: int = how many values can be displayed in the graph view at the same time.
                                     This also affects how many values are stored inside a sensor class.
    :param color_theme: str = the color theme to use in the GUI. Supported values are 'Dark' and 'Light'.
    :param mode: str = The mode the application runs in (Demo or Live).
    """

    def __init__(self, width: int, height: int, value_history_size: int, color_theme: str, mode: str):
        """Initializes this class and stores the given values in their corresponding fields.

        :param width: int = the width of the application window in pixels
        :param height: int = the height of the application window in pixels
        :param value_history_size: int = how many values can be displayed in the graph view at the same time.
                                         This also affects how many values are stored inside a sensor class.
        :param color_theme: str = the color theme to use in the GUI. Supported values are 'Dark' and 'Light'.
        :param mode: str = The mode the application runs in (Demo or Live).
        """

        self.width = width
        self.height = height
        self.value_history_size = value_history_size
        self.color_theme = color_theme
        self.mode = mode
