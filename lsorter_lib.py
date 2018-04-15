try:
    import pigpio
    #import RPi.GPIO as GPIO
except ModuleNotFoundError:
    print("pigpio or RPi.GPIO can't be found.")
    on_pi = False
else:
    print("Raspi-specific modules loaded correctly.")
    on_pi = True
import time
import sys
import os
#import cv2
#import matplotlib.pyplot
#import PIL
import numpy
#import imutils
import socket
from threading import Thread
#from PIL import Image
#from imutils.video import WebcamVideoStream, FPS

print("imported modules")

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
class unipolarstepper():
    def __init__(self, pins, stepmode="full", stepperturn=2048):#stepmode = wave | full | half, pins = [blue, pink, yellow, orange] in BCM
        wavesteps = [[1, 0, 0, 0],
                     [0, 1, 0, 0],
                     [0, 0, 1, 0],
                     [0, 0, 0, 1]]
        fullsteps = [[1, 1, 0, 0],
                     [0, 1, 1, 0],
                     [0, 0, 1, 1],
                     [1, 0, 0, 1]]
        halfsteps = [[1, 0, 0, 0],
                     [1, 1, 0, 0],
                     [0, 1, 0, 0],
                     [0, 1, 1, 0],
                     [0, 0, 1, 0],
                     [0, 0, 1, 1],
                     [0, 0, 0, 1],
                     [1, 0, 0, 1]]
        if stepmode == "wave":
            self.stepdata = wavesteps
        elif stepmode == "full":
            self.stepdata = fullsteps
        elif stepmode == "half":
            self.stepdata = halfsteps
        else:
            raise ValueError("You have to set stepmode to wave or full or half!")

        self.stepmode = stepmode
        if on_pi:
            for pin in pins:
                pi.set_mode(pin, pigpio.OUTPUT)
        else:
            print("[would setup pins {} to GPIO.out if there are pins]".format(pins))
        self.pins = pins
        self.stepperturn = stepperturn
        self.stepout(0)
    def stepout(self, step):
        #if self.stepmode == "wave":
        #    pi.write(self.pins[(step+1 if dir else step-1)], 0)
        #    pi.write(self.pins[step], 1)
        if on_pi:
            for p in range(4):
                pi.write(self.pins[p], self.stepdata[step][p])
        else:
            print("[would set pins {} to step {} ({}) if there are pins]".format(self.pins, step, self.stepdata[step]))
        self.step = step
    def makestep(self, dir=True, verbose=True):
        st = (self.step - 1 if not dir else self.step + 1)
        if not verbose:
            print("st before: {}".format(st))
        if self.stepmode == "half":
            if st == -1:
                st = 7
            elif st == 8:
                st = 0
        elif st == -1:
            st = 3
        elif st == 4:
            st = 0
        if not verbose:
            print("st after: {}".format(st))
        self.stepout(st)
    def drive_rpm(self, rpm, dir = True):
        """if rpm<0 rpm means sleep between steps"""
        self.drivethread = Thread(target=self._drive_thread, args=(rpm, dir))
        self.thread_is_driving = True
        self.drivethread.start()
    def stop_driving(self):
        self.thread_is_driving = False
    def _drive_thread(self, rpm, dir):
        if rpm>0:
            drivepersleep = True
            sleep = 1/self.stepperturn*rpm
        else:
            drivepersleep = False
            sleep = -rpm
        print("started d_drive_thread with rpm={}, sleep={} and drivepersleep={}".format(rpm, sleep, drivepersleep))
        donesteps = 0
        starttime = time.perf_counter()
        nexttime = starttime + sleep
        while self.thread_is_driving:
            self.makestep(dir)
            time.sleep(sleep)
class Coordinator():
    def __init__(self, **kwargs):
        self.so = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.si = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.si.bind(("localhost", 54321))
        #self.belt = unipolarstepper([17, 27, 22, 10])
        self.slide = slideturner(4)
    def start(self):
        #self.belt.drive_rpm(0)
        self.slide.goto_box(0, False, verbose=False, delay=0)
        while True:
            self.so.sendto(b"wait", ("localhost", 12345))
            print("sent request.")
            color = self.si.recv(1024)
            delay = float(self.si.recv(1024))
            if color.decode() == "Red":
                self.slide.goto_box(0, False, verbose=False, delay=delay)
            elif color.decode() == "Green":
                self.slide.goto_box(1, False, verbose=False, delay=delay)
            elif color.decode() == "Blue":
                self.slide.goto_box(2, False, verbose=False, delay=delay)
            elif color.decode() == "Yellow":
                self.slide.goto_box(3, False, verbose=False, delay=delay)
            print(color, delay)

print("Initalised classes.")
Coordinator().start()