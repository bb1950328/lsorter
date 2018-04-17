#!/usr/bin/python3
#for python 3 on raspberry pi
import time
import os
import socket
import sys
import numpy
import pickle
from argparse import ArgumentParser
import pigpio

aparser = ArgumentParser(description = "script to control a servo via UDP")
aparser.add_argument("-p", "--servo-pin", dest = "pin", metavar = "Servo pin", type = int, help = "Which BCM GPIO pin device to use (Default 4)", default = 4)
aparser.add_argument("-i", "--ip", dest = "ip", metavar = "IP", type = str, help = "IP Address of the controller", default = "127.0.0.1")
aparser.add_argument("-r", "--rx-port", dest = "rxport", metavar = "RX Port", type = int, help = "Port to receive commands (Default 50004)", default = 50004)
args = aparser.parse_args()

try:
    pi = pigpio.pi()
except:#when daemon isn't running
    os.system("sudo pigpiod")
    pi = pigpio.pi()

class slideturner():
    def __init__(self, num_boxes, min_servo=675, max_servo=2350, pin=4):
        self.num_boxes = num_boxes
        self.min_servo, self.max_servo = min_servo, max_servo
        self.pin = pin
        if num_boxes < 1:
            raise ValueError("You must init at least one box")
        if on_pi:
            pi.set_mode(pin, pigpio.OUTPUT)
            print("setmode")
        else:
            print("[would setup pin {} to servo if there are pins]".format(pin))
    def calc_pulse(self, box, verbose=True):#box is from 0 to self.num_boxes-1
        angle = 180/self.num_boxes * (box+0.5)
        pulse = (angle/180*(self.max_servo - self.min_servo)) + self.min_servo
        if not verbose:
            print("Angle:", angle, "\tPulselength:", pulse)
        return pulse
    def goto_box(self, box, really_delay, verbose=True, delay=0):
        if delay:
            self.thread = Thread(target=self.goto_box, args=(box, delay))
            self.thread.start()
            return
        if really_delay:
            time.sleep(really_delay)
        self.box = box
        pulse = self.calc_pulse(box, verbose=verbose)
        if on_pi:
            
            pi.set_servo_pulsewidth(self.pin, pulse)
            print("setservo")
        else:
            print("[would set servo to {}ms if there's a servo.]".format(pulse))

slide = slideturner(args.pin)
self.slide.goto_box(0, False, verbose=False, delay=0)
rxsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
rxsock.bind((args.ip, args.rxport))
r = ""
try:
	while True:
		r = rxsock.recv(1024)
		if r == "num_slides":
			pass
		#TODO: if r=="kjgrewlkgdrhnsög"

