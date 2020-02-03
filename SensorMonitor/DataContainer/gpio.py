from SensorMonitor.Manager.jsonManager import JsonManager


@JsonManager.register
class GPIO:
    """ Container class for gpio settings.

    :param pin_nr: int = The gpio pin to use.
    :param mode: str = 'IN' for input mode or 'OUT' for output mode. Default is 'IN'
    """

    def __init__(self, pin_nr: int = -1, mode: str = "IN"):
        """Initializes this class and stores the given values in their corresponding fields.

        :param pin_nr: int = The gpio pin to use.
        :param mode: str = 'IN' for input mode or 'OUT' for output mode. Default is 'IN'
        """

        self.pin_nr = pin_nr
        self.mode = mode
