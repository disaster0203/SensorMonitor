import threading
import time
import datetime
from queue import Queue
from typing import Dict
from SensorMonitor.DataContainer.csvFile import CSVFile
from SensorMonitor.DataContainer.valueTimestampTuple import ValueTimestampTuple
from SensorMonitor.Manager.configManager import ConfigManager


class FileWorker:
    """Worker class that contains a thread that can be used to write csv files."""

    def __init__(self, path: str, queues: Dict[str, Queue], extension: str, separator: str = ","):
        """Initializes the FileWorker

        :param path: str = The path where all files should be created.
        :param queues: Dict[str, Queue] = a dictionary containing each active sensor as key and
                                         and a queue as value
        :param extension: str = the file types to create (separated by comma). At the moment only
                                'csv' is supported.
        :param separator: str = the column separator of the csv files.
        """
        
        self.configMng = ConfigManager()
        self.output_path = path
        self._queues = queues
        self._files = {}
        self._extensions = extension.split(",")
        self.separator = separator
        self._run = False
        self._writer_thread = None

    def is_running(self) -> bool:
        """Returns whether the thread is currently running or not.

        :return True if the thread is running, False otherwise.
        """

        return self._run

    def start(self):
        """Starts the thread. If it is already running nothing happens."""

        # is already running
        if self._run or len(self._extensions) == 0:
            return

        # create files
        if "csv" not in self._extensions and "xlsx" not in self._extensions:
            return  # Abort starting thread if no known file extension is used
        for name in self._queues:
            current_sensor = self.configMng.get_sensor_by_name(name)
            if "csv" in self._extensions:
                self._files[name] = {"csv": CSVFile(self.output_path + name + "__" + datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S") + ".csv",
                                                    self.separator, current_sensor.value_count)}
            # elif "xlsx" in self._extensions:
            #    self._files[name] = {"xlsx": open(self.output_path + datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S"), "w+")}

        # start thread
        self._run = True
        self._writer_thread = threading.Thread(target=self._thread_function)
        self._writer_thread.start()

    def stop(self):
        """Stops the thread. If it is already stopped nothing happens."""

        # is already paused
        if not self._run:
            return

        self._run = False
        self._writer_thread.join()

    def _thread_function(self):
        """The function that actually runs inside the thread. It iterates through the dictionary and listens on each queue.
        If new values arrived they are written to file. If the measurement was stopped but not all queues are empty, the
        remaining values are written to file before the thread stops."""

        while self._run:
            for n, q in self._queues.items():
                if not q.empty():
                    value = q.get()
                    q.task_done()

                    if value is not None:
                        if "csv" in self._extensions:
                            self._write_csv(n, value)
            time.sleep(0.075)  # wait for 75 ms for better performance
            value = None

        # After measuring stopped write remaining values into the files
        for n, q in self._queues.items():
            while not q.empty():
                value = q.get()
                q.task_done()
                self._write_csv(n, value)
                value = None

        for file in self._files:
            self._files[file]["csv"].finish()

    def _write_csv(self, sensor_name: str, value_to_write: ValueTimestampTuple):
        """ Writes a new row to a csv file.

        :param sensor_name: str = the name of the sensor hat got new values
        :param value_to_write: ValueTimestampTuple = the new value timestamp tuple to write to file.
        """

        self._files[sensor_name]["csv"].write_to_csv_file(value_to_write)

    # def _write_xlsx(self, sensor_name, value_to_write):
