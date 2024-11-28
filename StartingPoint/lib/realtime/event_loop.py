from lib.controller import Controller
from lib.realtime.realtime import WallClock, AbstractRealTimeSimulation
import time
import abc

class AbstractEventLoop:
    # delay in nanoseconds
    # should be non-blocking
    # should return timer ID
    @abc.abstractmethod
    def schedule(self, delay, callback):
        pass

    @abc.abstractmethod
    def cancel(self, timer_id):
        pass

# Runs virtual (simulated) time as close as possible to (scaled) wall-clock time.
# Depending on how fast your computer is, simulated time will always run a tiny bit behind wall-clock time, but this error will NOT grow over time.
class EventLoopRealTimeSimulation(AbstractRealTimeSimulation):

    def __init__(self, controller: Controller, event_loop: AbstractEventLoop, wall_clock: WallClock, termination_condition=lambda: False, time_advance_callback=lambda simtime:None):
        self.controller = controller
        self.event_loop = event_loop

        self.wall_clock = wall_clock

        self.termination_condition = termination_condition

        # Just a callback indicating that the current simulated time has changed.
        # Can be useful for displaying the simulated time in a GUI or something
        self.time_advance_callback = time_advance_callback

        # At most one timer will be scheduled at the same time
        self.scheduled_id = None

    def poke(self):
        if self.scheduled_id is not None:
            self.event_loop.cancel(self.scheduled_id)

        self.controller.run_until(self.wall_clock.time_since_start()) # this call may actually consume some time

        self.time_advance_callback(self.controller.simulated_time)

        if self.termination_condition():
            print("Termination condition satisfied. Stop mainloop.")
            return

        if self.controller.have_event():
            # schedule next wakeup
            sleep_duration = self.wall_clock.sleep_duration_until(self.controller.get_earliest())
            self.scheduled_id = self.event_loop.schedule(sleep_duration, self.poke)
            # print("sleeping for", pretty_time(sleep_duration))
        else:
            # print("sleeping until woken up")
            pass

    # generate input event at the current wall clock time
    # this method should be used for generating events that represent e.g., button clicks, key presses
    def add_input_now(self, sc, event, value=None):
        self.controller.add_input(sc, event, timestamp=self.wall_clock.time_since_start(), value=value)
        self.poke()

    # for events that need to happen immediately, at the current point in simulated time
    def add_input_sync(self, sc, event, value=None):
        self.controller.add_input_relative(sc, event, value=value)
        self.poke()
