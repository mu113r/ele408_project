import _pickle as pickle
import socket
from tkinter import *
from tkinter import messagebox
import numpy as np
from PIL import ImageGrab
import cv2
import ctypes
import threading
import time


class Root(Tk):

    def __init__(self):
        super(Root, self).__init__()
        self.title("Pictionary")
        self.orientation = Label(self, text="Orientation:")
        # self.orient = None
        # self.counter = 0
        self.socket = None
        self.data_queue = []
        self.collect = True
        self.data_collector = threading.Thread(target=self.collect_data)
        self.data_collector.daemon = True
        self.mode = None

        # self.update()

        # GUI ELEMENTS
        # Drawing canvas
        self.canvas = Canvas(self, width=600, height=600, bg="white", cursor="cross")
        self.label = Label(self, text="Draw..", font=("Helvetica", 48))
        self.clearButton = Button(self, text="Clear", command=self.clear_canvas)

        # Connection window
        self.IPEntry = Entry(self, width=25)
        self.IPLabel = Label(self, text="Enter your Raspberry Pi IP:")
        self.portEntry = Entry(self, width=10)
        self.portLabel = Label(self, text="Enter the server port:")
        self.connectButton = Button(self, text="Connect...", command=self.connect)

        # Calibration window
        self.calibrateButton = Button(self, text="Calibrate", command=self.set_mode_calibrate)
        self.calibrateDoneButton = Button(self, text="Done", command=self.set_mode_draw)
        self.avgPitchLabel = Label(self, text="Average Pitch Offset:")
        self.avgYawLabel = Label(self, text="Average Yaw Offset:")
        self.avgPitchLabelValue = Label(self)
        self.avgYawLabelValue = Label(self)
        self.pitchOffset = 0
        self.yawOffset = 0

        self.previous_pitch = None
        self.previous_yaw = None
        self.timeSinceLastDraw = time.perf_counter()

        self.connect()
        self.show_draw()

    def show_connect(self):
        self.IPLabel.grid(row=0, column=0, padx=10, pady=(10, 0), sticky=W)
        self.IPEntry.grid(row=0, column=1, padx=10, pady=(10, 0), sticky=W, columnspan=2)
        self.portLabel.grid(row=1, column=0, padx=10, pady=(10, 10), sticky=W)
        self.portEntry.grid(row=1, column=1, padx=10, pady=(10, 10), sticky=W)
        self.connectButton.grid(row=1, column=2, padx=10, pady=(10, 10), sticky=W)


    def set_mode_draw(self):
        self.mode = "draw"
        self.after_cancel(self.calibrate_timer)
        self.show_draw()
        self.update()

    def set_mode_calibrate(self):
        self.mode = "calibrate"
        self.after_cancel(self.update_timer)
        self.clear_all()
        self.show_calibrate()
        self.calibrate()

    def show_calibrate(self):
        self.avgPitchLabel.grid(row=0, column=0, padx=10, pady=10, sticky=W)
        self.avgYawLabel.grid(row=1, column=0, padx=10, pady=10, sticky=W)
        self.avgPitchLabelValue.grid(row=0, column=1, padx=10, pady=10, sticky=W)
        self.avgYawLabelValue.grid(row=1, column=1, padx=10, pady=10, sticky=W)
        self.calibrateDoneButton.grid(row=2, column=0, padx=10, pady=10, sticky=W)

    def calibrate(self):
        if len(self.data_queue) != 0:
            self.pitchCali = round(self.data_queue[0]["pitch"])
            self.yawCali= round(self.data_queue[0]["yaw"])
            self.avgPitchLabelValue.config(text=str(self.pitchCali))
            self.avgYawLabelValue.config(text=str(self.yawCali))
            del(self.data_queue[0])

        self.calibrate_timer = self.after(1, self.calibrate)


    def show_draw(self):
        # Grid structure
        self.clear_all()

        self.canvas.grid(row=0, column=0, pady=2, sticky=W, columnspan=2)
        self.label.grid(row=0, column=2, pady=2, padx=2)
        self.clearButton.grid(row=1, column=0, pady=2)
        self.orientation.grid(row=1, column=2)
        self.calibrateButton.grid(row=1, column=1, padx=10, pady=(10, 10), sticky=W)

    def clear_canvas(self):
        self.canvas.delete("all")

    def draw_lines(self, currentYaw, currentPitch):

        if time.perf_counter() - self.timeSinceLastDraw >= 0.5:
            self.previous_yaw, self.previous_pitch = None, None


        toPrintY = None
        toPrintX = None

        # Pitch is always accurate so far
        if currentPitch < 180:
            toPrintY = 300-10*currentPitch
            if toPrintY < 0:
                toPrintY = 0

        if currentPitch >= 180:
            toPrintY = 300 - (currentPitch - 360) * 10
            if toPrintY > 600:
                toPrintY = 600


        # Yaw needs calibration

        # Yaw lower bound is greater than = zero, can be one linear function
        if self.yawCali - 30 >= 0:
            toPrintX = 10*currentYaw - (abs((self.yawCali-30)) * 10)
            if toPrintX < 0:
                toPrintX = 0
        else:
            if currentYaw < self.yawCali + 35:
                toPrintX = 10*currentYaw - (abs((self.yawCali-30)) * 10)
            else:
                toPrintX = -10*(currentYaw-360+(30-self.yawCali))
        r = 16

        if toPrintX is not None and toPrintY is not None:
            # For the first time through
            if self.previous_pitch is None:
                self.previous_pitch = toPrintY
            if self.previous_yaw is None:
                self.previous_yaw = toPrintX

            self.canvas.create_line(self.previous_yaw, self.previous_pitch, toPrintX, toPrintY, width=r)

        self.previous_pitch = toPrintY
        self.previous_yaw = toPrintX

        self.timeSinceLastDraw = time.perf_counter()

    def update(self):
        if len(self.data_queue) != 0:
            current_pitch = round(self.data_queue[0]["pitch"])
            current_yaw = round(self.data_queue[0]["yaw"])

            if self.mode != "calibrate":
                result = "Pitch: " + str(current_pitch) + ", Yaw: " + str(current_yaw)
                self.orientation.config(text=result)
                self.draw_lines(current_yaw, current_pitch)
            else:
                self.calibrate()

            del(self.data_queue[0])

        self.update_timer = self.after(1, self.update)

    def connect(self):
        # IP = self.IPEntry.get()
        # port = int(self.portEntry.get())

        # FOR ME
        IP = '192.168.1.17'
        port = 9606

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((IP, port))
            connected = True
        except Exception:
            connected = False

        if connected:
            self.data_collector.start()
            self.clear_all()
            self.show_draw()
            self.update()
        else:
            print("Server Potentially not running")
            messagebox.showerror('Unable to connect', 'Is your Raspberry Pi server running on the correct port?')

    def collect_data(self):
        while self.collect:
            theData = self.socket.recv(4096)
            theData = pickle.loads(theData)
            if theData["pitch"] < 360 and theData["yaw"] < 360:
                self.data_queue.append(theData)

    def all_children(self):
        list = self.winfo_children()
        for item in list:
            if item.winfo_children():
                list.extend(item.winfo_children())
        return list

    def clear_all(self):
        widget_list = self.all_children()
        for item in widget_list:
            item.pack_forget()
            item.grid_forget()

App = Root()
App.mainloop()
