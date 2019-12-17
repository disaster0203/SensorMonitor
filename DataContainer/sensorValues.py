import sys
from typing import List


class SensorValues:
    """Container class for sensor settings.

            The following settings are provided:
            :param last_values: List[float] = the last '_history_size' values that were stored inside the class.
            :param current: float = the last value that was stored inside the class. Is the same like the last
                                    element in last_values.
            :param max: float = the maximum value that was stored inside the class since the start of the
                                measurement.
            :param min: float = the minimum value that was stored inside the class since the start of the
                                measurement.
            :param avg: float = the average of all values that were stored inside the class since the start of
                                the measurement.
            :param sum: float = the sum of all values that were stored inside the class since the start of
                                the measurement. This is used for the calculation of the average value.
            :param value_count: int = the number of values that were stored inside the class since the start of
                                      the measurement. This is used for the calculation of the average value.
            :param timestamp: str = the time that the last value was stored inside the class. It has the format
                                    Day.Month.Year-Hour:Minute:Second (17.12.2019-16:51:28).
            :param _history_size: int = private variable that defines the maximum size of last_values.
            """

    def __init__(self, history_size: int = 100):
        """Initializes this class and sets all variables to initial default values.

        :param history_size: int = the maximum size of last_values. Default is 100.
        """
        self.last_values = []
        self.current = 0
        self.max = -sys.maxsize - 1
        self.min = sys.maxsize
        self.avg = 0
        self.sum = 0
        self.value_count = 0
        self.timestamp = ""
        self._history_size = history_size

    def add_new_value(self, new_value, timestamp):
        """Adds a new current value to the class. This will recalculate max, min, avg, sum and count.

        :param new_value: float = the new value to store inside the class.
        :param timestamp: str = the timestamp of the new value. It has the format
                                Day.Month.Year-Hour:Minute:Second (17.12.2019-16:51:28).
        """

        self.current = new_value
        self.last_values.append(new_value)
        self.max = max(self.max, new_value)
        self.min = min(self.min, new_value)
        self.sum = self.sum + new_value
        self.value_count = self.value_count + 1
        self.avg = self.sum / self.value_count
        self.timestamp = timestamp
        # If the list is too long, create a sublist by removing elements from the start
        if len(self.last_values) > self._history_size:
            self.last_values = self.last_values[len(self.last_values) - self._history_size:]

    def clear_values(self):
        """Resets this class by clearing the list of last values and setting all variables back
        to their default value."""

        self.last_values = []
        self.current = 0
        self.max = -sys.maxsize - 1
        self.min = sys.maxsize
        self.avg = 0
        self.sum = 0
        self.value_count = 0
        self.timestamp = ""
