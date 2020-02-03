import time
import threading
from queue import Queue
from datetime import datetime
from typing import List
import SensorMonitor.DataContainer.converterFunctions as Converter
from SensorMonitor.DataContainer.valueTimestampTuple import ValueTimestampTuple
from SensorMonitor.DataContainer.gpio import GPIO
from SensorMonitor.Manager.ads1256 import ADS1256


class GpioWorker:
    """Worker class that contains a thread that can be used to access gpio sensor values."""

    def __init__(self, device_type: str, gpio: List[GPIO], queue: Queue, update_interval: float = 0.5):
        """Initializes the SensorValuesWorker

        :param device_type: str = the type of the sensor.
        :param gpio: List[GPIO] = the GPIO pins of the sensor plus their mode.
        :param queue: Queue = the queue to communicate with the gui thread.
        :param update_interval: float = the time in seconds between two new values.
        """

        self._converter_function = Converter.get_converter_function(device_type)
        self._gpio = gpio
        self._queue = queue
        self._update_interval = update_interval
        self._run = False
        self._sensor_thread = None
        self.ADC = None

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

        self.ADC = ADS1256()
        self.ADC.ads1256_init()

        self._run = True
        self._sensor_thread = threading.Thread(target=self._thread_function)
        self._sensor_thread.start()

    def stop(self):
        """Stops the thread. If it is already stopped nothing happens."""

        if not self._run:
            return  # is already paused

        self._run = False
        self._sensor_thread.join()

    def _thread_function(self):
        """The function that actually runs inside the thread. It creates random float numbers each '_update_interval'
        and puts them together with a timestamp into a queue."""

        while self._run:
            # Collect value from the input gpio pin
            value = -1
            for gpio in self._gpio:
                if gpio.mode == "IN":
                    value = self.ADC.ads1256_get_channel_value_in_volt(gpio.pin_nr)
                    if self._converter_function is not None:
                        value = self._converter_function(value)
                    break

            # Put value in queue so that other threads can receive it
            self._queue.put(ValueTimestampTuple([value], datetime.now().strftime("%d.%m.%Y-%H:%M:%S")))
            time.sleep(self._update_interval)
