import SensorMonitor.Themes.colors_darkTheme as Dark
import SensorMonitor.Themes.colors_lightTheme as Light
import tkinter as tk


class ColorManager:
    """ Manages colors and icons that are used in the gui depending on the currently used theme. At the
        moment two themes are implemented (light and dark).

        This class uses the singleton pattern which means that while the application runs only one instance
        of this class can exist at the same time. At each position the class is used always the same instance
        is manipulated.
        """

    __instance = None
    theme = "Dark"

    def __new__(cls, *args, **kwargs):
        """Singleton pattern: Checks if the class is already initialized. If not it is initialized and
        stored in the private internal variable __instance. Do not manipulate __instance from outside!"""

        if not cls.__instance:
            cls.__instance = super(ColorManager, cls).__new__(cls, *args, **kwargs)
        return cls.__instance

    def set_theme(self, theme: str):
        """Sets the theme to use. By default 'Dark' is used."""

        if theme == "Dark" or theme == "Light":
            self.theme = theme

    def get_default_color(self) -> str:
        """Returns the default UI color. This color is used for the background of the application.

        :return The default UI color or black if no valid theme is set.
        """

        if self.theme != "":
            if self.theme == "Dark":
                return Dark.default_color
            elif self.theme == "Light":
                return Light.default_color
        return "#000000"

    def get_secondary_color(self) -> str:
        """Returns the secondary UI color. This color is used for background parts of the application
        that should get some separation from the default background color.

        :return The secondary UI color or black if no valid theme is set.
        """

        if self.theme != "":
            if self.theme == "Dark":
                return Dark.secondary_color
            elif self.theme == "Light":
                return Light.secondary_color
        return "#000000"

    def get_hover_color(self) -> str:
        """Returns the hover UI color. This color is used for background parts of the application
        that can be hover by the user.

        :return The hover UI color or black if no valid theme is set.
        """

        if self.theme != "":
            if self.theme == "Dark":
                return Dark.hover_color
            elif self.theme == "Light":
                return Light.hover_color
        return "#000000"

    def get_hover_selected_color(self) -> str:
        """Returns the hover selected UI color. This color is used for background parts of the
        application that are selected (list items) and can be hover by the user.

        :return The hover selected UI color or black if no valid theme is set.
        """

        if self.theme != "":
            if self.theme == "Dark":
                return Dark.hover_selected_color
            elif self.theme == "Light":
                return Light.hover_selected_color
        return "#000000"

    def get_disabled_color(self) -> str:
        """Returns the disabled UI color. This color is used for background parts of the application
        that can be disabled.

        :return The disabled UI color or black if no valid theme is set.
        """

        if self.theme != "":
            if self.theme == "Dark":
                return Dark.disabled_color
            elif self.theme == "Light":
                return Light.disabled_color
        return "#000000"

    def get_selected_color(self) -> str:
        """Returns the selected UI color. This color is used for background parts of the application
        that can be selected by the user.

        :return The selected UI color or black if no valid theme is set.
        """

        if self.theme != "":
            if self.theme == "Dark":
                return Dark.selected_color
            elif self.theme == "Light":
                return Light.selected_color
        return "#000000"

    def get_foreground_color(self) -> str:
        """Returns the foreground UI color. This color is used for icons and texts in the application.

        :return The foreground UI color or black if no valid theme is set.
        """

        if self.theme != "":
            if self.theme == "Dark":
                return Dark.foreground_color
            elif self.theme == "Light":
                return Light.foreground_color
        return "#000000"

    def get_default_signal_color(self) -> str:
        """Returns the signal UI color. This color is used for icons of the application that should
        attract the users attention.

        :return The signal UI color or black if no valid theme is set.
        """

        if self.theme != "":
            if self.theme == "Dark":
                return Dark.default_signal_color
            elif self.theme == "Light":
                return Light.default_signal_color
        return "#000000"

    def get_disabled_signal_color(self) -> str:
        """Returns the disabled signal UI color. This color is used for icons of the application that
        should attract the users attention but are currently disabled.

        :return The disabled signal UI color or black if no valid theme is set.
        """

        if self.theme != "":
            if self.theme == "Dark":
                return Dark.disabled_signal_color
            elif self.theme == "Light":
                return Light.disabled_signal_color
        return "#000000"

    @staticmethod
    def get_disabled_icon(color: str, canvas: tk.Canvas, canvas_w: float, canvas_h: float, line_width: int) -> tk.Canvas:
        """Takes a canvas object and draws the disable icon in it.

        :param color: str = the icons color in hex format (e.g. '#FF000').
        :param canvas: tk.Canvas = the canvas to draw the icon into.
        :param canvas_w: float = the width (horizontal available drawing space) of the canvas.
        :param canvas_h: float = the height (vertical available drawing space) of the canvas.
        :param line_width: int = the line thickness of the icon in pixels.

        :return the input canvas with the disabled icon in it.
        """

        # Draw the circle
        canvas.create_oval(line_width * 0.5, line_width * 0.5,
                           canvas_w - line_width * 0.5, canvas_h - line_width * 0.5,
                           fill="", outline=color, width=line_width)

        # Draw the diagonal line from left bottom to right top
        canvas.create_line(canvas_w * 0.15, canvas_h * 0.85,
                           canvas_w * 0.85, canvas_h * 0.15,
                           width=line_width, fill=color)
        return canvas

    @staticmethod
    def get_play_icon(color: str, canvas: tk.Canvas, canvas_w: float, canvas_h: float) -> tk.Canvas:
        """Takes a canvas object and draws the play icon in it.

        :param color: str = the icons color in hex format (e.g. '#FF000').
        :param canvas: tk.Canvas = the canvas to draw the icon into.
        :param canvas_w: float = the width (horizontal available drawing space) of the canvas.
        :param canvas_h: float = the height (vertical available drawing space) of the canvas.

        :return the input canvas with the play icon in it.
        """

        # Draw a triangle / arrow that points to the right
        canvas.create_polygon(canvas_w * 0.1, 0,
                              canvas_w * 0.9, canvas_h * 0.5,
                              canvas_w * 0.1, canvas_h,
                              fill=color, outline="")
        return canvas

    @staticmethod
    def get_stop_icon(color: str, canvas: tk.Canvas, canvas_w: float, canvas_h: float) -> tk.Canvas:
        """Takes a canvas object and draws the stop icon in it.

        :param color: str = the icons color in hex format (e.g. '#FF000').
        :param canvas: tk.Canvas = the canvas to draw the icon into.
        :param canvas_w: float = the width (horizontal available drawing space) of the canvas.
        :param canvas_h: float = the height (vertical available drawing space) of the canvas.

        :return the input canvas with the stop icon in it.
        """

        # Draw a simple square.
        canvas.create_rectangle(canvas_w * 0.1, canvas_h * 0.1,
                                canvas_w * 0.9, canvas_h * 0.9,
                                fill=color, outline="")
        return canvas

    def get_folder_icon(self, color: str, canvas: tk.Canvas, canvas_w: float, canvas_h: float) -> tk.Canvas:
        """Takes a canvas object and draws the folder icon in it.

        :param color: str = the icons color in hex format (e.g. '#FF000').
        :param canvas: tk.Canvas = the canvas to draw the icon into.
        :param canvas_w: float = the width (horizontal available drawing space) of the canvas.
        :param canvas_h: float = the height (vertical available drawing space) of the canvas.

        :return the input canvas with the folder icon in it.
        """

        # Draw the folder (rectangle with an extra area in the top left corner)
        canvas.create_polygon(0, canvas_h * 0.1,
                              canvas_w * 0.3, canvas_h * 0.1,
                              canvas_w * 0.45, canvas_h * 0.25,
                              canvas_w, canvas_h * 0.25,
                              canvas_w, canvas_h * 0.9,
                              0, canvas_h * 0.9,
                              fill=color, outline="")

        # Draw three ovals at the lower part of the folder icon. This will represent the
        # three dots ('...') iconography.
        canvas.create_oval(canvas_w * 0.2, canvas_h * 0.6,
                           canvas_w * 0.35, canvas_h * 0.75,
                           fill=self.get_default_color(), outline="")
        canvas.create_oval(canvas_w * 0.45, canvas_h * 0.6,
                           canvas_w * 0.6, canvas_h * 0.75,
                           fill=self.get_default_color(), outline="")
        canvas.create_oval(canvas_w * 0.7, canvas_h * 0.6,
                           canvas_w * 0.85, canvas_h * 0.75,
                           fill=self.get_default_color(), outline="")
        return canvas

    @staticmethod
    def get_sensor_icon(color: str, canvas: tk.Canvas, canvas_w: float, canvas_h: float) -> tk.Canvas:
        """Takes a canvas object and draws the sensor icon in it.

        :param color: str = the icons color in hex format (e.g. '#FF000').
        :param canvas: tk.Canvas = the canvas to draw the icon into.
        :param canvas_w: float = the width (horizontal available drawing space) of the canvas.
        :param canvas_h: float = the height (vertical available drawing space) of the canvas.

        :return the input canvas with the sensor icon in it.
        """

        # Draw the folder (rectangle with an extra area in the top left corner)

        # Draw the zigzag line on the left.
        canvas.create_line(0, canvas_h / 2,
                           canvas_w * 0.1, canvas_h * 0.5,
                           canvas_w * 0.2, 0,
                           canvas_w * 0.3, canvas_h * 0.75,
                           canvas_w * 0.4, 0,
                           canvas_w * 0.5, canvas_h * 0.5,
                           canvas_w * 0.6, canvas_h * 0.5,
                           width=1.5, fill=color)

        # Draw the dot at the end of the zigzag line in the middle of the canvas.
        canvas.create_oval(canvas_w * 0.55, canvas_h * 0.45,
                           canvas_w * 0.65, canvas_h * 0.55,
                           fill=color, outline="")

        # Draw the small arc on the right.
        canvas.create_arc(canvas_w * 0.5, canvas_h * 0.33,
                          canvas_w * 0.8, canvas_h * 0.66,
                          start=300, extent=120,
                          style='arc', width=1.5, outline=color)

        # Draw the big arc on the right.
        canvas.create_arc(canvas_w * 0.3, canvas_h * 0.2,
                          canvas_w * 0.9, canvas_h * 0.8,
                          start=300, extent=120,
                          style='arc', width=1.5, outline=color)
        return canvas
