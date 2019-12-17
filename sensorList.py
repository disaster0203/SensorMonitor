from tkinter import *
import queue
import SensorMonitor.configManager as conf
import SensorMonitor.colorManager as col
import SensorMonitor.sensorItem as item
import SensorMonitor.fileWorker as fileWorker
from SensorMonitor.valueTimestampTuple import ValueTimestampTuple


class SensorList(Frame):
    def __init__(self, parent, disable_callback, select_callback, value_callback, list_width, *args, **kwargs):
        Frame.__init__(self, parent)
        self.currently_selected_index = -1
        self.config_mng = conf.ConfigManager()
        self.color_mng = col.ColorManager()
        self.file_worker = None
        self.item_queues = None
        self.disable_callback = disable_callback
        self.select_callback = select_callback
        self.value_callback = value_callback
        self.list_width = list_width
        self.is_measuring = False

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.configure(bg=self.color_mng.get_default_color(), width=self.list_width)

        self.scrollbar = Scrollbar(self, orient=VERTICAL)
        self.scrollbar.grid(column=0, row=0, sticky="nse")

        self.scroll_container = Canvas(self, relief="ridge", highlightthickness=0, bg=self.color_mng.get_default_color())
        self.scroll_container.grid(column=0, row=0, sticky="nsw")

        self.item_container = Frame(self.scroll_container)
        self.item_container.bind('<Enter>', self._bound_to_mousewheel)
        self.item_container.bind('<Leave>', self._unbound_to_mousewheel)

        self.item_views = []
        for index, sensor in enumerate(self.config_mng.get_sensors()):
            is_last = index == len(self.config_mng.get_sensors()) - 1
            sensor_item = item.SensorItem(self.item_container, self.config_mng.get_sensors()[index],
                                          self.config_mng.get_window_settings().value_history_size,
                                          self._on_disable_sensor, self._on_select_sensor, self._on_value_update, index, self.list_width, is_last)
            sensor_item.grid(row=index, sticky="w")
            self.item_views.append(sensor_item)
        self.scroll_container.create_window(0, 0, anchor="w", window=self.item_container)
        self.scroll_container.update_idletasks()

        self.scrollbar.config(command=self.scroll_container.yview)
        self.scroll_container.configure(scrollregion=self.scroll_container.bbox(ALL), yscrollcommand=self.scrollbar.set)

    def get_first_selectable(self):
        for i, sensor in enumerate(self.item_views):
            if sensor.is_active():
                return i
        return -1  # Nothing is selectable

    def get_sensors(self):
        return self.item_views

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

    def start_measurement(self):
        # First setup queues for each active sensor to be able to communicate new values to write thread
        self.item_queues = {}
        for sensor in self.item_views:
            if sensor.is_active():
                self.item_queues[sensor.get_data().name] = queue.Queue()

        # Initialize and start write thread
        self.file_worker = fileWorker.FileWorker(self.config_mng.get_output_settings().defaultPath +
                                                 self.config_mng.get_output_settings().defaultFilename + "_",
                                                 self.item_queues,
                                                 self.config_mng.get_output_settings().defaultFileExtension,
                                                 self.config_mng.get_output_settings().separator)
        self.file_worker.start()

        # Start worker threads on each active sensor that deliver values
        for sensor in self.item_views:
            if sensor.is_active():
                sensor.start_value_collection()

        self.is_measuring = True

    def stop_measurement(self):
        for sensor in self.item_views:
            if sensor.is_active():
                sensor.stop_value_collection()
        self.file_worker.stop()
        self.is_measuring = False

    def measuring(self):
        return self.is_measuring

    def clear(self):
        for sensor in self.item_views:
            sensor.clear_values()

    def _on_disable_sensor(self, index, name):
        if self.item_views[index].is_active():
            self.item_views[index].disable()
        else:
            self.item_views[index].enable()
        self.disable_callback(index, name, self.item_views[index].is_active())

    def _on_select_sensor(self, index, name):
        self.select(index)
        self.select_callback(self.currently_selected_index, name)

    def _on_value_update(self, index, name, values):
        self.item_queues[name].put(ValueTimestampTuple(values.current, values.timestamp))

        if index == self.currently_selected_index:
            self.value_callback(index, name, values)

    def _bound_to_mousewheel(self, event):
        self.scroll_container.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.scroll_container.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.scroll_container.yview_scroll(int(-1 * (event.delta / 120)), "units")
