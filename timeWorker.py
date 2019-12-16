import threading
import time
from datetime import datetime


class TimeWorker:
    def __init__(self, queue, update_interval=0.5):
        self._queue = queue
        self._update_interval = update_interval
        self._run = False
        self._time_thread = None
        self._time_to_run = None

    def start(self, time_to_run=0):
        # is already running
        if self._run:
            return

        self._run = True
        # If the user submitted None, simply start an upcounting thread
        if time_to_run <= 0:
            self._time_thread = threading.Thread(target=self._thread_function_upcounting)
            self._time_thread.start()

        # Start a downcounting thread
        else:
            self._time_thread = threading.Thread(target=self._thread_function_downcounting, kwargs={'time_to_run':time_to_run})
            self._time_thread.start()

    def stop(self):
        if not self._run:
            return  # is already paused

        self._run = False
        self._time_thread.join()

    def _thread_function_upcounting(self):
        run_time = datetime.now()
        while self._run:
            delta = datetime.now() - run_time
            self._queue.put(delta.seconds)
            time.sleep(self._update_interval)

    def _thread_function_downcounting(self, time_to_run):
        run_time = datetime.now()
        while self._run:
            delta = time_to_run - (datetime.now() - run_time).total_seconds()
            if delta <= 0.0:
                self._run = False
                self._queue.put(None)
            else:
                self._queue.put(delta)
                time.sleep(self._update_interval)
