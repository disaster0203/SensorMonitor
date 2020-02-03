from csv import writer
from SensorMonitor.DataContainer.valueTimestampTuple import ValueTimestampTuple


class CSVFile:
    """Container class for sensor settings.

    The following settings are provided:
    - path: str = the name of the sensor that is displayed in the GUI.
    - file: file = the file to write to.
    - writer: writer = file writer object that does the actual writing.
    """

    def __init__(self, path: str, separator: str = ","):
        """Container class for sensor settings.

        The following settings are provided:
        :param path: str = the name of the sensor that is displayed in the GUI.
        :param separator: str = the column separator. Default is ','.
        """

        self.path = path
        self.file = open(self.path, "w", newline='')
        self.writer = writer(self.file, delimiter=separator)
        # Write headline
        self.writer.writerow(["Value", "Time"])

    def write(self, value: ValueTimestampTuple):
        """Writes a new value-timestamp tuple to the file.

        :param value: ValueTimestampTuple = the tuple to write.
        """

        self.writer.writerow([value.value, value.timestamp])

    def finish(self):
        """Closes the file after all rows are written."""

        self.file.close()
