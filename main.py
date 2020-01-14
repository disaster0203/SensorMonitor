import time
import queue
import os
import platform
from tkinter import Tk, filedialog, Frame, Entry, Canvas, Label, END
from SensorMonitor.Manager.configManager import ConfigManager
from SensorMonitor.Manager.colorManager import ColorManager
from SensorMonitor.Widgets.sensorList import SensorList
from SensorMonitor.Widgets.graphView import GraphView
from SensorMonitor.Worker.timeWorker import TimeWorker
from SensorMonitor.DataContainer.sensorValues import SensorValues

############################################################################
# Define global variables
configMng = ConfigManager()
configMng.load_config("./config.json")
colorMng = ColorManager()
colorMng.set_theme("dark")


class MainWindow:
    """Represents the main window of the application."""

    play_icon = None

    def __init__(self, window: Tk):
        """Initializes the main window.

        :param window: Tk = the window object
        """

        self.window = window

        self.window.resizable(False, False)
        self.window.wm_title("Raspberry Sensor Monitor")
        self.window.geometry(str(configMng.get_window_settings().width) + "x" + str(configMng.get_window_settings().height))
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        self.is_running = False
        self.timer_queue = None
        self.time_worker = None

        self._setup_layout()

        # Select the first selectable sensor in the list
        selectable = self.sensor_list.get_first_selectable()
        if selectable != -1:
            self.sensor_list.select(selectable)

    def _setup_layout(self):
        """Initializes and configures all layout components of the window:
        - Sensor list
        - Folder path chooser
        - Folder path icon
        - Play/Pause icon
        - Graph view
        - Current sensor name
        - Current sensor value
        - Current sensor max
        - Current sensor min
        - Current sensor avg
        - Recording time label
        - Recording time value
        """

        ############################################################################
        # Sensor list area
        self.list_area = Frame(self.window, bg=colorMng.get_secondary_color(), height=configMng.get_window_settings().height,
                               width=configMng.get_window_settings().width * 0.25)
        self.list_area.grid_rowconfigure(0, weight=1)
        self.list_area.grid_columnconfigure(0, weight=0)
        self.list_area.grid(column=0, row=0, sticky="nsw")
        self.sensor_list = SensorList(self.list_area, self.on_disable, self.on_select, self.on_value,
                                      configMng.get_window_settings().width * 0.25)
        self.sensor_list.grid(column=0, row=0, sticky="nsw")

        ############################################################################
        # Content area
        self.content_area = Frame(self.window, bg=colorMng.get_default_color(), height=configMng.get_window_settings().height,
                                  width=configMng.get_window_settings().width * 0.75)
        self.content_area.grid(column=0, row=0, sticky="nse")

        ############################################################################
        # Control area (Path text input, open folder button, play/pause button)
        self.control_area = Frame(self.content_area, bg=colorMng.get_default_color())
        self.control_area.grid(column=1, row=0, sticky="nswe")
        self.control_area.grid_rowconfigure(0, weight=1)
        self.control_area.grid_columnconfigure(0, weight=1)
        self.control_area.grid_columnconfigure(1, weight=1)
        self.control_area.grid_columnconfigure(2, weight=1)
        # Path text input
        self.path_input = Entry(self.control_area, bd=0, fg=colorMng.get_foreground_color(),
                                bg=colorMng.get_secondary_color(), font="Helvetica 14")
        self.path_input.grid(column=0, row=0, sticky="we", padx=10, pady=10)
        self.path_input.insert(0, self._create_platform_specific_path(configMng.get_output_settings().default_path))
        # Open folder button
        self.folder_icon = Canvas(self.control_area, width=20, height=20, bg=colorMng.get_default_color(),
                                  highlightthickness=0, relief="ridge")
        self.folder_icon = colorMng.get_folder_icon(colorMng.get_foreground_color(), self.folder_icon, 20, 20)
        self.folder_icon.bind("<Button-1>", self.open_folder_dialog)
        self.folder_icon.grid(column=1, row=0, sticky="W", padx=5, pady=10)
        # Play/Pause button
        self.play_icon = Canvas(self.control_area, width=20, height=20, bg=colorMng.get_default_color(),
                                highlightthickness=0, relief="ridge")
        self.play_icon = colorMng.get_play_icon(colorMng.get_default_signal_color(), self.play_icon, 20, 20)
        self.play_icon.bind("<Button-1>", self.toggle_start_stop)
        self.play_icon.grid(column=2, row=0, sticky="E", padx=10, pady=10)

        ############################################################################
        # Graph area
        selected_sensor_data = self.sensor_list.get_selected_item()

        self.graph_area = Frame(self.content_area, bg=colorMng.get_default_color())
        self.graph_area.grid_rowconfigure(0, weight=1)
        self.graph_area.grid_columnconfigure(0, weight=1)
        self.graph_area.grid(column=1, row=1, sticky="nswe")
        if selected_sensor_data is None:
            temp_color = "#000000"
        else:
            temp_color = selected_sensor_data.get_data().color
        self.graph = GraphView(self.graph_area, [], configMng.get_window_settings().value_history_size, temp_color, 5,
                               configMng.get_window_settings().width * 0.75 - 20,  # minus padding
                               configMng.get_window_settings().height / 7 * 4 - 20)  # minus padding
        self.graph.grid(column=0, row=0, sticky="nswe", padx=10, pady=10)

        ############################################################################
        # Value display area
        self.value_area = Frame(self.content_area, bg=colorMng.get_default_color())
        self.value_area.grid_rowconfigure(0, weight=2)
        self.value_area.grid_rowconfigure(1, weight=1)
        self.value_area.grid_rowconfigure(2, weight=1)
        self.value_area.grid_rowconfigure(3, weight=1)
        self.value_area.grid_rowconfigure(4, weight=1)
        self.value_area.grid_columnconfigure(0, weight=1)
        self.value_area.grid_columnconfigure(1, weight=3)
        self.value_area.grid(column=1, row=2, sticky="nswe")
        # Sensor name
        if selected_sensor_data is None:
            temp_name = "Kein Sensor aktiv..."
            temp_current = ""
            temp_max = ""
            temp_min = ""
            temp_avg = ""
        else:
            temp_name = selected_sensor_data.get_data().name
            temp_current = round(selected_sensor_data.get_values().current, 3)
            temp_max = round(selected_sensor_data.get_values().max, 3)
            temp_min = round(selected_sensor_data.get_values().min, 3)
            temp_avg = round(selected_sensor_data.get_values().avg, 3)

        self.sensor_name = Label(self.value_area, font="Helvetica 14 bold", text=temp_name,
                                 fg=colorMng.get_foreground_color(), bg=colorMng.get_default_color())
        self.sensor_name.grid(column=0, row=0, columnspan=2, sticky="wn", padx=10, pady=10)

        # Value labels
        self.current_value_label = Label(self.value_area, font="Helvetica 14", text="Akt.:",
                                         fg=colorMng.get_foreground_color(), bg=colorMng.get_default_color())
        self.current_value_label.grid(column=0, row=1, sticky="wn", padx=10)
        self.current_value = Label(self.value_area, font="Helvetica 14", text=temp_current,
                                   fg=colorMng.get_foreground_color(), bg=colorMng.get_default_color())
        self.current_value.grid(column=0, row=1, sticky="en", padx=10)

        self.max_value_label = Label(self.value_area, font="Helvetica 11", text="Max.:",
                                     fg=colorMng.get_foreground_color(), bg=colorMng.get_default_color())
        self.max_value_label.grid(column=0, row=2, sticky="wn", padx=10)
        self.max_value = Label(self.value_area, font="Helvetica 11", text=temp_max,
                               fg=colorMng.get_foreground_color(), bg=colorMng.get_default_color())
        self.max_value.grid(column=0, row=2, sticky="en", padx=10)

        self.min_value_label = Label(self.value_area, font="Helvetica 11", text="Min.:",
                                     fg=colorMng.get_foreground_color(), bg=colorMng.get_default_color())
        self.min_value_label.grid(column=0, row=3, sticky="wn", padx=10)
        self.min_value = Label(self.value_area, font="Helvetica 11", text=temp_min,
                               fg=colorMng.get_foreground_color(), bg=colorMng.get_default_color())
        self.min_value.grid(column=0, row=3, sticky="en", padx=10)

        self.avg_value_label = Label(self.value_area, font="Helvetica 11", text="Avg.:",
                                     fg=colorMng.get_foreground_color(), bg=colorMng.get_default_color())
        self.avg_value_label.grid(column=0, row=4, sticky="wn", padx=10)
        self.avg_value = Label(self.value_area, font="Helvetica 11", text=temp_avg,
                               fg=colorMng.get_foreground_color(), bg=colorMng.get_default_color())
        self.avg_value.grid(column=0, row=4, sticky="en", padx=10)

        # Time
        self.recording_time_label = Label(self.value_area, font="Helvetica 11", text="Aufnahmezeit",
                                          fg=colorMng.get_foreground_color(), bg=colorMng.get_default_color())
        self.recording_time_label.grid(column=2, row=3, sticky="en", padx=10)
        self.recording_time = Label(self.value_area, font="Helvetica 11", text="00:00:00",
                                    fg=colorMng.get_foreground_color(), bg=colorMng.get_default_color())
        self.recording_time.grid(column=2, row=4, sticky="en", padx=10)

    def on_disable(self, index: int, name: str, state: bool):
        """Callback function that gets called if a sensor item was disabled/enabled.

        :param index: int = the list index of the disabled/enabled item.
        :param name: str = the name of the disabled/enabled item.
        :param state: bool = whether the item was is disabled (False) or enabled (True) now.
        """

        configMng.change_sensor_state(state, index)
        if self.sensor_list.get_selected_index() == -1:
            self.sensor_name.configure(text="Kein Sensor aktiv...")
            self.current_value.configure(text="")
            self.max_value.configure(text="")
            self.min_value.configure(text="")
            self.avg_value.configure(text="")
            self.graph.clear()
        elif self.sensor_list.get_selected_index() == index:
            self.sensor_name.configure(text=name)
            self.current_value.configure(text=round(self.sensor_list.get_sensors()[index].get_values().current, 3))
            self.max_value.configure(text=round(self.sensor_list.get_sensors()[index].get_values().max, 3))
            self.min_value.configure(text=round(self.sensor_list.get_sensors()[index].get_values().min, 3))
            self.avg_value.configure(text=round(self.sensor_list.get_sensors()[index].get_values().avg, 3))
            self.graph.replace(self.sensor_list.get_sensors()[index].get_values().last_values,
                               self.sensor_list.get_sensors()[index].get_data().color)

    def on_select(self, index: int, name: str):
        """Callback function that gets called if a sensor item was selected.

        :param index: int = the index of the selected item.
        :param name: str = the name of the selected item.
        """

        self.sensor_name.configure(text=name)
        # Check if index is in range of sensor list
        sensors = self.sensor_list.get_sensors()
        if len(sensors) > 0 and index < len(sensors):
            # Check if sensor has values
            values = sensors[index].get_values()
            if values is not None:
                # Display values in GUI
                self.current_value.configure(text=round(values.current, 3))
                self.max_value.configure(text=round(values.max, 3))
                self.min_value.configure(text=round(values.min, 3))
                self.avg_value.configure(text=round(values.avg, 3))
                self.graph.replace(values.last_values, sensors[index].get_data().color)

    def on_value(self, index: int, name: str, values: SensorValues):
        """Callback function that gets called if now values from the currently selected sensor arrived.

        :param index: int = the index of the sensor.
        :param name: str = the name of the sensor.
        :param values: SensorValues = the new values object.
        """

        self.sensor_name.configure(text=name)
        self.current_value.configure(text=round(values.current, 3))
        self.max_value.configure(text=round(values.max, 3))
        self.min_value.configure(text=round(values.min, 3))
        self.avg_value.configure(text=round(values.avg, 3))
        self.graph.add_value(values.current)

    def open_folder_dialog(self, event):
        """Opens a platform specific window where the user can select a folder."""

        self.path_input.delete(0, END)
        complete_path = self._create_platform_specific_path(filedialog.askdirectory())
        self.path_input.insert(0, complete_path)
        configMng.change_output_path(complete_path)

    def toggle_start_stop(self, event):
        """Starts or stops a measurement."""

        self.play_icon.delete("all")
        if not self.is_running:
            self.is_running = True
            self.play_icon = colorMng.get_stop_icon(colorMng.get_default_signal_color(), self.play_icon, 20, 20)
            self.graph.clear()
            self.sensor_list.clear()

            self.timer_queue = queue.Queue()
            self.time_worker = TimeWorker(self.timer_queue)
            self.time_worker.start()
            self.window.after(100, self.process_time_queue)
            self.sensor_list.start_measurement()
        else:
            self.is_running = False
            self.play_icon = colorMng.get_play_icon(colorMng.get_default_signal_color(), self.play_icon, 20, 20)
            self.time_worker.stop()
            self.sensor_list.stop_measurement()

    def process_time_queue(self):
        """Listens for updates in the queue of the time worker and displays new timestamps in the GUI."""

        try:
            seconds = self.timer_queue.get(0)
            if seconds is None:
                self.on_time_worker_finished()
                return
            self.recording_time.configure(text=time.strftime("%H:%M:%S", time.gmtime(seconds)))
        except queue.Empty:
            self.window.after(100, self.process_time_queue)
            return
        self.timer_queue.queue.clear()
        self.window.after(100, self.process_time_queue)

    def on_time_worker_finished(self):
        """Callback that gets called if a down-counting time worker finished."""

        self.toggle_start_stop(None)

    @staticmethod
    def _create_platform_specific_path(input_path: str) -> str:
        """Adds the right platform specific folder separators to the path. Linux and Apple (Darwin) new / while Windows needs \\

        :param input_path: str = the path to transform.
        :return the transformed path.
        """

        current_platform = platform.system()
        if current_platform == "Linux" or current_platform == "Darwin":
            input_path = input_path.replace("\\", "/")
        elif "Windows":
            input_path = input_path.replace("/", "\\")

        # Add / or \\ at the end of the path if it is not already there
        return os.path.join(input_path, "")


############################################################################
# Create window
root = Tk()
# root.protocol("WM_DELETE_WINDOW", self.quit)
main_window = MainWindow(root)
root.mainloop()
