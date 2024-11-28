from lib.realtime.event_loop import AbstractEventLoop

# schedules calls in an existing tkinter eventloop
class TkEventLoopAdapter(AbstractEventLoop):
    def __init__(self, tk):
        self.tk = tk

    def schedule(self, delay, callback):
        return self.tk.after(int(delay / 1000000), # ns to ms
            callback)

    def cancel(self, timer):
        self.tk.after_cancel(timer)
