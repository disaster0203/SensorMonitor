import os
from typing import List, Optional
from SensorMonitor.DataContainer.sensor import Sensor
from SensorMonitor.DataContainer.windowSettings import WindowSettings
from SensorMonitor.DataContainer.outputSettings import OutputSettings
from SensorMonitor.DataContainer.configData import ConfigData
from SensorMonitor.DataContainer.gpio import GPIO
from SensorMonitor.DataContainer.i2cDevice import I2CDevice
from SensorMonitor.Manager.jsonManager import JsonManager


class ConfigManager:
    """ Manages the config file by reading its content and writing changes the user does to the file.

    This class uses the singleton pattern which means that while the application runs only one instance
    of this class can exist at the same time. At each position the class is used always the same instance
    is manipulated.
    """

    __instance = None
    path_to_config = ""
    config_data = None

    def __new__(cls, *args, **kwargs):
        """Singleton pattern: Checks if the class is already initialized. If not it is initialized and
        stored in the private internal variable __instance. Do not manipulate __instance from outside!"""

        if not cls.__instance:
            cls.__instance = super(ConfigManager, cls).__new__(cls, *args, **kwargs)
        return cls.__instance

    def load_config(self, path: str):
        """Checks if a config file exists and returns its content. If no file exists it will create a new
        one with default values and returns their content after creation.
        :param path: str = path to the config file. If it does not exist, a new config file will be created at this
                           location."""

        self.path_to_config = path
        if not os.path.exists(path) or not os.path.isfile(path):
            self.config_data = self.__create_config_from_defaults__()
        else:
            self.config_data = JsonManager.from_file(self.path_to_config, "r")

    def write_config_data(self):
        """Writes the data that is currently stored in an ConfigData variable into the config file on the disk."""

        if self.config_data is not None and os.path.exists(self.path_to_config) and os.path.isfile(self.path_to_config):
            JsonManager.to_file(self.config_data, self.path_to_config, "w")

    def get_sensor(self, index: int) -> Optional[Sensor]:
        """Returns the sensor config data at the given index from the list of sensors. If the index exceeds the range
        of the sensor list (0 > index > sensor list size) this method will return 'None'.
        :param index: int = the list index of the sensor data to return.

        :return The sensor data at the given index or None if the index exceeds the sensor lists range.
        """

        if self.config_data is not None and 0 <= index < len(self.config_data.sensors):
            return self.config_data.sensors[index]
        else:
            return None

    def get_sensors(self) -> Optional[List[Sensor]]:
        """Returns the whole list of sensor config data. If the list is not initialized, 'None' will be returned.

        :return The list of all sensor data objects that are stored in the config file or 'None' if the list is not yet
                initialized.
        """

        if self.config_data is not None:
            return self.config_data.sensors
        else:
            return None

    def change_sensor_state(self, new_state: bool, index: int) -> bool:
        """Changes the active setting of a specific sensor. This will rewrite the config file on disk and therefor
        the changes are permanent.

        :param new_state: bool = the new state of the sensor. True for enabled and False for disabled.
        :param index: int = the list index of the sensor to manipulate. If the index exceeds the range of the list nothing
                            will be done.

        :return True if changing the sensors state was successful and False otherwise.
        """

        if self.config_data is not None and 0 <= index < len(self.config_data.sensors):
            self.config_data.sensors[index].active = new_state
            self.write_config_data()
            return True
        else:
            return False

    def get_window_settings(self) -> Optional[WindowSettings]:
        """Returns a WindowSettings object with all window settings that are stored inside the config file.

        :return The window settings that are stored in the config file, or 'None' if the data is not yet
                initialized.
        """

        if self.config_data is not None:
            return self.config_data.window_settings
        else:
            return None

    def get_output_settings(self) -> Optional[OutputSettings]:
        """Returns a OutputSettings object with all output settings that are stored inside the config file.

        :return The output settings that are stored in the config file, or 'None' if the data is not yet
                initialized.
        """
        if self.config_data is not None:
            return self.config_data.output_settings
        else:
            return None

    def change_output_path(self, path: str) -> bool:
        """Changes the output folder path. This will rewrite the config file on disk and therefor the
        changes are permanent.

        :param path: str = the new output folder path. The path must be a folder path and contain no file.
                           It does not necessarily have to end with a /  (Linux, Apple) or a \\ (Windows).
                           The separators / and \\ are changed automatically depending on the os the
                           application currently runs on.

        :return True if changing the output path was successful and False otherwise.
        """

        if self.config_data is not None:
            self.config_data.output_settings.defaultPath = path
            self.write_config_data()
            return True
        else:
            return False

    def __create_config_from_defaults__(self) -> ConfigData:
        """Creates a new config file at the default config path from default values and returns a ConfigData
        object.
        The default values are:
        Window settings
        - width = 800
        - height = 600
        - value_history_size = 100
        - color_theme = 'Dark'
        Output Settings
        - defaultPath = '../'
        - defaultFilename = 'Measurement_'
        - defaultFileExtension = 'csv'
        - separator = ','
        Sensor List with one sensor
        - name = 'TestSensor'
        - gpioPin = [1, 'IN']
        - offset = 0
        - active = True
        - color = '#FF0000'
        - units = 'C' (for degree celsius; the little circle is an invalid character in utf-8)
        - update_interval = 0.5

        :return a ConfigData object containing the default config values.
        """
        window = WindowSettings(800, 600, 100, "Dark", "Live")
        output = OutputSettings("../", "Measurement_", "csv", ",")
        sensors = [Sensor("Distance Sensor 1", "DistanceSensor_GP2Y0A710K0F", [GPIO(1, "IN")], None, 1, 0, True, ["#FF0000"], ["cm"], 0.5),
                   Sensor("Distance Sensor 2", "DistanceSensor_GP2Y0A21YK0F", [GPIO(2, "IN")], None, 1, 0, False, ["#00FF00"], ["cm"], 0.5),
                   Sensor("Weather Sensor", "WeatherSensor_BMP280", None, I2CDevice(1), 3, 0, False, ["#FF0000", "#00FF00", "#0000FF"],
                          ["C", "hPa", "m"], 0.5)]
        new_config = ConfigData(sensors, window, output)

        JsonManager.to_file(new_config, self.path_to_config, "x")

        return new_config
