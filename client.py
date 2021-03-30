from tkinter import *
import socket
import time
import _pickle as pickle


IP_ADDR = '192.168.1.13'
PORT = 9607

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((IP_ADDR, PORT))
    connected = True
except Exception:
    connected = False
    print("Server potentially not running")


times = []
getData = True
dataPoints = 0
dataP = []
data = []

while getData:
    theData = s.recv(4096)
    data.append(pickle.loads(theData))
    times.append(time.perf_counter())
    dataPoints += 1
    if dataPoints == 2:
        getData = False

delta = times[1] - times[0]
print(delta)
print(data)


