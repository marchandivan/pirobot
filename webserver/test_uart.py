import serial
from time import sleep

ser = serial.Serial ("/dev/ttyAMA0", 9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)    #Open port with baud rate
while True:
    data = input("Command: ")
    ser.write(data.encode())

