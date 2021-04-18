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
import threading
import sys

#try:
#    import thread
#except ImportError:
#    import _thread as thread

sense = SenseHat()

sense.set_imu_config(True, True, True)

orientation = None

def orientation_thread():
    global orientation
    global ap
    while(True):
        orientation = sense.get_orientation_degrees()

data_thread = threading.Thread(target=orientation_thread)
data_thread.daemon = True
data_thread.start()
time.sleep(1)

# SERVER SENDING DATA
host = '192.168.1.17'
port = 9606
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
                            data = pickle.dumps(orientation, -1)
                            conn.sendall(data)
    except:
        conn.close()
        break
        
s.close()
sys.exit()

