from typing import List
from SensorMonitor.DataContainer.gpio import GPIO
from SensorMonitor.DataContainer.i2cDevice import I2CDevice
from SensorMonitor.Manager.jsonManager import JsonManager


@JsonManager.register
class Sensor:
    """Container class for sensor settings.

        The following settings are provided:
        :param name: str = the name of the sensor that is displayed in the GUI.
        :param device_type: str = the type of the sensor that is used to chose the right value converter function.
        :param gpio_pins: List[GPIO] = if the sensor uses GPIO this class specifies the pins. If GPIO is defined I2CDevice has to be None.
        :param i2c_device: I2CDevice = if the sensor uses I2C this class specifies the bus. If I2CDevice is defined GPIO has to be None.
        :param value_count: int = How many different values the sensor returns.
        :param offset: float = calibration value that will be added to each received sensor value.
        :param active: bool = whether the sensor is active or not. If it is inactive no data will be recorded.
        :param colors: List[str] = The graph colors of this sensor. It only accepts hex color values (e.g. #FF0000 for Red)
        :param units: List[str] = The SI units of the sensor values. This is only used for displaying in the GUI and can also
                           be an empty string ("") if the unit is unknown or does not exist.
        :param update_interval: float = How often the software triggers the sensor to receive new values (in seconds).
        """

    def __init__(self, name: str = "", device_type: str = "", gpio_pins: List[GPIO] = None, i2c_device: I2CDevice = None, value_count: int = 1,
                 offset: float = 0, active: bool = False, colors: List[str] = "", units: List[str] = [""], update_interval: float = 0):
        """Initializes this class and stores the given values in their corresponding fields.

        :param name: str = the name of the sensor that is displayed in the GUI.
        :param device_type: str = the type of the sensor that is used to chose the right value converter function.
        :param gpio_pins: List[GPIO] = if the sensor uses GPIO this class specifies the pins. If GPIO is defined I2CDevice has to be None.
        :param i2c_device: I2CDevice = if the sensor uses I2C this class specifies the bus. If I2CDevice is defined GPIO has to be None.
        :param value_count: int = How many different values the sensor returns.
        :param offset: float = calibration value that will be added to each received sensor value.
        :param active: bool = whether the sensor is active or not. If it is inactive no data will be recorded.
        :param colors: List[str] = The graph colors of this sensor. It only accepts hex color values (e.g. #FF0000 for Red)
        :param units: List[str] = The SI units of the sensor values. This is only used for displaying in the GUI and can also
                           be an empty string ("") if the unit is unknown or does not exist.
        :param update_interval: float = How often the software triggers the sensor to receive new values (in seconds).
        """

        self.name = name
        self.device_type = device_type
        self.gpio_pins = gpio_pins
        self.i2c_device = i2c_device
        self.value_count = value_count
        self.offset = offset
        self.active = active
        self.colors = colors
        self.units = units
        self.update_interval = update_interval
