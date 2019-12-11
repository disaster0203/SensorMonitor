import threading
import time
from datetime import datetime


class TimeWorker:
    def __init__(self, update_callback, finish_callback, update_interval=0.5):
        self._update_callback = update_callback
        self._update_interval = update_interval
        self._finish_callback = finish_callback
        self._run = False
        self._time_thread = None
        self._base_time = None
        self._run_time = None
        self._time_to_run = None

    def start(self, time_to_run=0):
        # is already running
        if self._run:
            return

        self._run = True
        # If the user submitted None, simply start an upcounting thread
        if time_to_run <= 0:
            self._time_thread = threading.Thread(target=self._thread_function_upcounting)
            self._run_time = datetime.now()
            self._time_thread.start()

        # Start a downcounting thread
        else:
            self._time_thread = threading.Thread(target=self._thread_function_downcounting)
            self._base_time = time_to_run
            self._run_time = datetime.now()
            self._time_thread.start()

    def stop(self):
        if not self._run:
            return  # is already paused

        self._run = False
        self._time_thread.join()

    def _thread_function_upcounting(self):
        while self._run:
            delta = datetime.now() - self._run_time
            self._update_callback(delta.seconds)
            time.sleep(self._update_interval)

    def _thread_function_downcounting(self):
        while self._run:
            delta = self._base_time - (datetime.now() - self._run_time).total_seconds()
            if delta <= 0.0:
                self._run = False
                self._finish_callback()
            else:
                self._update_callback(delta)
                time.sleep(self._update_interval)
