from typing import List
from SensorMonitor.DataContainer.gpio import GPIO
from SensorMonitor.Manager.jsonManager import JsonManager


@JsonManager.register
class Sensor:
    """Container class for sensor settings.

        The following settings are provided:
        :param name: str = the name of the sensor that is displayed in the GUI.
        :param gpio_pins: List[GPIO] = the GPIO pins this sensor uses. Needed to access the sensor.
        :param offset: float = calibration value that will be added to each received sensor value.
        :param active: bool = whether the sensor is active or not. If it is inactive no data will be recorded.
        :param color: str = The graph color of this sensor. It only accepts hex color values (e.g. #FF0000 for Red)
        :param unit: str = The SI unit of the sensor values. This is only used for displaying in the GUI and can also
                           be an empty string ("") if the unit is unknown or does not exist.
        :param update_interval: float = How often the software triggers the sensor to receive new values (in seconds).
        """

    def __init__(self, name: str = "", gpio_pins: List[GPIO] = None, offset: float = 0, active: bool = False, color: str = "", unit: str = "",
                 update_interval: float = 0):
        """Initializes this class and stores the given values in their corresponding fields.

        :param name: str = the name of the sensor that is displayed in the GUI.
        :param gpio_pins: List[GPIO] = the GPIO pins this sensor uses. Needed to access the sensor.
        :param offset: float = calibration value that will be added to each received sensor value.
        :param active: bool = whether the sensor is active or not. If it is inactive no data will be recorded.
        :param color: str = The graph color of this sensor. It only accepts hex color values (e.g. #FF0000 for Red)
        :param unit: str = The SI unit of the sensor values. This is only used for displaying in the GUI and can also
                           be an empty string ("") if the unit is unknown or does not exist.
        :param update_interval: float = How often the software triggers the sensor to receive new values (in seconds).
        """

        self.name = name
        self.gpio_pins = gpio_pins
        self.offset = offset
        self.active = active
        self.color = color
        self.unit = unit
        self.update_interval = update_interval
