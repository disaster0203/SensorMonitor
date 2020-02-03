import threading
import time
from queue import Queue
from datetime import datetime


class TimeWorker:
    """Worker class that contains a thread that continuously delivers timestamps."""

    def __init__(self, queue: Queue, update_interval: float = 0.5):
        """Initializes the TimeWorker

        :param queue: Queue = the queue to communicate with the gui thread.
        :param update_interval: float = the time in seconds between two new timestamps.
        """

        self._queue = queue
        self._update_interval = update_interval
        self._run = False
        self._time_thread = None
        self._time_to_run = None

    def is_running(self) -> bool:
        """Returns whether the thread is currently running or not.

        :return True if the thread is running, False otherwise.
        """

        return self._run

    def start(self, time_to_run=0):
        """Starts the thread. If it is already running nothing happens."""

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
        """Stops the thread. If it is already stopped nothing happens."""

        if not self._run:
            return  # is already paused

        self._run = False
        self._time_thread.join()

    def _thread_function_upcounting(self):
        """The function that actually runs inside the thread. It counts from zero upwards."""

        run_time = datetime.now()
        while self._run:
            delta = datetime.now() - run_time
            self._queue.put(delta.seconds)
            time.sleep(self._update_interval)

    def _thread_function_downcounting(self, time_to_run):
        """The function that actually runs inside the thread. It counts from a given time downwards and stops
        automatically after reaching zero.

        :param time_to_run: float = the time this thread should run in seconds.
        """

        run_time = datetime.now()
        while self._run:
            delta = time_to_run - (datetime.now() - run_time).total_seconds()
            if delta <= 0.0:
                self._run = False
                self._queue.put(None)
            else:
                self._queue.put(delta)
                time.sleep(self._update_interval)
