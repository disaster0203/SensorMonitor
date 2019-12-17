from tkinter import *
import queue
import SensorMonitor.colorManager as col
from SensorMonitor.demoValueWorker import DemoValueWorker, ValueTimestampTuple


class SensorValues:
    def __init__(self, history_size=100):
        self.last_values = []
        self.current = 0
        self.max = -sys.maxsize - 1
        self.min = sys.maxsize
        self.avg = 0
        self.sum = 0
        self.value_count = 0
        self.timestamp = ""
        self._history_size = history_size

    def add_new_value(self, new_value, timestamp):
        self.current = new_value
        self.last_values.append(new_value)
        self.max = max(self.max, new_value)
        self.min = min(self.min, new_value)
        self.sum = self.sum + new_value
        self.value_count = self.value_count + 1
        self.avg = self.sum / self.value_count
        self.timestamp = timestamp
        # If the list is too long, create a sublist by removing elements from the start
        if len(self.last_values) > self._history_size:
            self.last_values = self.last_values[len(self.last_values) - self._history_size:]

    def clear_values(self):
        self.last_values = []
        self.current = 0
        self.max = -sys.maxsize - 1
        self.min = sys.maxsize
        self.avg = 0
        self.sum = 0
        self.value_count = 0
        self.timestamp = ""

class SensorItem(Frame):
    def __init__(self, parent, sensor_data, history_size, disable_callback, select_callback, value_update_callback, index, item_width,
                 is_last=False, *args, **kwargs):
        Frame.__init__(self, parent)
        self.grid_rowconfigure(0, weight=1)

        self.colorMng = col.ColorManager()
        self.data = sensor_data
        self._is_selected = False
        self.disable_callback = disable_callback
        self.select_callback = select_callback
        self.value_update_callback = value_update_callback
        self.index = index
        self.height = self.winfo_reqheight()
        self.item_width = item_width
        self.is_last = is_last
        self.sensor_values = SensorValues(history_size)
        self.worker_queue = None
        self.worker = None
        self.setup_layout()

    def setup_layout(self):
        self.grid(row=0, column=0, sticky="ns")
        self.bind("<Motion>", self.hover_sensor)
        self.bind("<Leave>", self.unhover_sensor)
        self.bind("<Button-1>", self.select_sensor)
        self.bind("<Configure>", self.__on_resize)
        self.configure(bg=self.colorMng.get_default_color(), width=self.item_width)

        self.sensor_icon = Canvas(self, width=30, height=30, bg=self.colorMng.get_default_color(), highlightthickness=0, relief="ridge")
        self.sensor_icon = self.colorMng.get_sensor_icon(self.data.color, self.sensor_icon, 30, 30)
        self.sensor_icon.bind("<Motion>", self.hover_sensor)
        self.sensor_icon.bind("<Leave>", self.unhover_sensor)
        self.sensor_icon.bind("<Button-1>", self.select_sensor)
        self.sensor_icon.grid(column=0, row=0, rowspan=2, sticky="w", padx=5, pady=10)

        self.sensor_name = Label(self, text=self.data.name, fg=self.colorMng.get_foreground_color(), bg=self.colorMng.get_default_color(), padx=10,
                                 font="Helvetica 11")
        self.sensor_name.bind("<Motion>", self.hover_sensor)
        self.sensor_name.bind("<Leave>", self.unhover_sensor)
        self.sensor_name.bind("<Button-1>", self.select_sensor)
        self.sensor_name.grid(column=1, row=0, rowspan=2, sticky="w")

        self.disable_btn = Canvas(self, width=20, height=20, bg=self.colorMng.get_default_color(), highlightthickness=0, relief="ridge")
        self.disable_btn = self.colorMng.get_disabled_icon(self.colorMng.get_default_signal_color(), self.disable_btn, 20, 20, 2)
        self.disable_btn.bind("<Motion>", self.hover_sensor)
        self.disable_btn.bind("<Leave>", self.unhover_sensor)
        self.disable_btn.bind("<Button-1>", self.change_sensor_state)
        if self.data.active:
            self.disable_btn = self.colorMng.get_disabled_icon(self.colorMng.get_default_signal_color(), self.disable_btn, 20, 20, 2)
        else:
            self.disable_btn = self.colorMng.get_disabled_icon(self.colorMng.get_disabled_signal_color(), self.disable_btn, 20, 20, 2)
        self.disable_btn.grid(column=2, row=0, columnspan=2, sticky="e", padx=5, pady=5)

        self.pin_nr = Label(self, text="GPIO", fg=self.colorMng.get_foreground_color(), bg=self.colorMng.get_default_color(), padx=5)
        self.pin_nr.bind("<Motion>", self.hover_sensor)
        self.pin_nr.bind("<Leave>", self.unhover_sensor)
        self.pin_nr.bind("<Button-1>", self.change_sensor_state)
        self.pin_nr.grid(column=2, row=1, sticky="e")

        self.pin_icon = Label(self, text=self.data.gpioPin, fg=self.colorMng.get_foreground_color(), bg=self.colorMng.get_default_color(), padx=5)
        self.pin_icon.bind("<Motion>", self.hover_sensor)
        self.pin_icon.bind("<Leave>", self.unhover_sensor)
        self.pin_icon.bind("<Button-1>", self.select_sensor)
        self.pin_icon.grid(column=3, row=1, sticky="e")

        if not self.is_last: # add divider if not last item
            self.divider = Canvas(self, width=self.item_width, height=1, bg=self.colorMng.get_foreground_color(),
                                  highlightthickness=0, relief="ridge")
            self.divider.grid(column=0, row=1, columnspan=4, sticky="s")

        if self.is_active():
            self.enable()
        else:
            self.disable()

    def get_data(self):
        return self.data

    def get_values(self):
        return self.sensor_values

    def clear_values(self):
        self.sensor_values.clear_values()

    def is_active(self):
        return self.data.active

    def is_selected(self):
        return self._is_selected

    def change_sensor_state(self, event):
        self.disable_callback(self.index, self.data.name)

    def select_sensor(self, event):
        if self.data.active:
            self.select_callback(self.index, self.data.name)

    def start_value_collection(self):
        self.worker_queue = queue.Queue()
        self.worker = DemoValueWorker(self.data.gpioPin, self.worker_queue)
        self.worker.start()
        self.after(100, self.__on_new_value)

    def stop_value_collection(self):
        self.worker.stop()
        self.worker_queue = None
        self.worker = None

    def is_measuring(self):
        return self.worker.is_running()

    def hover_sensor(self, event):
        if self.data.active:
            if self._is_selected:
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

    def unhover_sensor(self, event):
        if self._is_selected:
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

    def select(self):
        if self.data.active:
            self._is_selected = True
            self.configure(bg=self.colorMng.get_selected_color())
            self.sensor_icon.configure(bg=self.colorMng.get_selected_color())
            self.sensor_name.configure(bg=self.colorMng.get_selected_color())
            self.disable_btn.configure(bg=self.colorMng.get_selected_color())
            self.pin_nr.configure(bg=self.colorMng.get_selected_color())
            self.pin_icon.configure(bg=self.colorMng.get_selected_color())
            return True
        return False

    def deselect(self):
        if self.data.active:
            self._is_selected = False
            self.configure(bg=self.colorMng.get_default_color())
            self.sensor_icon.configure(bg=self.colorMng.get_default_color())
            self.sensor_name.configure(bg=self.colorMng.get_default_color())
            self.disable_btn.configure(bg=self.colorMng.get_default_color())
            self.pin_nr.configure(bg=self.colorMng.get_default_color())
            self.pin_icon.configure(bg=self.colorMng.get_default_color())
            return True
        return False

    def disable(self):
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

    def __on_new_value(self):
        try:
            if self.worker_queue is not None:
                new_values = self.worker_queue.get(0)
                if new_values is None:
                    # Measuring stoped
                    return
            else:
                return
        except queue.Empty:
            self.after(100, self.__on_new_value)
            return

        self.sensor_values.add_new_value(new_values.value, new_values.timestamp)
        self.value_update_callback(self.index, self.data.name, self.sensor_values)
        self.after(100, self.__on_new_value)

    def __on_resize(self, event):
        self.width = event.width
        self.height = event.height
        self.config(width=self.width, height=self.height)
