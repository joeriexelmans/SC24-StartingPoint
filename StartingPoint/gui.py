import tkinter
from lib.controller import pretty_time
import random

WATER_COLOR = '#1c8ce8'
SKY_COLOR = '#ffc4d4'
DOOR_COLOR = '#633f09'

TRAFFIC_LIGHT_OFF_COLOR = '#362d2d'
TRAFFIC_LIGHT_RED_COLOR = '#ff0000'
TRAFFIC_LIGHT_GREEN_COLOR = '#4be81c'

DEFAULT_WIDGET_COLOR = '#d9d9d9'

# Paints a single lock door onto canvas
class LockDoorView:
    def __init__(self, canvas, x, scale=1):
        self.canvas = canvas
        self.door_id = canvas.create_rectangle((x-10)*scale, 70*scale, (x+10)*scale, 250*scale)
        self.flow_id = canvas.create_rectangle((x-12)*scale, 220*scale, (x+12)*scale, 240*scale, outline='')

        canvas.create_oval((x-15)*scale, 10, (x+15)*scale, 54, fill='black')
        self.red_light_id = canvas.create_oval((x-10)*scale, 12, (x+10)*scale, 32, outline='')
        self.green_light_id = canvas.create_oval((x-10)*scale, 32, (x+10)*scale, 52, outline='')

        self.set_doors(open=False)
        self.set_flow(open=False)
        self.set_red_light()

    def set_doors(self, open):
        if open:
            self.canvas.itemconfig(self.door_id, fill='', outline='black', dash=(4,6))
        else:
            self.canvas.itemconfig(self.door_id, fill=DOOR_COLOR, outline='', dash=None)

    def set_flow(self, open):
        if open:
            self.canvas.itemconfig(self.flow_id, fill=WATER_COLOR)
        else:
            self.canvas.itemconfig(self.flow_id, fill='')

    def set_green_light(self):
        self.canvas.itemconfig(self.red_light_id, fill=TRAFFIC_LIGHT_OFF_COLOR)
        self.canvas.itemconfig(self.green_light_id, fill=TRAFFIC_LIGHT_GREEN_COLOR)

    def set_red_light(self):
        self.canvas.itemconfig(self.red_light_id, fill=TRAFFIC_LIGHT_RED_COLOR)
        self.canvas.itemconfig(self.green_light_id, fill=TRAFFIC_LIGHT_OFF_COLOR)

# TkInter canvas with water levels, doors
class LockView:
    def __init__(self, parent, scale=1):
        self.scale = scale
        self.canvas = tkinter.Canvas(parent, bg=SKY_COLOR, width=600*scale, height=250*scale)
        # LOW side:
        self.canvas.create_rectangle(0, 200*scale, 200*scale, 250*scale, fill=WATER_COLOR, outline='')
        # MIDDLE side:
        self.middle_rectangle_id = self.canvas.create_rectangle(200*scale, 200*scale, 400*scale, 250*scale, fill=WATER_COLOR, outline='')
        # HIGH side:
        self.canvas.create_rectangle(400*scale, 100*scale, 600*scale, 250*scale, fill=WATER_COLOR, outline='')

        self.ldoor = LockDoorView(self.canvas, 200, scale)
        self.hdoor = LockDoorView(self.canvas, 400, scale)

    def set_water_lvl(self, water_lvl):
        self.canvas.coords(self.middle_rectangle_id, 200*self.scale, (250-water_lvl/10)*self.scale, 400*self.scale, 250*self.scale)

class GUI:
    def __init__(self, sim, sc, wlvlsc, toplevel, randomseed=0):
        # to raise input events
        self.sim = sim
        self.sc = sc
        self.wlvlsc = wlvlsc

        self.rand = random.Random(randomseed) # seed

        toplevel.resizable(0,0)
        toplevel.title("Lock Simulator")

        self.lock_view = LockView(toplevel)
        self.lock_view.canvas.pack(side=tkinter.TOP)

        self.var_simtime = tkinter.StringVar()
        self.var_ldoors = tkinter.StringVar(value="CLOSED")
        self.var_hdoors = tkinter.StringVar(value="CLOSED")
        self.var_lflow = tkinter.StringVar(value="CLOSED")
        self.var_hflow = tkinter.StringVar(value="CLOSED")
        self.var_lsignal = tkinter.StringVar(value="RED")
        self.var_hsignal = tkinter.StringVar(value="RED")
        self.var_sensor = tkinter.StringVar(value="")
        self.var_real_lvl = tkinter.StringVar(value="")
        self.var_sensor_status = tkinter.StringVar(value="NO FAILURE DETECTED")

        sim_frame = tkinter.LabelFrame(toplevel, text="Environment")
        tkinter.Label(sim_frame, text="Real Water Level").grid(column=0, row=0)
        tkinter.Entry(sim_frame, state='readonly', width=8, textvariable=self.var_real_lvl, justify=tkinter.RIGHT).grid(column=1, row=0)
        tkinter.Label(sim_frame, text="cm").grid(column=2, row=0)

        tkinter.Label(sim_frame, text="Water Level Sensor").grid(column=0, row=1)
        self.entry_sensor = tkinter.Entry(sim_frame, state='readonly', width=8, textvariable=self.var_sensor, justify=tkinter.RIGHT)
        self.entry_sensor.grid(row=1, column=1)
        tkinter.Label(sim_frame, text="cm").grid(row=1, column=2)

        self.button_broken_sensor = tkinter.Button(sim_frame, text="Break Sensor",
            command=self.break_sensor, width=14)
        self.button_unbroken_sensor = tkinter.Button(sim_frame, text="Un-break Sensor",
            command=self.unbreak_sensor, width=14, state=tkinter.DISABLED)
        self.button_broken_sensor.grid(column=0, row=3, columnspan=3)
        self.button_unbroken_sensor.grid(column=0, row=4, columnspan=3)

        tkinter.Label(sim_frame, text="Simulated Time").grid(column=0, row=5)
        tkinter.Entry(sim_frame, state='readonly', width=8, textvariable=self.var_simtime, justify=tkinter.RIGHT).grid(row=5, column=1)
        tkinter.Label(sim_frame, text="s").grid(row=5, column=2)
        sim_frame.pack(side=tkinter.LEFT)

        request_frame = tkinter.LabelFrame(toplevel, text="Actions")
        self.button_obstruct = tkinter.Button(request_frame, text="Obstruct door", command=lambda: sim.add_input_now(self.sc, "door_obstructed"), width=18).pack()
        self.button_change_lvl = tkinter.Button(request_frame, command=lambda: self.sim.add_input_now(self.sc, "request_lvl_change"), width=18)
        self.button_change_lvl.pack()
        self.button_resume = tkinter.Button(request_frame, text="Resume (make sure sensor is repaired first!)",
            command=self.resume, wraplength=160, width=18, state=tkinter.DISABLED)
        self.button_resume.pack()
        request_frame.pack(side=tkinter.LEFT)

        self.set_request_pending(value=False)

        status_frame = tkinter.LabelFrame(toplevel, text="Status")
        tkinter.Label(status_frame, text="Low").grid(row=0, column=1)
        tkinter.Label(status_frame, text="High").grid(row=0, column=2)
        tkinter.Label(status_frame, text="Doors").grid(row=1, column=0)
        tkinter.Label(status_frame, text="Flow").grid(row=2, column=0)
        tkinter.Label(status_frame, text="Signal").grid(row=3, column=0)
        tkinter.Entry(status_frame, state='readonly', width=8, textvariable=self.var_ldoors).grid(row=1, column=1)
        tkinter.Entry(status_frame, state='readonly', width=8, textvariable=self.var_hdoors).grid(row=1, column=2)
        tkinter.Entry(status_frame, state='readonly', width=8, textvariable=self.var_lflow).grid(row=2, column=1)
        tkinter.Entry(status_frame, state='readonly', width=8, textvariable=self.var_hflow).grid(row=2, column=2)
        tkinter.Entry(status_frame, state='readonly', width=8, textvariable=self.var_lsignal).grid(row=3, column=1)
        tkinter.Entry(status_frame, state='readonly', width=8, textvariable=self.var_hsignal).grid(row=3, column=2)
        tkinter.Label(status_frame, text="Sensor").grid(row=4, column=0)
        tkinter.Entry(status_frame, state='readonly', width=18, textvariable=self.var_sensor_status).grid(row=4, column=1, columnspan=2)
        status_frame.pack(side=tkinter.LEFT)

    def set_doors(self, side, open):
        strval = "OPEN" if open else "CLOSED"
        if side == self.sc.LOW:
            self.var_ldoors.set(strval)
            self.lock_view.ldoor.set_doors(open)
        elif side == self.sc.HIGH:
            self.var_hdoors.set(strval)
            self.lock_view.hdoor.set_doors(open)

    def set_flow(self, side, open):
        strval = "OPEN" if open else "CLOSED"
        eventname = "open_flow" if open else "close_flow"
        self.sim.add_input_sync(self.wlvlsc, eventname, value=side)
        if side == self.sc.LOW:
            self.var_lflow.set(strval)
            self.lock_view.ldoor.set_flow(open)
        elif side == self.sc.HIGH:
            self.var_hflow.set(strval)
            self.lock_view.hdoor.set_flow(open)

    def set_green_light(self, side):
        if side == self.sc.LOW:
            self.var_lsignal.set("GREEN")
            self.lock_view.ldoor.set_green_light()
        else:
            self.var_hsignal.set("GREEN")
            self.lock_view.hdoor.set_green_light()

    def set_red_light(self, side):
        if side == self.sc.LOW:
            self.var_lsignal.set("RED")
            self.lock_view.ldoor.set_red_light()
        else:
            self.var_hsignal.set("RED")
            self.lock_view.hdoor.set_red_light()

    def break_sensor(self):
        self.sim.add_input_now(self.wlvlsc, "toggle_sensor_broken")
        self.entry_sensor.config(readonlybackground='red')
        self.button_broken_sensor.config(state=tkinter.DISABLED)
        self.button_unbroken_sensor.config(state=tkinter.NORMAL)

    def unbreak_sensor(self):
        self.sim.add_input_now(self.wlvlsc, "toggle_sensor_broken")
        self.entry_sensor.config(readonlybackground=DEFAULT_WIDGET_COLOR) # default color
        self.button_broken_sensor.config(state=tkinter.NORMAL)
        self.button_unbroken_sensor.config(state=tkinter.DISABLED)

    def resume(self):
        self.sim.add_input_now(self.sc, "resume")
        self.button_resume.config(state=tkinter.DISABLED, bg=DEFAULT_WIDGET_COLOR)
        self.var_sensor_status.set("NO FAILURE DETECTED")

    def set_request_pending(self, value):
        if value:
            self.button_change_lvl.config(state=tkinter.DISABLED, text="Change requested")
        else:
            self.button_change_lvl.config(state=tkinter.NORMAL, text="Request water lvl change")

    def on_water_level_reading(self, water_level):
        # the measured water level - can be nonsense if sensor is broken
        noisy_water_level = int(water_level + self.rand.random()*10)
        self.sim.add_input_sync(self.sc, "water_lvl", value=noisy_water_level)
        self.var_sensor.set(noisy_water_level)

    def on_real_water_level(self, water_level):
        # the actual water level
        self.var_real_lvl.set(int(water_level))
        self.lock_view.set_water_lvl(water_level)

    def set_sensor_broken(self):
        self.button_resume.config(state=tkinter.NORMAL, bg='yellow')
        self.var_sensor_status.set("FAILURE DETECTED")

    def time_changed(self, simtime):
        self.var_simtime.set(f'{simtime / 1000000000:.3f}')
