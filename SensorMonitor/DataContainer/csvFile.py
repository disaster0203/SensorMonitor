from csv import writer
from SensorMonitor.DataContainer.valueTimestampTuple import ValueTimestampTuple


class CSVFile:
    """Container class for sensor settings.

    The following settings are provided:
    - path: str = the name of the sensor that is displayed in the GUI.
    - file: file = the file to write to.
    - writer: writer = file writer object that does the actual writing.
    """

    def __init__(self, path: str, separator: str = ",", value_columns: int = 1):
        """Container class for sensor settings.

        The following settings are provided:
        :param path: str = the name of the sensor that is displayed in the GUI.
        :param separator: str = the column separator. Default is ','.
        :param value_columns: int = the number of different values that are delivered by the sensor at once. Default is 1.
        """

        self.path = path
        self.file = open(self.path, "w", newline='')
        self.writer = writer(self.file, delimiter=separator)
        self.columns = value_columns

        # Write headline
        columns = []
        for column in range(self.columns):
            columns.append("Value " + str(column + 1))

        columns.append("Time")
        self.writer.writerow(columns)

    def write_to_csv_file(self, value: ValueTimestampTuple):
        """Writes a new value-timestamp tuple to the file.

        :param value: ValueTimestampTuple = the tuple to write.
        """
        row_content = []
        for col in range(self.columns):
            row_content.append(value.value[0][col])
        
        row_content.append(value.timestamp)
        self.writer.writerow(row_content)

    def finish(self):
        """Closes the file after all rows are written."""

        self.file.close()
