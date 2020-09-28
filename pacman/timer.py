import pygame




class TimerManager:
    def __init__(self):
        self.timers = {}

    def add_timer(self, key, countdown_time, start_immediately_yn, tag):
        self.timers[key] = Timer(countdown_time, start_immediately_yn, tag)

    def remove_timer(self, key):
        del self.timers[key]

    def remove_elapsed_timers(self):
        for key, val in self.timers.items():
            if val.get_state() == "elapsed":
                del self.timers[key]

    def get_elapsed_timers(self):
        elapsed_timers = {}
        for key, val in self.timers.items():
            if val.get_state() == "elapsed":
                elapsed_timers[key] = val

        return elapsed_timers

    def start_all(self):
        for key, val in self.timers.items():
            val.start()

    def stop_all(self):
        for key, val in self.timers.items():
            val.stop()

    def reset_all(self):
        for key, val in self.timers.items():
            val.reset()


class Timer:
    def __init__(self, countdown_time, start_immediately_yn, tag):
        self._running = False
        self._original_countdown_time = countdown_time
        self._time_remaining = countdown_time
        self._end_time = 0
        self._start_time = 0
        self.tag = tag
        if start_immediately_yn:
            self.start()

    def get_state(self):
        tr = self.get_time_remaining()
        if self._running and tr > 0:
            return "running"
        elif self._running and tr <= 0:
            return "elapsed"
        else:
            return "stopped"

    def set_countdown_time(self, countdown_time):
        self._original_countdown_time = countdown_time
        self._time_remaining = countdown_time
        if self._running:
            self.start()

    def _update_time_remaining(self):
        if self._running:
            t = pygame.time.get_ticks()
            if t < self._end_time:
                self._time_remaining = self._end_time - t
            else:
                self._time_remaining = 0

    def reset(self):
        self._time_remaining = self._original_countdown_time

    def start(self):
        self._start_time = pygame.time.get_ticks()
        self._end_time = self._start_time + self._time_remaining
        self._running = True

    def stop(self):
        self._update_time_remaining()
        self._running = False

    def get_time_remaining(self):
        self._update_time_remaining()
        return self._time_remaining

    def get_elapsed_time(self):
        return pygame.time.get_ticks() - self._start_time


