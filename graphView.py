from tkinter import *
import colorManager as col


class GraphView(Canvas):
    def __init__(self, parent, initial_values, max_value_count, color, coordinate_system_resolution,
                 canvas_width, canvas_height, *args, **kwargs):
        Canvas.__init__(self, parent)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.parent = parent
        self.colorMng = col.ColorManager()
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
        if len(self.values) > self.max_values:
            first_value = len(self.values) - self.max_values
            self.values = self.values[first_value:]

    def add_value(self, value):
        self.values.append(value)
        self.check_values_list()
        self.draw()

    def replace(self, new_values, new_color):
        self.color = new_color
        self.values = new_values
        self.check_values_list()
        self.draw()

    def draw(self):
        if len(self.values) == 0:
            return
        max_val = self._max_value()
        min_val = self._min_value()
        x_step = (self.canvas_w - 2.25 * self.x_offset) / self.max_values
        self.delete("all")
        self.draw_coordinate_system(max_val, min_val, self.canvas_w, self.canvas_h)
        self.draw_graph(max_val, min_val, x_step, self.canvas_h)

    def draw_coordinate_system(self, max_val, min_val, canvas_width, canvas_height):
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

    def draw_graph(self, max_val, min_val, x_step, canvas_height):
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

    def _max_value(self):
        return max(self.values)

    def _min_value(self):
        return min(self.values)

    @staticmethod
    def _transform_to_range(value, source_max, source_min, destination_max, destination_min):
        if source_max - source_min == 0:
            return destination_min  # in this case the calculation would result in destination_min + 0 * 0 / 0
        else:
            return destination_min + (destination_max - destination_min) * (value - source_min) / (source_max - source_min)
