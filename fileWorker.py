import threading
import time
import datetime
import csv


class CSVFile:
    def __init__(self, path, separator=","):
        self.path = path
        self.file = open(self.path, "w", newline='')
        self.writer = csv.writer(self.file, delimiter=separator)
        # Write headline
        self.writer.writerow(["Value", "Time"])

    def write(self, value):
        self.writer.writerow([value.value, value.timestamp])

    def finish(self):
        self.file.close()


class FileWorker:
    def __init__(self, path, queues, extension, separator=","):
        self.output_path = path
        self._queues = queues
        self._files = {}
        self._extensions = extension.split(",")
        self.separator = separator
        self._run = False
        self._writer_thread = None

    def start(self):
        # is already running
        if self._run or len(self._extensions) == 0:
            return

        # create files
        if "csv" not in self._extensions and "xlsx" not in self._extensions:
            return  # Abort starting thread if no known file extension is used
        for name in self._queues:
            if "csv" in self._extensions:
                self._files[name] = {"csv": CSVFile(self.output_path + name + "__" + datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S") + ".csv",
                                                    self.separator)}
            # elif "xlsx" in self._extensions:
            #    self._files[name] = {"xlsx": open(self.output_path + datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S"), "w+")}

        # start thread
        self._run = True
        self._writer_thread = threading.Thread(target=self._thread_function)
        self._writer_thread.start()

    def stop(self):
        # is already paused
        if not self._run:
            return

        self._run = False
        self._writer_thread.join()

    def _thread_function(self):
        while self._run:
            for n, q in self._queues.items():
                if not q.empty():
                    value = q.get()
                    q.task_done()

                    if value is not None:
                        if "csv" in self._extensions:
                            self._write_csv(n, value)
            time.sleep(0.075)  # wait for 75 ms for better performance

        # After measuring stopped write remaining values into the files
        for n, q in self._queues.items():
            while not q.empty():
                value = q.get()
                q.task_done()
                self._write_csv(n, value)

        for file in self._files:
            self._files[file]["csv"].finish()

    def _write_csv(self, sensor_name, value_to_write):
        self._files[sensor_name]["csv"].write(value_to_write)

    # def _write_xlsx(self, sensor_name, value_to_write):
