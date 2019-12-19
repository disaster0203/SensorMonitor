import queue
from tkinter import Frame, Canvas, Label, BaseWidget
from typing import Callable
from SensorMonitor.Manager.colorManager import ColorManager
from SensorMonitor.Worker.demoValueWorker import DemoValueWorker
from SensorMonitor.Worker.sensorValuesWorker import SensorValuesWorker
from SensorMonitor.DataContainer.sensorValues import SensorValues
from SensorMonitor.DataContainer.sensor import Sensor


class SensorItem(Frame):
    """Overwrites tkinter's Frame widget in order to create a sensor list item."""

    sensor_icon = None
    sensor_name = None
    disable_btn = None
    pin_nr = None
    pin_icon = None
    divider = None

    def __init__(self,
                 parent: BaseWidget,
                 sensor_data: Sensor,
                 history_size: int,
                 disable_callback: Callable[[int, str], None],
                 select_callback: Callable[[int, str], None],
                 value_update_callback: Callable[[int, str, SensorValues], None],
                 index: int,
                 item_width: float,
                 is_last: bool = False,
                 mode: str = "Demo",
                 *args, **kwargs):
        """Initializes the SensorItem widget.

        :param parent: BaseWidget = the parent widget element of the item view.
        :param sensor_data: Sensor = the config data of the sensor this widget represents.
        :param history_size: int = how many past values should be stored inside the widget.
        :param disable_callback: Callable[[int, str], None] = will be called if the user disables/enables this widget/sensor.
        :param select_callback: Callable[[int, str], None] = will be called if the user selects/deselects this widget/sensor.
        :param value_update_callback: Callable[[int, str, SensorValues], None] = will be called if new values from a value worker arrived.
        :param index: int = the index of this widget in the sensor list.
        :param item_width: float = the width of the widget in pixels.
        :param is_last: bool = whether this item is the last one in the sensor list (then it needs no divider line).
        :param mode: str = The mode the application runs in (Demo or Live).
        :param args: = can be ignored but are needed for internal purposes from tkinter.
        :param kwargs: = can be ignored but are needed for internal purposes from tkinter.
        """

        Frame.__init__(self, parent)
        self.grid_rowconfigure(0, weight=1)

        self.colorMng = ColorManager()
        self.data = sensor_data
        self.is_selected = False
        self.disable_callback = disable_callback
        self.select_callback = select_callback
        self.value_update_callback = value_update_callback
        self.index = index
        self.height = self.winfo_reqheight()
        self.item_width = item_width
        self.is_last = is_last
        self.mode = mode
        self.sensor_values = SensorValues(history_size)
        self.worker_queue = None
        self.worker = None
        self.setup_layout()

    def setup_layout(self):
        """Initializes and configures all layout components of the widget:
        - Sensor icon
        - Name label
        - Disable icon
        - GPIO label
        - GPIO number
        - Divider line (if not last element)
        """

        self.grid(row=0, column=0, sticky="ns")
        self.bind("<Motion>", self._hover_sensor)
        self.bind("<Leave>", self._unhover_sensor)
        self.bind("<Button-1>", self._select_sensor)
        self.bind("<Configure>", self._on_resize)
        self.configure(bg=self.colorMng.get_default_color(), width=self.item_width)

        self.sensor_icon = Canvas(self, width=30, height=30, bg=self.colorMng.get_default_color(), highlightthickness=0, relief="ridge")
        self.sensor_icon = self.colorMng.get_sensor_icon(self.data.color, self.sensor_icon, 30, 30)
        self.sensor_icon.bind("<Motion>", self._hover_sensor)
        self.sensor_icon.bind("<Leave>", self._unhover_sensor)
        self.sensor_icon.bind("<Button-1>", self._select_sensor)
        self.sensor_icon.grid(column=0, row=0, rowspan=2, sticky="w", padx=5, pady=10)

        self.sensor_name = Label(self, text=self.data.name, fg=self.colorMng.get_foreground_color(), bg=self.colorMng.get_default_color(), padx=10,
                                 font="Helvetica 11")
        self.sensor_name.bind("<Motion>", self._hover_sensor)
        self.sensor_name.bind("<Leave>", self._unhover_sensor)
        self.sensor_name.bind("<Button-1>", self._select_sensor)
        self.sensor_name.grid(column=1, row=0, rowspan=2, sticky="w")

        self.disable_btn = Canvas(self, width=20, height=20, bg=self.colorMng.get_default_color(), highlightthickness=0, relief="ridge")
        self.disable_btn = self.colorMng.get_disabled_icon(self.colorMng.get_default_signal_color(), self.disable_btn, 20, 20, 2)
        self.disable_btn.bind("<Motion>", self._hover_sensor)
        self.disable_btn.bind("<Leave>", self._unhover_sensor)
        self.disable_btn.bind("<Button-1>", self._change_sensor_state)
        if self.data.active:
            self.disable_btn = self.colorMng.get_disabled_icon(self.colorMng.get_default_signal_color(), self.disable_btn, 20, 20, 2)
        else:
            self.disable_btn = self.colorMng.get_disabled_icon(self.colorMng.get_disabled_signal_color(), self.disable_btn, 20, 20, 2)
        self.disable_btn.grid(column=2, row=0, columnspan=2, sticky="e", padx=5, pady=5)

        self.pin_nr = Label(self, text="GPIO", fg=self.colorMng.get_foreground_color(), bg=self.colorMng.get_default_color(), padx=5)
        self.pin_nr.bind("<Motion>", self._hover_sensor)
        self.pin_nr.bind("<Leave>", self._unhover_sensor)
        self.pin_nr.bind("<Button-1>", self._change_sensor_state)
        self.pin_nr.grid(column=2, row=1, sticky="e")

        self.pin_icon = Label(self, text=self.data.gpioPin, fg=self.colorMng.get_foreground_color(), bg=self.colorMng.get_default_color(), padx=5)
        self.pin_icon.bind("<Motion>", self._hover_sensor)
        self.pin_icon.bind("<Leave>", self._unhover_sensor)
        self.pin_icon.bind("<Button-1>", self._select_sensor)
        self.pin_icon.grid(column=3, row=1, sticky="e")

        if not self.is_last:  # add divider if not last item
            self.divider = Canvas(self, width=self.item_width, height=1, bg=self.colorMng.get_foreground_color(),
                                  highlightthickness=0, relief="ridge")
            self.divider.grid(column=0, row=1, columnspan=4, sticky="s")

        if self.is_active():
            self.enable()
        else:
            self.disable()

    def get_data(self) -> Sensor:
        """Returns the config data object that this list item represents.

        :return: the config data of the sensor this item represents.
        """

        return self.data

    def get_values(self) -> SensorValues:
        """Returns the object that stores the sensor values of this item.

        :return: the sensor values of this sensor item.
        """

        return self.sensor_values

    def clear_values(self):
        """Resets all sensor values that are currently stored inside the widget back to their default values."""

        self.sensor_values.clear_values()

    def is_active(self) -> bool:
        """Returns whether the sensor this item represents is disabled or not.

        :return: True if the sensor is enabled, False otherwise.
        """

        return self.data.active

    def is_selected(self):
        """Returns whether the sensor this item represents is selected or not.

        :return: True if the sensor is selected, False otherwise.
        """

        return self.is_selected

    def _change_sensor_state(self, event):
        """Function that gets executed if the user clicks the disable icon. This method will call the disable_callback."""

        self.disable_callback(self.index, self.data.name)

    def _select_sensor(self, event):
        """Function that gets executed if the user clicks somewhere in the list item. This method will call the select_callback."""

        if self.data.active:
            self.select_callback(self.index, self.data.name)

    def start_value_collection(self):
        """Starts the value worker thread and listens to values from it via a queue."""

        self.worker_queue = queue.Queue()
        if self.mode == "Demo":
            self.worker = DemoValueWorker(self.data.gpioPin, self.worker_queue)
            self.worker.start()
            self.after(100, self._on_new_value)
        elif self.mode == "Live":
            self.worker = SensorValuesWorker(self.data.gpioPin, self.worker_queue)
            self.worker.start()
            self.after(100, self._on_new_value)

    def stop_value_collection(self):
        """Stops the value worker thread."""

        self.worker.stop()
        self.worker_queue = None
        self.worker = None

    def is_measuring(self):
        """Returns whether this item is currently measuring or not.

        :return: True if the sensor is measuring, False otherwise.
        """

        return self.worker.is_running()

    def select(self):
        """Selects the list item. This method changes the appearance of the item to selected state
        depending on the current theme."""

        if self.data.active:
            self.is_selected = True
            self.configure(bg=self.colorMng.get_selected_color())
            self.sensor_icon.configure(bg=self.colorMng.get_selected_color())
            self.sensor_name.configure(bg=self.colorMng.get_selected_color())
            self.disable_btn.configure(bg=self.colorMng.get_selected_color())
            self.pin_nr.configure(bg=self.colorMng.get_selected_color())
            self.pin_icon.configure(bg=self.colorMng.get_selected_color())
            return True
        return False

    def deselect(self):
        """Deselects the list item. This method changes the appearance back to default."""

        if self.data.active:
            self.is_selected = False
            self.configure(bg=self.colorMng.get_default_color())
            self.sensor_icon.configure(bg=self.colorMng.get_default_color())
            self.sensor_name.configure(bg=self.colorMng.get_default_color())
            self.disable_btn.configure(bg=self.colorMng.get_default_color())
            self.pin_nr.configure(bg=self.colorMng.get_default_color())
            self.pin_icon.configure(bg=self.colorMng.get_default_color())
            return True
        return False

    def disable(self):
        """Function that gets executed if the user disables the list item by clicking the disable icon. This method
        changes the appearance of the item to disabled state depending on the current theme."""

        if self.worker is not None and self.worker.is_running():
            return  # do not allow disabling sensors if measurement is currently in progress

        self.data.active = False
        self.disable_btn.delete("all")
        self.disable_btn = self.colorMng.get_disabled_icon(self.colorMng.get_disabled_signal_color(), self.disable_btn,
                                                           20, 20, 2)
        self.configure(bg=self.colorMng.get_disabled_color())
        self.sensor_icon.configure(bg=self.colorMng.get_disabled_color())
        self.sensor_name.configure(bg=self.colorMng.get_disabled_color())
        self.disable_btn.configure(bg=self.colorMng.get_disabled_color())
        self.pin_nr.configure(bg=self.colorMng.get_disabled_color())
        self.pin_icon.configure(bg=self.colorMng.get_disabled_color())

    def enable(self):
        """Function that gets executed if the user enables the list item by clicking the disable icon. This method
        changes the appearance back to default."""

        if self.worker is not None and self.worker.is_running():
            return  # do not allow enabling sensors if measurement is currently in progress

        self.data.active = True
        self.disable_btn.delete("all")
        self.disable_btn = self.colorMng.get_disabled_icon(self.colorMng.get_default_signal_color(), self.disable_btn,
                                                           20, 20, 2)
        self.configure(bg=self.colorMng.get_default_color())
        self.sensor_icon.configure(bg=self.colorMng.get_default_color())
        self.sensor_name.configure(bg=self.colorMng.get_default_color())
        self.disable_btn.configure(bg=self.colorMng.get_default_color())
        self.pin_nr.configure(bg=self.colorMng.get_default_color())
        self.pin_icon.configure(bg=self.colorMng.get_default_color())

    def _hover_sensor(self, event):
        """Function that gets executed if the user hovers with the mouse somewhere over the list item. This method
        changes the appearance of the item to hover state depending on the current theme."""

        if self.data.active:
            if self.is_selected:
                self.configure(bg=self.colorMng.get_hover_selected_color())
                self.sensor_icon.configure(bg=self.colorMng.get_hover_selected_color())
                self.sensor_name.configure(bg=self.colorMng.get_hover_selected_color())
                self.disable_btn.configure(bg=self.colorMng.get_hover_selected_color())
                self.pin_nr.configure(bg=self.colorMng.get_hover_selected_color())
                self.pin_icon.configure(bg=self.colorMng.get_hover_selected_color())
            else:
                self.configure(bg=self.colorMng.get_hover_color())
                self.sensor_icon.configure(bg=self.colorMng.get_hover_color())
                self.sensor_name.configure(bg=self.colorMng.get_hover_color())
                self.disable_btn.configure(bg=self.colorMng.get_hover_color())
                self.pin_nr.configure(bg=self.colorMng.get_hover_color())
                self.pin_icon.configure(bg=self.colorMng.get_hover_color())

    def _unhover_sensor(self, event):
        """Function that gets executed if the user leaves the list item after hovering. This method changes the appearance
        back to default."""

        if self.is_selected:
            self.configure(bg=self.colorMng.get_selected_color())
            self.sensor_icon.configure(bg=self.colorMng.get_selected_color())
            self.sensor_name.configure(bg=self.colorMng.get_selected_color())
            self.disable_btn.configure(bg=self.colorMng.get_selected_color())
            self.pin_nr.configure(bg=self.colorMng.get_selected_color())
            self.pin_icon.configure(bg=self.colorMng.get_selected_color())
        else:
            self.configure(bg=self.colorMng.get_default_color())
            self.sensor_icon.configure(bg=self.colorMng.get_default_color())
            self.sensor_name.configure(bg=self.colorMng.get_default_color())
            self.disable_btn.configure(bg=self.colorMng.get_default_color())
            self.pin_nr.configure(bg=self.colorMng.get_default_color())
            self.pin_icon.configure(bg=self.colorMng.get_default_color())

    def _on_new_value(self):
        """Function that listens to new values from the value worker and sends them to SensorValues.
        It also calls the value_update_callback function to notify its parent widget."""

        try:
            if self.worker_queue is not None:
                new_values = self.worker_queue.get(0)
                if new_values is None:
                    # Measuring stopped
                    return
            else:
                return
        except queue.Empty:
            self.after(100, self._on_new_value)
            return

        # Apply calibration offset
        new_values.value = new_values.value + self.data.offset

        self.sensor_values.add_new_value(new_values.value, new_values.timestamp)
        self.value_update_callback(self.index, self.data.name, self.sensor_values)
        self.after(100, self._on_new_value)

    def _on_resize(self, event):
        """Function that gets called if the size of the item changes."""

        self.width = event.width
        self.height = event.height
        self.config(width=self.width, height=self.height)
