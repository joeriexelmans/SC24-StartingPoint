import threading

from lib.realtime.realtime import WallClock, AbstractRealTimeSimulation
from lib.controller import Controller, pretty_time

# Runs simulation, real-time, in its own thread
#
# Typical usage:
#   thread = threading.Thread(
#      target=ThreadedRealTimeSimulation(...).mainloop,
#   )
#   thread.start()
class ThreadedRealTimeSimulation(AbstractRealTimeSimulation):
    def __init__(self, controller: Controller, wall_clock: WallClock, termination_condition = lambda: False):
        self.controller = controller
        self.wall_clock = wall_clock
        self.termination_condition = termination_condition
        self.condition = threading.Condition()

    def mainloop(self):
        while True:
            self.controller.run_until(self.wall_clock.time_since_start())
            if self.termination_condition():
                print("Termination condition satisfied. Stop mainloop.")
                return
            if self.controller.have_event():
                earliest_event_time = self.controller.get_earliest()
                sleep_duration = self.wall_clock.sleep_duration_until(earliest_event_time)
                with self.condition:
                    # print('thread sleeping for', pretty_time(sleep_duration), 'or until interrupted')
                    self.condition.wait(sleep_duration / 1000000000)
                    # print('thread woke up')
            else:
                with self.condition:
                    # print('thread sleeping until interrupted')
                    self.condition.wait()

    def add_input_now(self, sc, event, value=None):
        with self.condition:
            self.controller.add_input(sc, event,
                timestamp=self.wall_clock.time_since_start(),
                value=value)
            self.condition.notify()
