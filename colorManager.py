import tkinter as tk
import colors_darkTheme as dark
import colors_lightTheme as light
from PIL import ImageTk, Image


class ColorManager:
    __instance = None
    theme = ""

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(ColorManager, cls).__new__(cls, *args, **kwargs)
        return cls.__instance

    def set_theme(self, theme):
        if theme == "dark" or theme == "light":
            self.theme = theme

    def get_default_color(self):
        if self.theme != "":
            if self.theme == "dark":
                return dark.default_color
            elif self.theme == "light":
                return light.default_color
        return "#000000"

    def get_secondary_color(self):
        if self.theme != "":
            if self.theme == "dark":
                return dark.secondary_color
            elif self.theme == "light":
                return light.secondary_color
        return "#000000"

    def get_hover_color(self):
        if self.theme != "":
            if self.theme == "dark":
                return dark.hover_color
            elif self.theme == "light":
                return light.hover_color
        return "#000000"

    def get_hover_selected_color(self):
        if self.theme != "":
            if self.theme == "dark":
                return dark.hover_selected_color
            elif self.theme == "light":
                return light.hover_selected_color
        return "#000000"

    def get_disabled_color(self):
        if self.theme != "":
            if self.theme == "dark":
                return dark.disabled_color
            elif self.theme == "light":
                return light.disabled_color
        return "#000000"

    def get_selected_color(self):
        if self.theme != "":
            if self.theme == "dark":
                return dark.selected_color
            elif self.theme == "light":
                return light.selected_color
        return "#000000"

    def get_foreground_color(self):
        if self.theme != "":
            if self.theme == "dark":
                return dark.foreground_color
            elif self.theme == "light":
                return light.foreground_color
        return "#000000"

    def get_default_signal_color(self):
        if self.theme != "":
            if self.theme == "dark":
                return dark.default_signal_color
            elif self.theme == "light":
                return light.default_signal_color
        return "#000000"

    def get_disabled_signal_color(self):
        if self.theme != "":
            if self.theme == "dark":
                return dark.disabled_signal_color
            elif self.theme == "light":
                return light.disabled_signal_color
        return "#000000"

    def get_disabled_icon(self, color, canvas, canvas_w, canvas_h, line_width):
        canvas.create_oval(line_width * 0.5, line_width * 0.5,
                           canvas_w - line_width * 0.5, canvas_h - line_width * 0.5,
                           fill="", outline=color, width=line_width)
        canvas.create_line(canvas_w * 0.15, canvas_h * 0.85,
                           canvas_w * 0.85, canvas_h * 0.15,
                           width=line_width, fill=color)
        return canvas

    def get_play_icon(self, color, canvas, canvas_w, canvas_h):
        canvas.create_polygon(canvas_w * 0.1, 0,
                              canvas_w * 0.9, canvas_h * 0.5,
                              canvas_w * 0.1, canvas_h,
                              fill=color, outline="")
        return canvas

    def get_stop_icon(self, color, canvas, canvas_w, canvas_h):
        canvas.create_rectangle(canvas_w * 0.1, canvas_h * 0.1,
                                canvas_w * 0.9, canvas_h * 0.9,
                                fill=color, outline="")
        return canvas

    def get_folder_icon(self, color, canvas, canvas_w, canvas_h):
        canvas.create_polygon(0, canvas_h * 0.1,
                              canvas_w * 0.3, canvas_h * 0.1,
                              canvas_w * 0.45, canvas_h * 0.25,
                              canvas_w, canvas_h * 0.25,
                              canvas_w, canvas_h * 0.9,
                              0, canvas_h * 0.9,
                              fill=color, outline="")
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

    def get_sensor_icon(self, color, canvas, canvas_w, canvas_h):
        canvas.create_line(0, canvas_h / 2,
                           canvas_w * 0.1, canvas_h * 0.5,
                           canvas_w * 0.2, 0,
                           canvas_w * 0.3, canvas_h * 0.75,
                           canvas_w * 0.4, 0,
                           canvas_w * 0.5, canvas_h * 0.5,
                           canvas_w * 0.6, canvas_h * 0.5,
                           width=1.5, fill=color)
        canvas.create_oval(canvas_w * 0.55, canvas_h * 0.45,
                           canvas_w * 0.65, canvas_h * 0.55,
                           fill=color, outline="")
        canvas.create_arc(canvas_w * 0.5, canvas_h * 0.33,
                          canvas_w * 0.8, canvas_h * 0.66,
                          start=300, extent=120,
                          style='arc', width=1.5, outline=color)
        canvas.create_arc(canvas_w * 0.3, canvas_h * 0.2,
                          canvas_w * 0.9, canvas_h * 0.8,
                          start=300, extent=120,
                          style='arc', width=1.5, outline=color)
        return canvas
