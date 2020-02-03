import queue
from tkinter import Frame, Scrollbar, VERTICAL, Canvas, ALL, BaseWidget
from typing import Callable, List, Optional
from SensorMonitor.Manager.configManager import ConfigManager
from SensorMonitor.Manager.colorManager import ColorManager
from SensorMonitor.Widgets.sensorItem import SensorItem, SensorValues
from SensorMonitor.Worker.fileWorker import FileWorker
from SensorMonitor.DataContainer.valueTimestampTuple import ValueTimestampTuple


class SensorList(Frame):
    """Overwrites tkinter's Frame widget in order to create a sensor list item."""

    scrollbar = None
    scroll_container = None
    item_container = None
    item_views = None

    def __init__(self,
                 parent: BaseWidget,
                 disable_callback: Callable[[int, str, bool], None],
                 select_callback: Callable[[int, str], None],
                 value_callback: Callable[[int, str, SensorValues], None],
                 list_width: float,
                 *args, **kwargs):
        """Initializes the SensorItem widget.

        :param parent: BaseWidget = the parent widget element of the list view.
        :param disable_callback: Callable[[int, str, bool], None] = will be called if the user disables/enables this widget/sensor.
        :param select_callback: Callable[[int, str], None] = will be called if the user selects/deselects this widget/sensor.
        :param value_callback: Callable[[int, str, SensorValues], None] = will be called if new values from a value worker arrived.
        :param list_width: float = the width of the widget in pixels.
        :param args: = can be ignored but are needed for internal purposes from tkinter.
        :param kwargs: = can be ignored but are needed for internal purposes from tkinter.
        """

        Frame.__init__(self, parent)
        self.currently_selected_index = -1
        self.config_mng = ConfigManager()
        self.color_mng = ColorManager()
        self.file_worker = None
        self.item_queues = None
        self.disable_callback = disable_callback
        self.select_callback = select_callback
        self.value_callback = value_callback
        self.list_width = list_width
        self.measuring = False
        self.setup_layout()

    def setup_layout(self):
        """Initializes and configures all layout components of the widget:
        - Scrollbar
        - Scroll container
        - Item container
        - List items
        """

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
            sensor_item = SensorItem(self.item_container, self.config_mng.get_sensors()[index],
                                     self.config_mng.get_window_settings().value_history_size,
                                     self._on_disable_sensor, self._on_select_sensor, self._on_value_update,
                                     index, self.list_width, is_last, self.config_mng.get_window_settings().mode)
            sensor_item.grid(row=index, sticky="w")
            self.item_views.append(sensor_item)
        self.scroll_container.create_window(0, 0, anchor="w", window=self.item_container)
        self.scroll_container.update_idletasks()
        self.currently_selected_index = self.get_first_selectable()
        self.select(self.currently_selected_index)

        self.scrollbar.config(command=self.scroll_container.yview)
        self.scroll_container.configure(scrollregion=self.scroll_container.bbox(ALL), yscrollcommand=self.scrollbar.set)

    def get_first_selectable(self) -> int:
        """Returns the index of the first list item that is not disabled. This is used to initially select the first
        possible item since always one item has to be selected.

        :return The index of the first selectable item or -1 if no item is selectable.
        """

        for i, sensor in enumerate(self.item_views):
            if sensor.is_active():
                return i
        return -1  # Nothing is selectable

    def get_sensors(self) -> List[SensorItem]:
        """Returns the list of sensor item widgets.

        :return the list of sensor items.
        """

        return self.item_views

    def get_selected_index(self) -> int:
        """Returns the index of the currently selected sensor item.
        :return the index of the currently selected sensor, or -1 if no sensor is selected.
        """

        return self.currently_selected_index

    def get_selected_item(self) -> Optional[SensorItem]:
        """Returns the currently selected sensor item.
        :return the currently selected item or 'None' if nothing is selected (all items are disabled).
        """

        if self.currently_selected_index == -1 or len(self.item_views) < self.currently_selected_index:
            return None
        else:
            return self.item_views[self.currently_selected_index]

    def is_selected(self, index: int) -> bool:
        """Returns whether the item at the given index in the list is selected or not.
        :param index: int = the index of the item to check its selection state.
        :return True if the item at the given index is selected, False otherwise.
        """

        return self.currently_selected_index == index

    def select(self, index: int):
        """Selects the item at the given list index.
        :param index: int = the index of the item to select."""

        self.item_views[self.currently_selected_index].deselect()
        self.item_views[index].select()
        self.currently_selected_index = index

    def start_measurement(self):
        """Starts measurement by starting the file worker and value workers in all active sensor items.
        If no sensor is enabled, do nothing."""

        # First setup queues for each active sensor to be able to communicate new values to write thread
        self.item_queues = {}
        for sensor in self.item_views:
            if sensor.is_active():
                self.item_queues[sensor.get_data().name] = queue.Queue()
                self.measuring = True

        # No sensor is enabled. Cannot start measurement
        if not self.measuring:
            self.stop_measurement()
            return

        # Initialize and start write thread
        self.file_worker = FileWorker(self.config_mng.get_output_settings().default_path +
                                      self.config_mng.get_output_settings().default_filename + "_",
                                      self.item_queues,
                                      self.config_mng.get_output_settings().default_file_extension,
                                      self.config_mng.get_output_settings().separator)
        self.file_worker.start()

        # Start worker threads on each active sensor that deliver values
        for sensor in self.item_views:
            if sensor.is_active():
                sensor.start_value_collection()

    def stop_measurement(self):
        """Stops measurement by stopping all running value workers and the file worker."""

        for sensor in self.item_views:
            if sensor.is_active():
                sensor.stop_value_collection()

        if self.file_worker is not None:
            self.file_worker.stop()

        self.measuring = False

    def is_measuring(self) -> bool:
        """Returns whether a measurement with minimum one sensor is currently running or not.

        :return True if a measurement is running, False otherwise.
        """

        return self.measuring

    def clear(self):
        """Clears the stored values of all sensor items."""

        for sensor in self.item_views:
            sensor.clear_values()

    def _on_disable_sensor(self, index: int, name: str):
        """Callback that gets called from a sensor item if the user clicks the disable icon.
        :param index: int = the index of the sensor that was disabled.
        :param name: str = the name of the sensor that was disabled.
        """

        if self.item_views[index].is_active():
            self.item_views[index].disable()
        else:
            self.item_views[index].enable()

        # If the disabled item was selected, find a new one to select instead.
        if self.currently_selected_index == index or self.currently_selected_index == -1:
            self.currently_selected_index = self.get_first_selectable()
            self._on_select_sensor(self.currently_selected_index, self.item_views[self.currently_selected_index].get_data().name)
        self.disable_callback(index, name, self.item_views[index].is_active())

    def _on_select_sensor(self, index: int, name: str):
        """Callback that gets called from a sensor item if the user selected it.
        :param index: int = the index of the item that was selected.
        :param name: str = the name of the item that was selected.
        """

        self.currently_selected_index = index
        if index != -1:
            self.select(index)
            self.select_callback(index, name)

    def _on_value_update(self, index: int, name: str, values: SensorValues):
        """Callback that gets called from a sensor item if new values arrived during a measurement.
        :param index: int = the index of the sensor that has new values.
        :param name: str = the name of the sensor that has new values.
        :param values: SensorValues = the new values.
        """

        self.item_queues[name].put(ValueTimestampTuple([values.current], values.timestamp))

        if index == self.currently_selected_index:
            self.value_callback(index, name, values)

    def _bound_to_mousewheel(self, event):
        """Callback that enables scrolling via mouse wheel if the user hovers the list."""

        self.scroll_container.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        """Callback that disables scrolling via mouse wheel if the user unhovers the list."""
        self.scroll_container.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        """Callback that scrolls the list if the user uses the mouse wheel while hovering the list."""
        self.scroll_container.yview_scroll(int(-1 * (event.delta / 120)), "units")
