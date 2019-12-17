from typing import List
from SensorMonitor.DataContainer.sensor import Sensor
from SensorMonitor.DataContainer.windowSettings import WindowSettings
from SensorMonitor.DataContainer.outputSettings import OutputSettings


class ConfigData:
    """Container class that stores all config settings.

    The following settings are provided:
    :param sensors: List[Sensor] = a list of all sensor objects to use. Stores sensor names, colors, gpio pins, etc.
    :param window_settings: WindowSettings = stores the window settings like window width and height.
    :param output_settings: OutputSettings = stores the output settings like file path, file name, extension.
    """

    def __init__(self, sensors: List[Sensor], window_settings: WindowSettings, output_settings: OutputSettings):
        """Initializes this class and stores the given values in their corresponding fields.

        :param sensors: List[Sensor] = a list of all sensor objects to use. Stores sensor names, colors, gpio pins, etc.
        :param window_settings: WindowSettings = stores the window settings like window width and height.
        :param output_settings: OutputSettings = stores the output settings like file path, file name, extension.
        """

        self.sensors = sensors
        self.window_settings = window_settings
        self.output_settings = output_settings
