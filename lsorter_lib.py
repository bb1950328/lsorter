import pigpio, time, sys, os
import RPi.GPIO as GPIO
from threading import Thread

pi = pigpio.pi()
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

class slideturner():
    def __init__(self, num_boxes, min_servo=675, max_servo=2350, pin=4):
        self.num_boxes = num_boxes
        self.min_servo, self.max_servo = min_servo, max_servo
        if num_boxes < 1:
            raise ValueError("You must init at least one box")
        pi.set_mode(pin, pigpio.OUTPUT)
    def calc_pulse(self, box, verbose=True):#box is from 0 to self.num_boxes-1
        angle = 180/self.num_boxes * (box+0.5)
        pulse = (angle/180*(self.max_servo - self.min_servo)) + self.min_servo
        if not verbose:
            print("Angle:", angle, "\nPulselength:", pulse)
        return pulse
    def goto_angle(self, box, verbose=True):
        self.box = box
        pulse = calc_pulse(box, verbose=verbose)
        pi.set_servo_pulsewidth(17, pulse)
class unipolarstepper():
    def init(self, pins, stepmode="full"):#stepmode = wave | full | half, pins = [blue, pink, yellow, orange] in BCM
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
        step = 0

        if stepmode == "wave":
            self.stepdata = wavesteps
        elif stepmode == "full":
            self.stepdata = fullsteps
        elif stepmode == "half":
            self.stepdata = halfsteps
        else:
            raise ValueError("You have to set stepmode to wave or full or half!")

        for pin in pins:
            GPIO.setup(pin, GPIO.OUT)
        self.pins = pins
        self.stepmode = stepmode
    def stepout(self, step):
        dat = self.stepdata
        for p in range(4):
            GPIO.output(self.pins[p], dat[p])
        self.step = step
    def makestep(self, dir=True):
        st = (self.step - 1 if not dir else self.step + 1)
        if self.stepmode == "half":
            if st == -1:
                st = 7
            elif st == 8:
                st = 0
        elif st == -1:
            st = 4
        elif st == 4:
            st = 0
        self.stepout(st)
    def drive_rpm(self, rpm):
        self.drivethread = Thread(target=self._drive_thread, args=(rpm))
        self.thread_is_driving = True
        self.drivethread.start()
    def stop_driving(self):
        self.thread_is_driving = False
    def _drive_thread(self, rpm):
        pass
