from datetime import datetime
import time
import tkinter as tk
from tkinter import filedialog
import queue
import configManager as CM
import colorManager as Col
import sensorList as List
import graphView as Graph
from timeWorker import TimeWorker

############################################################################
# Define global variables
configMng = CM.ConfigManager("./config.json")
colorMng = Col.ColorManager()
colorMng.set_theme("dark")


class MainWindow:
    def __init__(self, window):
        self.window = window

        self.window.resizable(False, False)
        self.window.wm_title("Raspberry Sensor Monitor")
        self.window.geometry(str(configMng.get_window_settings().width) + "x" + str(configMng.get_window_settings().height))
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        self.is_running = False
        self.timer_queue = None
        self.time_wrkr = None

        self._setup_layout()

        # Select the first selectable sensor in the list
        selectable = self.sensor_list.get_first_selectable()
        if selectable != -1:
            self.sensor_list.select(selectable)

    def _setup_layout(self):
        ############################################################################
        # Sensor list area
        self.list_area = tk.Frame(self.window, bg=colorMng.get_secondary_color(), height=configMng.get_window_settings().height,
                                  width=configMng.get_window_settings().width * 0.25)
        self.list_area.grid_rowconfigure(0, weight=1)
        self.list_area.grid_columnconfigure(0, weight=0)
        self.list_area.grid(column=0, row=0, sticky="nsw")
        self.sensor_list = List.SensorList(self.list_area, configMng.get_sensors(), self.on_disable, self.on_select, self.on_value,
                                           configMng.get_window_settings().width * 0.25)
        self.sensor_list.grid(column=0, row=0, sticky="nsw")

        ############################################################################
        # Content area
        self.content_area = tk.Frame(self.window, bg=colorMng.get_default_color(), height=configMng.get_window_settings().height,
                                     width=configMng.get_window_settings().width * 0.75)
        self.content_area.grid(column=0, row=0, sticky="nse")

        ############################################################################
        # Control area (Path text input, open folder button, play/pause button)
        self.control_area = tk.Frame(self.content_area, bg=colorMng.get_default_color())
        self.control_area.grid(column=1, row=0, sticky="nswe")
        self.control_area.grid_rowconfigure(0, weight=1)
        self.control_area.grid_columnconfigure(0, weight=1)
        self.control_area.grid_columnconfigure(1, weight=1)
        self.control_area.grid_columnconfigure(2, weight=1)
        # Path text input
        self.path_input = tk.Entry(self.control_area, bd=0, fg=colorMng.get_foreground_color(),
                                   bg=colorMng.get_secondary_color(), font="Helvetica 14")
        self.path_input.grid(column=0, row=0, sticky="we", padx=10, pady=10)
        self.path_input.insert(0, configMng.get_output_settings().defaultPath)
        # Open folder button
        self.folder_icon = tk.Canvas(self.control_area, width=20, height=20, bg=colorMng.get_default_color(),
                                     highlightthickness=0, relief="ridge")
        self.folder_icon = colorMng.get_folder_icon(colorMng.get_foreground_color(), self.folder_icon, 20, 20)
        self.folder_icon.bind("<Button-1>", self.open_folder_dialog)
        self.folder_icon.grid(column=1, row=0, sticky="W", padx=5, pady=10)
        # Play/Pause button
        self.play_icon = tk.Canvas(self.control_area, width=20, height=20, bg=colorMng.get_default_color(),
                                   highlightthickness=0, relief="ridge")
        self.play_icon = colorMng.get_play_icon(colorMng.get_default_signal_color(), self.play_icon, 20, 20)
        self.play_icon.bind("<Button-1>", self.toggle_start_stop)
        self.play_icon.grid(column=2, row=0, sticky="E", padx=10, pady=10)

        ############################################################################
        # Graph area
        self.graph_area = tk.Frame(self.content_area, bg=colorMng.get_default_color())
        self.graph_area.grid_rowconfigure(0, weight=1)
        self.graph_area.grid_columnconfigure(0, weight=1)
        self.graph_area.grid(column=1, row=1, sticky="nswe")
        self.graph = Graph.GraphView(self.graph_area, [], 20, configMng.get_sensors()[0].color, 5,
                                     configMng.get_window_settings().width * 0.75 - 20,  # minus padding
                                     configMng.get_window_settings().height / 7 * 4 - 20)  # minus padding
        self.graph.grid(column=0, row=0, sticky="nswe", padx=10, pady=10)

        ############################################################################
        # Value display area
        self.value_area = tk.Frame(self.content_area, bg=colorMng.get_default_color())
        self.value_area.grid_rowconfigure(0, weight=2)
        self.value_area.grid_rowconfigure(1, weight=1)
        self.value_area.grid_rowconfigure(2, weight=1)
        self.value_area.grid_rowconfigure(3, weight=1)
        self.value_area.grid_rowconfigure(4, weight=1)
        self.value_area.grid_columnconfigure(0, weight=1)
        self.value_area.grid_columnconfigure(1, weight=3)
        self.value_area.grid(column=1, row=2, sticky="nswe")
        # Sensor name
        self.sensor_name = tk.Label(self.value_area, font="Helvetica 14 bold", text=self.sensor_list.get_selected_item().get_data().name,
                                    fg=colorMng.get_foreground_color(), bg=colorMng.get_default_color())
        self.sensor_name.grid(column=0, row=0, columnspan=2, sticky="wn", padx=10, pady=10)

        # Value labels
        self.current_value_label = tk.Label(self.value_area, font="Helvetica 14", text="Akt.:",
                                            fg=colorMng.get_foreground_color(), bg=colorMng.get_default_color())
        self.current_value_label.grid(column=0, row=1, sticky="wn", padx=10)
        self.current_value = tk.Label(self.value_area, font="Helvetica 14", text="25.3 °C",
                                      fg=colorMng.get_foreground_color(), bg=colorMng.get_default_color())
        self.current_value.grid(column=0, row=1, sticky="en", padx=10)

        self.max_value_label = tk.Label(self.value_area, font="Helvetica 11", text="Max.:",
                                        fg=colorMng.get_foreground_color(), bg=colorMng.get_default_color())
        self.max_value_label.grid(column=0, row=2, sticky="wn", padx=10)
        self.max_value = tk.Label(self.value_area, font="Helvetica 11", text="34.1 °C",
                                  fg=colorMng.get_foreground_color(), bg=colorMng.get_default_color())
        self.max_value.grid(column=0, row=2, sticky="en", padx=10)

        self.min_value_label = tk.Label(self.value_area, font="Helvetica 11", text="Min.:",
                                        fg=colorMng.get_foreground_color(), bg=colorMng.get_default_color())
        self.min_value_label.grid(column=0, row=3, sticky="wn", padx=10)
        self.min_value = tk.Label(self.value_area, font="Helvetica 11", text="24.5 °C",
                                  fg=colorMng.get_foreground_color(), bg=colorMng.get_default_color())
        self.min_value.grid(column=0, row=3, sticky="en", padx=10)

        self.avg_value_label = tk.Label(self.value_area, font="Helvetica 11", text="Avg.:",
                                        fg=colorMng.get_foreground_color(), bg=colorMng.get_default_color())
        self.avg_value_label.grid(column=0, row=4, sticky="wn", padx=10)
        self.avg_value = tk.Label(self.value_area, font="Helvetica 11", text="27.8 °C",
                                        fg=colorMng.get_foreground_color(), bg=colorMng.get_default_color())
        self.avg_value.grid(column=0, row=4, sticky="en", padx=10)

        # Time
        self.recording_time_label = tk.Label(self.value_area, font="Helvetica 11", text="Aufnahmezeit",
                                             fg=colorMng.get_foreground_color(), bg=colorMng.get_default_color())
        self.recording_time_label.grid(column=2, row=3, sticky="en", padx=10)
        self.recording_time = tk.Label(self.value_area, font="Helvetica 11", text="00:00:00",
                                       fg=colorMng.get_foreground_color(), bg=colorMng.get_default_color())
        self.recording_time.grid(column=2, row=4, sticky="en", padx=10)

    def on_disable(self, index, name, state):
        configMng.change_sensor_state(state, index)

    def on_select(self, index, name):
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

    def on_value(self, index, name, values):
        self.sensor_name.configure(text=name)
        self.current_value.configure(text=round(values.current, 3))
        self.max_value.configure(text=round(values.max, 3))
        self.min_value.configure(text=round(values.min, 3))
        self.avg_value.configure(text=round(values.avg, 3))
        self.graph.add_value(values.current)

    def open_folder_dialog(self, event):
        self.path_input.delete(0, tk.END)
        complete_path = filedialog.askdirectory()
        self.path_input.insert(0, complete_path)
        return complete_path

    @staticmethod
    def construct_filename(folder_path):
        cur_time = datetime.now().strftime("%Y-%m-%d_%H:%M")
        return folder_path + "/" + configMng.get_output_settings().defaultFilename + cur_time + configMng.get_output_settings().defaultFileExtension

    def toggle_start_stop(self, event):
        self.play_icon.delete("all")
        if not self.is_running:
            self.is_running = True
            self.play_icon = colorMng.get_stop_icon(colorMng.get_default_signal_color(), self.play_icon, 20, 20)

            self.timer_queue = queue.Queue()
            self.time_wrkr = TimeWorker(self.timer_queue)
            self.time_wrkr.start()
            self.window.after(100, self.process_time_queue)
            self.sensor_list.start_measurement()
        else:
            self.is_running = False
            self.play_icon = colorMng.get_play_icon(colorMng.get_default_signal_color(), self.play_icon, 20, 20)
            self.time_wrkr.stop()
            self.sensor_list.stop_measurement()

    def process_time_queue(self):
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
        self.toggle_start_stop(None)


############################################################################
# Create window
root = tk.Tk()
#root.protocol("WM_DELETE_WINDOW", self.quit)
main_window = MainWindow(root)
root.mainloop()
