import RPi.GPIO as GPIO
import time
import threading
from queue import Queue
from datetime import datetime
from typing import List
from SensorMonitor.DataContainer.valueTimestampTuple import ValueTimestampTuple
from SensorMonitor.DataContainer.gpio import GPIO


class SensorValuesWorker:
    """Worker class that contains a thread that can be used to access sensor values."""

    def __init__(self, gpio: List[GPIO], queue: Queue, update_interval: float = 0.5):
        """Initializes the SensorValuesWorker

        :param gpio: List[GPIO] = the GPIO pins of the sensor plus their mode.
        :param queue: Queue = the queue to communicate with the gui thread.
        :param update_interval: float = the time in seconds between two new values.
        """

        self._gpio = gpio
        self._queue = queue
        self._update_interval = update_interval
        self._run = False
        self._sensor_thread = None

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

        GPIO.setmode(GPIO.BCM)
        for gpio in self._gpio:
            if gpio.mode == "IN":
                GPIO.setup(gpio.pin_nr, GPIO.IN)
            else:
                GPIO.setup(gpio.pin_nr, GPIO.OUT)

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
            value = None
            for gpio in self._gpio:
                if gpio.mode == "IN":
                    value = GPIO.input(gpio.pin_nr)
                    break

            # Put value in queue so that other threads can receive it
            self._queue.put(ValueTimestampTuple(value, datetime.now().strftime("%d.%m.%Y-%H:%M:%S")))
            time.sleep(self._update_interval)
