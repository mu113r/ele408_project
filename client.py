import _pickle as pickle
import socket
from tkinter import *
from tkinter import messagebox
import numpy as np
from PIL import ImageGrab
import cv2
import ctypes
import threading


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

        self.connect()

    def show_connect(self):
        self.IPLabel.grid(row=0, column=0, padx=10, pady=(10, 0), sticky=W)
        self.IPEntry.grid(row=0, column=1, padx=10, pady=(10, 0), sticky=W, columnspan=2)
        self.portLabel.grid(row=1, column=0, padx=10, pady=(10, 10), sticky=W)
        self.portEntry.grid(row=1, column=1, padx=10, pady=(10, 10), sticky=W)
        self.connectButton.grid(row=1, column=2, padx=10, pady=(10, 10), sticky=W)

    def show_draw(self):
        # Grid structure
        self.canvas.grid(row=0, column=0, pady=2, sticky=W)
        self.label.grid(row=0, column=1, pady=2, padx=2)
        self.clearButton.grid(row=1, column=0, pady=2)
        self.orientation.grid(row=1, column=1)

        # Draw lines based on mouse motion
        self.canvas.bind("<B1-Motion>", self.draw_lines)

    def clear_canvas(self):
        self.canvas.delete("all")

    def draw_lines(self, y):
        x = 300
        if y < 180:
            toPrintY = 300-10*y
            if toPrintY < 0:
                toPrintY = 0

        if y >= 180:
            toPrintY = 300 - (y - 360) * 10
            if toPrintY > 600:
                toPrintY = 600
        r = 8
        self.canvas.create_oval(x - r, toPrintY - r, x + r, toPrintY + r, fill='black')

    def update(self):
        if len(self.data_queue) != 0:
            pitch = round(self.data_queue[0]["pitch"])
            yaw = round(self.data_queue[0]["yaw"])

            result = "Pitch: " + str(pitch) + ", Yaw: " + str(yaw)
            self.orientation.config(text=result)
            self.draw_lines(pitch)

            del(self.data_queue[0])

        self.after(1, self.update)

    def connect(self):
        # IP = self.IPEntry.get()
        # port = int(self.portEntry.get())

        # FOR ME
        IP = '192.168.1.13'
        port = 9607

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
