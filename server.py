#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 30 14:05:19 2021

@author: pi
"""

from sense_hat import SenseHat
import time
from tkinter import *
import socket
import _pickle as pickle

sense = SenseHat()
sense.clear()

# ONBOARD GUI
#
#class Root(Tk):
#    
#    def __init__(self):
#        super(Root, self).__init__()
#        self.geometry("250x30")
#        self.orientation = Label(self, text="Orientation:")
#        self.orientation.pack()
#        self.orient = None
#        self.counter = 0
#        
#    def update(self):
#        self.orient = sense.get_orientation()
#        pitch = round(self.orient["pitch"], 2)
#        roll = round(self.orient["roll"], 2)
#        yaw = round(self.orient["yaw"], 2)
#        
#        if self.counter == 10:
#            result = "Pitch: " + str(pitch) + ", Roll: " + str(roll) + ", Yaw: " + str(yaw)
#            self.orientation.config(text=result)
#            self.counter = 0
#        
#        self.counter += 1
#        self.after(1, self.update)
#        
#
#IMU = Root()
#IMU.update()
#IMU.mainloop()
      

# ONBOARD CONSOLE ONLY  
#while True:
#    gyro = sense.get_gyroscope()
#    orient = sense.get_orientation()
#    
#    pitch = round(gyro["pitch"], 2)
#    roll = round(gyro["roll"], 2)
#    yaw = round(gyro["yaw"], 2)
#    result = "Pitch: " + str(pitch) + ", Roll: " + str(roll) + ", Yaw: " + str(yaw)            
#    print(result)


# SERVER SENDING DATA
host = '192.168.1.13'
port = 9607
s = socket.socket()
s.bind((host, port))
s.listen(10)


while True:
    try:
        conn, addr = s.accept()
        if conn:
            print(f"Connection established, from: {addr}")
            while True:
                gyro = sense.get_gyroscope()
#                data = str(str(gyro["pitch"]) + "/" + str(gyro["yaw"]))
                data = pickle.dumps(gyro, -1)
                conn.sendall(data)
    except:
        conn.close()
        break
        
s.close()

