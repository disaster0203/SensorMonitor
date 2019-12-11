from tkinter import *
import colorManager as col
import sensorItem as item


class SensorList(Frame):
    def __init__(self, parent, sensors, disable_callback, select_callback, list_width, *args, **kwargs):
        Frame.__init__(self, parent)
        self.currently_selected_index = -1
        self.colorMng = col.ColorManager()
        self.disable_callback = disable_callback
        self.select_callback = select_callback
        self.list_width = list_width

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.configure(bg=self.colorMng.get_default_color(), width=self.list_width)

        self.scrollbar = Scrollbar(self, orient=VERTICAL)
        self.scrollbar.grid(column=0, row=0, sticky="nse")

        self.scroll_container = Canvas(self, relief="ridge", highlightthickness=0, bg=self.colorMng.get_default_color())
        self.scroll_container.grid(column=0, row=0, sticky="nsw")

        self.item_container = Frame(self.scroll_container)
        self.item_container.bind('<Enter>', self._bound_to_mousewheel)
        self.item_container.bind('<Leave>', self._unbound_to_mousewheel)

        self.item_views = []
        for index, sensor in enumerate(sensors):
            is_last = index == len(sensors) - 1
            sensor_item = item.SensorItem(self.item_container, sensor, self._on_disable_sensor, self._on_select_sensor,
                                          index, self.list_width, is_last)
            sensor_item.grid(row=index, sticky="w")
            self.item_views.append(sensor_item)
        self.scroll_container.create_window(0, 0, anchor="w", window=self.item_container)
        self.scroll_container.update_idletasks()

        self.scrollbar.config(command=self.scroll_container.yview)
        self.scroll_container.configure(scrollregion=self.scroll_container.bbox(ALL), yscrollcommand=self.scrollbar.set)

    def get_first_selectable(self):
        for i, item in enumerate(self.item_views):
            if item.is_active():
                return i
        return -1  # Nothing is selectable

    def get_selected_index(self):
        return self.currently_selected_index

    def get_selected_item(self):
        return self.item_views[self.currently_selected_index]

    def is_selected(self, index):
        return self.currently_selected_index == index

    def select(self, index):
        if index == self.currently_selected_index:
            return
        else:
            self.item_views[self.currently_selected_index].deselect()
            self.item_views[index].select()
            self.currently_selected_index = index

    def _on_disable_sensor(self, index, name):
        if self.item_views[index].is_active():
            self.item_views[index].disable()
        else:
            self.item_views[index].enable()
        self.disable_callback(index, name, self.item_views[index].is_active())

    def _on_select_sensor(self, index, name):
        self.select(index)
        self.select_callback(self.currently_selected_index, name, self.item_views[self.currently_selected_index].is_selected())

    def _bound_to_mousewheel(self, event):
        self.scroll_container.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.scroll_container.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.scroll_container.yview_scroll(int(-1 * (event.delta / 120)), "units")
