from enum import Enum


class GPIOMode(Enum):
    """Enum class for GPIO modes. There are two possible modes:
    - IN for input mode.
    - OUT for output mode.
    """

    IN = "IN"
    OUT = "OUT"


class GPIO:
    """ Container class for gpio settings.

    :param pin: int = The gpio pin to use.
    :param mode: GPIOMode = IN for input mode or OUT for output mode.
    """

    def __init__(self, pin: int, mode: GPIOMode = GPIOMode.IN):
        """Initializes this class and stores the given values in their corresponding fields.

        :param pin: int = The gpio pin to use.
        :param mode: GPIOMode = IN for input mode or OUT for output mode.
        """

        self.pin_nr = pin
        self.mode = mode
