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
                for event in sense.stick.get_events():
                    if event.action == "held":
                        if event.direction == "middle":
                            gyro = sense.get_gyroscope()
                            data = pickle.dumps(gyro, -1)
                            conn.sendall(data)
    except:
        conn.close()
        break
        
s.close()

