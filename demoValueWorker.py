import threading
import time
import random
from datetime import datetime
from SensorMonitor.valueTimestampTuple import ValueTimestampTuple

class DemoValueWorker:
    def __init__(self, gpio, queue, update_interval=0.5):
        self._gpio = gpio
        self._queue = queue
        self._update_interval = update_interval
        self._run = False
        self._demo_thread = None

    def is_running(self):
        return self._run

    def start(self):
        # is already running
        if self._run:
            return

        self._run = True
        self._demo_thread = threading.Thread(target=self._thread_function)
        self._demo_thread.start()

    def stop(self):
        if not self._run:
            return  # is already paused

        self._run = False
        self._demo_thread.join()

    def _thread_function(self):
        while self._run:
            self._queue.put(ValueTimestampTuple(random.uniform(-3, 3), datetime.now().strftime("%d.%m.%Y-%H:%M:%S")))
            time.sleep(self._update_interval)
