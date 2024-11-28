# Author: Joeri Exelmans

class QueueEntry:
    __slots__ = ('timestamp', 'raise_method', 'value', 'canceled', 'event_name') # For MAXIMUM performance :)

    def __init__(self, timestamp, raise_method, value, event_name):
        self.timestamp = timestamp
        self.raise_method = raise_method
        self.value = value
        self.event_name = event_name # name of the event - only needed for debugging
        self.canceled = False

    def __repr__(self):
        return f"({self.timestamp}, {self.event_name}, {self.value})"

# The main primitive for discrete event simulation.
# An event queue / event loop, using virtualized (simulated) time, independent of wall clock time.
class Controller:
    def __init__(self):
        self.event_queue = []
        self.simulated_time = 0
        self.input_tracers = []

    # timestamp = absolute value, in simulated time (since beginning of simulation)
    def add_input(self, sc, event_name, timestamp, value=None):
        if '.' in event_name:
            interface, short_event_name = event_name.split('.')
            raise_method = getattr(getattr(sc, interface), 'raise_' + short_event_name)
        else:
            raise_method = getattr(sc, 'raise_' + event_name)
        self.add_input_lowlevel(timestamp, raise_method, value, event_name)

    # time_offset = relative to current simulated time
    def add_input_relative(self, sc, event_name, time_offset=0, value=None):
        timestamp = self.simulated_time + time_offset
        return self.add_input(sc, event_name, timestamp, value)

    def add_input_lowlevel(self, timestamp, raise_method, value, event_name):
        e = QueueEntry(timestamp, raise_method, value, event_name)
        self.event_queue.append(e)
        # important to use a stable sorting algorithm here,
        # so the order between equally-timestamped events is preserved:
        self.event_queue.sort(key = lambda entry: entry.timestamp)
        return e

    # difference here is that the added event will occur BEFORE equally-timestamped events that were already in the queue
    def add_input_lowlevel_interrupt(self, timestamp, raise_method, value, event_name):
        e = QueueEntry(timestamp, raise_method, value, event_name)
        self.event_queue.insert(0, e)
        self.event_queue.sort(key = lambda entry: entry.timestamp)
        return e

    # Runs simulation as-fast-as-possible, until 'until'-timestamp (in simulated time)
    # blocking, synchronous function
    def run_until(self, until):
        # print('running until', pretty_time(until))
        while self.have_event() and self.get_earliest() <= until:
            e = self.event_queue[0]
            for sc, tracer in self.input_tracers:
                if sc == e.raise_method.__self__:
                    tracer(e.timestamp, e.event_name, e.value)
            # e = self.event_queue.pop();
            self.event_queue = self.event_queue[1:]
            if not e.canceled:
                self.simulated_time = e.timestamp
                if e.value == None:
                    e.raise_method()
                else:
                    e.raise_method(e.value)

    def have_event(self):
        return len(self.event_queue) > 0

    def get_earliest(self):
        # return self.event_queue[-1].timestamp
        return self.event_queue[0].timestamp


def pretty_time(time_ns):
    return f'{round(time_ns / 1000000000, 3)} s'
