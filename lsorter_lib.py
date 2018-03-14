import pigpio, time, sys, os
import RPi.GPIO as GPIO

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
    def init(self, pins, stepmode="full", stepperturn = 2048):#stepmode = wave | full | half, pins = [blue, pink, yellow, orange] in BCM
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

        for pin in pins:
            GPIO.setup(pin, GPIO.OUT)
        self.pins = pins
        self.stepperturn = stepperturn
        self.stepout(0)
    def stepout(self, step):
        dat = self.stepdata[step]
        for p in range(4):
            GPIO.output(self.pins[p], dat[p])
        self.step = step
    def makestep(self, dir=True):#dir False | True -> forward | backward
        step = (self.step-1 if not dir else self.step+1)
        if self.stepmode == "wave" or self.stepmode == "full":
            if step == 4:
                step = 0
            elif step == -1:
                step = 3
        else:#self.stepmode == "half"
            if step == 8:
                step = 0
            elif step == -1:
                step = 7
        self.stepout(step)
