import time
import abc

# Use time_scale different from 1.0 for scaled real-time execution:
#   time_scale > 1 speeds up simulation
#   0 < time_scale < 1 slows down simulation
class WallClock:
    def __init__(self, time_scale=1.0):
        self.time_scale = time_scale
        self.purposefully_behind = 0

    def record_start_time(self):
        self.start_time = time.perf_counter_ns()

    def time_since_start(self):
        time_since_start = time.perf_counter_ns() - self.start_time
        return (time_since_start * self.time_scale) + self.purposefully_behind

    def sleep_duration_until(self, earliest_event_time):
        now = self.time_since_start()
        sleep_duration = int((earliest_event_time - now) / self.time_scale)
        # sleep_duration can be negative, if the next event is in the past
        # This indicates that our computer is too slow, and cannot keep up with the simulation.
        # Like all things fate-related, we embrace this slowness, rather than fighting it:
        # We will temporarily run the simulation at a slower pace, which has the benefit of the simulation remaining responsive to user input.
        self.purposefully_behind   = min(sleep_duration, 0) # see above comment
        actual_sleep_duration      = max(sleep_duration, 0) # can never sleep less than 0
        return actual_sleep_duration

class AbstractRealTimeSimulation:
    # Generate input event at the current wall clock time (with time-scale applied, of course)
    # This method should be used for interactive simulation, for generating events that were caused by e.g., button clicks, key presses, ...
    @abc.abstractmethod
    def add_input_now(self, sc, event, value=None):
        pass
