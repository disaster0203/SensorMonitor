from tkinter import Canvas, Label, BaseWidget
from typing import List
from SensorMonitor.Manager.colorManager import ColorManager


class GraphView(Canvas):
    """Overwrites tkinter's Canvas widget in order to create a graph view with dynamic coordinate system."""

    def __init__(self, parent: BaseWidget, initial_values: List[float], max_value_count: int, color: str, coordinate_system_resolution: int,
                 canvas_width: float, canvas_height: float, *args, **kwargs):
        """Initializes the GraphView widget.

        :param parent: BaseWidget = the parent widget element of the graph view.
        :param initial_values: List[float] = if the graph view should not start with an empty graph, you can pass initial values to it.
        :param max_value_count: int = how many values can be displayed in the graph (x-axis range).
        :param color: str = the color of the graph line in hex color format (e.g. '#FF0000').
        :param coordinate_system_resolution: int = how many value labels and horizontal dotted lines should be added at the y-axis.
        :param canvas_width: float = the width (horizontal available drawing space) of the canvas.
        :param canvas_height: float = the height (vertical available drawing space) of the canvas.
        :param args: = can be ignored but are needed for internal purposes from tkinter.
        :param kwargs: = can be ignored but are needed for internal purposes from tkinter.
        """

        Canvas.__init__(self, parent)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.parent = parent
        self.colorMng = ColorManager()
        self.values = initial_values
        self.max_values = max_value_count
        self.canvas_w = canvas_width
        self.canvas_h = canvas_height
        self.check_values_list()
        self.configure(bg=self.colorMng.get_secondary_color(), highlightthickness=0, relief="ridge")

        self.color = color
        self.coordinate_system_resolution = coordinate_system_resolution
        self.x_offset = 35
        self.y_offset = 35
        self.draw()

    def check_values_list(self):
        """Checks if the current values list is too long and removes as many values from the front of the list until
        its length is inside the max_values-range."""

        if len(self.values) > self.max_values:
            first_value = len(self.values) - self.max_values
            self.values = self.values[first_value:]

    def add_value(self, value: float):
        """Adds a new value at the end of the list. If the list is too long after adding the value, it will get shortened
        via the method self.check_values_list()."""

        self.values.append(value)
        self.check_values_list()
        self.draw()

    def replace(self, new_values: List[float], new_color: str):
        """Replaces the values and color of the current graph with new ones. After the replacement the graph gets redrawn.

        :param new_values: List[float] = a new list of values that replaces the old one.
        :param new_color: str = a new color for the graph line in hex color format (e.g. '#FF0000').
        """
        self.color = new_color
        self.values = new_values
        self.check_values_list()
        self.draw()

    def clear(self):
        """Empties the current list of values and redraws the graph."""

        self.values = []
        self.check_values_list()
        self.draw()

    def draw(self):
        """First draws the coordinate system and afterwards the graph on top."""

        if len(self.values) == 0:
            return
        max_val = self._max_value()
        min_val = self._min_value()
        x_step = (self.canvas_w - 2.25 * self.x_offset) / self.max_values
        self.delete("all")
        self.draw_coordinate_system(max_val, min_val, self.canvas_w, self.canvas_h)
        self.draw_graph(max_val, min_val, x_step, self.canvas_h)

    def draw_coordinate_system(self, max_val: float, min_val: float, canvas_width: float, canvas_height: float):
        """Draws the coordinate system into the canvas.

        :param max_val: float = the maximum value from the list of values (upper border).
        :param min_val: float = the minimum value from the list of values (lower border).
        :param canvas_width: float = the width (horizontal available drawing space) of the canvas.
        :param canvas_height: float = the height (vertical available drawing space) of the canvas.
        """

        y_distance = (canvas_height - 2 * self.y_offset) / self.coordinate_system_resolution
        steps = round((max_val - min_val) / self.coordinate_system_resolution, 2)

        i = 0
        while i <= self.coordinate_system_resolution:
            y_pos = canvas_height - self.y_offset - i * y_distance
            annotation = Label(self, text=str(round(i * steps + min_val, 3)), font="Helvetica 10",
                               fg=self.colorMng.get_foreground_color(), bg=self.colorMng.get_secondary_color())
            self.create_window(5, y_pos, anchor="w", window=annotation)
            self.create_line(self.x_offset, y_pos, canvas_width - 2 * self.x_offset, y_pos, width=1, dash=(3, 3),
                             fill=self.colorMng.get_disabled_color())
            i += 1

    def draw_graph(self, max_val: float, min_val: float, x_step: float, canvas_height: float):
        """Draws the graph line into the canvas.

        :param max_val: float = the maximum value from the list of values (upper border).
        :param min_val: float = the minimum value from the list of values (lower border).
        :param x_step: float = the horizontal distance between two point coordinates in pixels.
        :param canvas_height: float = the height (vertical available drawing space) of the canvas.
        """

        index = 0
        while index < len(self.values) - 1:
            y1_val = self._transform_to_range(self.values[index], max_val, min_val,
                                              canvas_height - 2 * self.y_offset, 0)
            y1_val = canvas_height - y1_val - self.y_offset
            y2_val = self._transform_to_range(self.values[index+1], max_val, min_val,
                                              canvas_height - 2 * self.y_offset, 0)
            y2_val = canvas_height - y2_val - self.y_offset
            self.create_line(index * x_step + self.x_offset, y1_val, (index + 1) * x_step + self.x_offset, y2_val,
                             width=2, fill=self.color)
            index += 1

    def _max_value(self) -> float:
        """Returns the maximum value from the list of values.
        :return the maximum value from the list of values."""

        return max(self.values)

    def _min_value(self) -> float:
        """Returns the minimum value from the list of values.
        :return the minimum value from the list of values."""

        return min(self.values)

    @staticmethod
    def _transform_to_range(value: float, source_max: float, source_min: float, destination_max: float, destination_min: float) -> float:
        """Transforms a given value from one range to another one. For example 0 in the range [-4;4] gets 2 in the range [0; 4].

        :param value: float = the value to transform.
        :param source_max: float = the source range upper border. If source_max = source_min the transform result will simply be
                                   destination_min (to avoid divide by zero).
        :param source_min: float = the source range lower border. If source_min = source_max the transform result will simply be
                                   destination_min (to avoid divide by zero).
        :param destination_max: float = the destination range upper border. If destination_max = destination_min the transform
                                        result will simply be destination_min.
        :param destination_min: float = the destination range lower border. If destination_min = destination_max the transform
                                        result will simply be destination_min.
        :return: the transformed value.
        """

        if source_max - source_min == 0:
            return destination_min  # in this case the calculation would result in destination_min + 0 * 0 / 0
        else:
            return destination_min + (destination_max - destination_min) * (value - source_min) / (source_max - source_min)
