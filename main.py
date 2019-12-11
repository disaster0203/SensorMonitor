import tkinter as tk
from tkinter import ttk
import configManager as CM
import colorManager as Col
import sensorList as SL


def on_disable(index, name, state):
    print("disabled: " + name + " - " + str(not state))


def on_select(index, name, state):
    print("select: " + name + " - " + str(state))


configMng = CM.ConfigManager("./config.json")
colorMng = Col.ColorManager()
colorMng.set_theme("dark")

root = tk.Tk()
root.wm_title("Raspberry Sensor Monitor")
root.geometry(str(configMng.get_window_settings().width) + "x" + str(configMng.get_window_settings().height))

list = SL.SensorList(root, configMng.config_data.sensors, on_disable, on_select)
list.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W))

root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=4)

root.mainloop()
