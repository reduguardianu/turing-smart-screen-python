import logging
import time
import library.scheduler as scheduler


class InactivityChecker:
    def __init__(self, inactivity_threshold = 10, callback=None):
        self.inactivity_threshold = inactivity_threshold
        self.callback = callback
        self.last_activity_time = time.time()

    @scheduler.schedule(10)  # Check every minute
    def check_inactivity(self):
        current_time = time.time()
        if current_time - self.last_activity_time > self.inactivity_threshold:
            if self.callback is not None:
                logging.info("Inactivity threshold reached, executing callback")
                self.callback()
        self.last_activity_time = time.time()

        