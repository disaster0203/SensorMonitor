import threading
import time
import random
from queue import Queue
from datetime import datetime
from SensorMonitor.DataContainer.valueTimestampTuple import ValueTimestampTuple


class DemoValueWorker:
    """Worker class that contains a thread that can be used to simulate sensors by creating random numbers."""

    def __init__(self, gpio: int, queue: Queue, update_interval: float = 0.5):
        """Initializes the DemoValueWorker

        :param gpio: int = dummy GPIO pin of a virtual sensor. Is only here to offer
                           the same interface like the real value worker.
        :param queue: Queue = the queue to communicate with the gui thread.
        :param update_interval: float = the time in seconds between two new values.
        """

        self._gpio = gpio
        self._queue = queue
        self._update_interval = update_interval
        self._run = False
        self._demo_thread = None

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

        self._run = True
        self._demo_thread = threading.Thread(target=self._thread_function)
        self._demo_thread.start()

    def stop(self):
        """Stops the thread. If it is already stopped nothing happens."""

        if not self._run:
            return  # is already paused

        self._run = False
        self._demo_thread.join()

    def _thread_function(self):
        """The function that actually runs inside the thread. It creates random float numbers each '_update_interval'
        and puts them together with a timestamp into a queue."""
        
        while self._run:
            self._queue.put(ValueTimestampTuple(random.uniform(-3, 3), datetime.now().strftime("%d.%m.%Y-%H:%M:%S")))
            time.sleep(self._update_interval)
