import time
import threading
from smbus2 import SMBus
from queue import Queue
from datetime import datetime
from SensorMonitor.DataContainer.valueTimestampTuple import ValueTimestampTuple
from SensorMonitor.Manager.bmp280 import BMP280


class BMP280Worker:
    """Worker class that contains a thread that can be used to access sensor values from the BMP280 sensor via I2C."""

    def __init__(self, queue: Queue, bus: int, update_interval: float = 0.5):
        """Initializes the SensorValuesWorker

        :param queue: Queue = the queue to communicate with the gui thread.
        :param bus: int = the bus that is used to connect with the sensor.
        :param update_interval: float = the time in seconds between two new values.
        """

        self._bus = bus
        self._queue = queue
        self._update_interval = update_interval
        self._run = False
        self._sensor_thread = None
        self._bmp280 = None

    def is_running(self) -> bool:
        """Returns whether the thread is currently running or not.

        :return True if the thread is running, False otherwise.
        """

        return self._run

    def start(self):
        """Starts the thread. If it is already running nothing happens."""

        # is already running
        if self._run:
            return

        self._bmp280 = BMP280(i2c_dev=self._bus)

        self._run = True
        self._sensor_thread = threading.Thread(target=self._thread_function)
        self._sensor_thread.start()

    def stop(self):
        """Stops the thread. If it is already stopped nothing happens."""

        if not self._run:
            return  # is already paused

        self._run = False
        self._sensor_thread.join()
        self._bmp280 = None

    def _thread_function(self):
        """The function that actually runs inside the thread. It creates random float numbers each '_update_interval'
        and puts them together with a timestamp into a queue."""

        while self._run:
            # Collect value from the input gpio pin
            values = [self._bmp280.get_temperature(), self._bmp280.get_pressure(), self._bmp280.get_altitude()]

            # Put value in queue so that other threads can receive it
            self._queue.put(ValueTimestampTuple(values, datetime.now().strftime("%d.%m.%Y-%H:%M:%S")))
            time.sleep(self._update_interval)
