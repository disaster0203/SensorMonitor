class Sensor:
    """Container class for sensor settings.

        The following settings are provided:
        :param name: str = the name of the sensor that is displayed in the GUI.
        :param gpio_pin: int = the GPIO pin this sensor uses. Needed to access the sensor.
        :param offset: float = calibration value that will be added to each received sensor value.
        :param active: bool = whether the sensor is active or not. If it is inactive no data will be recorded.
        :param color: str = The graph color of this sensor. It only accepts hex color values (e.g. #FF0000 for Red)
        :param unit: str = The SI unit of the sensor values. This is only used for displaying in the GUI and can also
                           be an empty string ("") if the unit is unknown or does not exist.
        """

    def __init__(self, name: str, gpio_pin: int, offset: float, active: bool, color: str, unit: str):
        """Initializes this class and stores the given values in their corresponding fields.

        :param name: str = the name of the sensor that is displayed in the GUI.
        :param gpio_pin: int = the GPIO pin this sensor uses. Needed to access the sensor.
        :param offset: float = calibration value that will be added to each received sensor value.
        :param active: bool = whether the sensor is active or not. If it is inactive no data will be recorded.
        :param color: str = The graph color of this sensor. It only accepts hex color values (e.g. #FF0000 for Red)
        :param unit: str = The SI unit of the sensor values. This is only used for displaying in the GUI and can also
                           be an empty string ("") if the unit is unknown or does not exist.
        """

        self.name = name
        self.gpioPin = gpio_pin
        self.offset = offset
        self.active = active
        self.color = color
        self.unit = unit
