import tkinter
import atexit
import sys

# load generated Statechart code
from srcgen.water_level_simulator import WaterLevelSimulator
from srcgen.lock_controller import LockController
# from srcgen.solution import Solution as LockController # Teacher's solution

from lib.yakindu.rx import Observer
from lib.controller import Controller, pretty_time
from lib.tracer import Tracer, format_trace_as_python_code
from lib.yakindu_helpers import YakinduTimerServiceAdapter, CallbackObserver, trace_output_events
from lib.realtime.realtime import WallClock
from lib.realtime.event_loop import EventLoopRealTimeSimulation
from lib.realtime.tk_event_loop import TkEventLoopAdapter

from gui import GUI

if __name__ == "__main__":

    # read time scale from command line
    try:
        time_scale = float(sys.argv[1])
    except:
        time_scale = 1.0
    print(f"TIME SCALE is {time_scale}")


    sc = LockController()
    wlvlsc = WaterLevelSimulator() # our environment is also modeled as a statechart :)

    controller = Controller()

    # We'll record input and output events
    tracer = Tracer()
    controller.input_tracers.append((sc, tracer.record_input_event))
    trace_output_events(controller, sc, callback=tracer.record_output_event)

    sc.timer_service = YakinduTimerServiceAdapter(controller)
    wlvlsc.timer_service = YakinduTimerServiceAdapter(controller)

    toplevel = tkinter.Tk()

    wall_clock = WallClock(time_scale)
    sim = EventLoopRealTimeSimulation(controller, TkEventLoopAdapter(toplevel), wall_clock)

    gui = GUI(sim, sc, wlvlsc, toplevel)

    sim.time_advance_callback = gui.time_changed

    # output event handlers of LockController
    sc.set_request_pending_observable.subscribe(CallbackObserver(gui.set_request_pending))
    sc.open_flow_observable.subscribe(CallbackObserver(lambda side: gui.set_flow(side, True)))
    sc.close_flow_observable.subscribe(CallbackObserver(lambda side: gui.set_flow(side, False)))
    sc.open_doors_observable.subscribe(CallbackObserver(lambda side: gui.set_doors(side, True)))
    sc.close_doors_observable.subscribe(CallbackObserver(lambda side: gui.set_doors(side, False)))
    sc.green_light_observable.subscribe(CallbackObserver(gui.set_green_light))
    sc.red_light_observable.subscribe(CallbackObserver(gui.set_red_light))
    sc.set_sensor_broken_observable.subscribe(CallbackObserver(gui.set_sensor_broken))

    # output event handlers of WaterLevelSimulator
    wlvlsc.sensor_reading_observable.subscribe(CallbackObserver(gui.on_water_level_reading))
    wlvlsc.real_water_level_observable.subscribe(CallbackObserver(gui.on_real_water_level))

    def print_trace_on_exit():
        print("End of simulation. Full I/O trace:")
        print("{")
        print('    "name": "interactive",')
        print('    "input_events": ', end='')
        print(format_trace_as_python_code(tracer.input_events, indent=4))
        print('    "output_events": ', end='')
        print(format_trace_as_python_code(tracer.output_events, indent=4))
        print("}")
    atexit.register(print_trace_on_exit)

    wall_clock.record_start_time() # start_time is NOW!

    # Enter default states
    sc.enter()
    wlvlsc.enter()

    sim.poke() # schedule first simulator wakeup (in tk event loop)
    toplevel.mainloop() # everything is controlled by tkinter's eventloop
