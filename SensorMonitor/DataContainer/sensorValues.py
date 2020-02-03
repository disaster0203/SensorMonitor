import sys


class SensorValues:
    """Container class for sensor settings.

            The following settings are provided:
            :param last_values: Lis[List[float]] = the last '_history_size' values that were stored inside the class.
            :param current: List[float] = the last values that were stored inside the class. Is the same like the last
                                    element in last_values.
            :param max: List[float] = the maximum values that were stored inside the class since the start of the
                                measurement.
            :param min: List[float] = the minimum values that were stored inside the class since the start of the
                                measurement.
            :param avg: List[float] = the average of all values that were stored inside the class since the start of
                                the measurement.
            :param sum: List[float] = the sum of all values that were stored inside the class since the start of
                                the measurement. This is used for the calculation of the average value.
            :param value_count: int = the number of values that were stored inside the class since the start of
                                      the measurement. This is used for the calculation of the average value.
            :param timestamp: str = the time that the last value was stored inside the class. It has the format
                                    Day.Month.Year-Hour:Minute:Second (17.12.2019-16:51:28).
            :param _history_size: int = private variable that defines the maximum size of last_values.
            """

    def __init__(self, history_size: int = 100, value_count: int = 1):
        """Initializes this class and sets all variables to initial default values.

        :param history_size: int = the maximum size of last_values. Default is 100.
        :param value_count: int = how many different values arrive at once. Default is 1.
        """
        self.value_count = value_count
        self.last_values = []
        self.current = []
        self.max = []
        self.min = []
        self.avg = []
        self.sum = []
        self.value_count = 0
        self.timestamp = ""
        self._history_size = history_size

        self.clear_values()

    def add_new_value(self, new_values, timestamp):
        """Adds a new current value to the class. This will recalculate max, min, avg, sum and count.

        :param new_values: List[float] = the new value to store inside the class.
        :param timestamp: str = the timestamp of the new value. It has the format
                                Day.Month.Year-Hour:Minute:Second (17.12.2019-16:51:28).
        """

        self.timestamp = timestamp
        self.value_count = self.value_count + 1

        for i, value in enumerate(new_values):
            self.current[i] = value
            self.last_values[i].append(value)
            self.max[i] = max(self.max[i], value)
            self.min[i] = min(self.min[i], value)
            self.sum[i] = self.sum[i] + value
            self.avg[i] = self.sum[i] / self.value_count
            # If the list is too long, create a sublist by removing elements from the start
            if len(self.last_values[i]) > self._history_size:
                self.last_values[i] = self.last_values[i][len(self.last_values) - self._history_size:]

    def clear_values(self):
        """Resets this class by clearing the list of last values and setting all variables back
        to their default value."""

        self.last_values = []
        self.current = []
        self.max = []
        self.min = []
        self.avg = []
        self.sum = []
        self.value_count = 0
        self.timestamp = ""

        for value in range(self.value_count):
            self.last_values.append([])
            self.max.append(-sys.maxsize - 1)
            self.min.append(sys.maxsize)
            self.avg.append(0)
            self.sum.append(0)
