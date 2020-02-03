from SensorMonitor.Manager.jsonManager import JsonManager


@JsonManager.register
class I2CDevice:
    """ Container class for I2C settings.

    :param bus: int = The bus to use.
    """

    def __init__(self, bus: int = -1):
        """Initializes this class and stores the given values in their corresponding fields.

        :param bus: int = The bus to use.
        """

        self.bus = bus
