import pigpio, time, sys, os, cv2, matplotlib.pyplot, PIL, numpy, imutils
import RPi.GPIO as GPIO
from threading import Thread
from PIL import Image
from imutils.video import WebcamVideoStream, FPS

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
        pulse = self.calc_pulse(box, verbose=verbose)
        pi.set_servo_pulsewidth(17, pulse)
class unipolarstepper():
    def init(self, pins, stepmode="full", stepperturn=2048):#stepmode = wave | full | half, pins = [blue, pink, yellow, orange] in BCM
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

        for pin in pins:
            GPIO.setup(pin, GPIO.OUT)
        self.pins = pins
        self.stepmode = stepmode
        self.stepperturn = stepperturn
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
    def drive_rpm(self, rpm, dir = True):
        self.drivethread = Thread(target=self._drive_thread, args=(rpm, dir))
        self.thread_is_driving = True
        self.drivethread.start()
    def stop_driving(self):
        self.thread_is_driving = False
    def _drive_thread(self, rpm, dir):
        sleep = 1/self.stepperturn
        donesteps = 0
        starttime = time.perf_counter()
        nexttime = starttime + sleep
        while self.thread_is_driving:
            self.makestep(dir)
            donesteps += 1
            nexttime += sleep
            while time.perf_counter()<nexttime:
                time.sleep(0.001)
class WebcamAnalyser():
    def __init__(self, camport = 0):
        self.camport = camport
        self.vstream = WebcamVideoStream(src=0).start()
        self.fps = FPS().start()
    def diffImg(self, t0, t1, t2):
        d1 = cv2.absdiff(t2, t1)
        d2 = cv2.absdiff(t1, t0)
        return cv2.bitwise_and(d1, d2)
    def wait_for_brick(cam=0):
    ##winName = "Movement Indicator"
    ##cv2.namedWindow(winName)
        t_minus = cv2.cvtColor(capture_img(cam), cv2.COLOR_RGB2GRAY)
        t = cv2.cvtColor(capture_img(cam), cv2.COLOR_RGB2GRAY)
        t_plus = cv2.cvtColor(capture_img(cam), cv2.COLOR_RGB2GRAY)
        while True:
        #start = time.perf_counter()
            dimg=diffImg(t_minus, t, t_plus)
            print("M: ", cv2.countNonZero(dimg))
        # Read next image
            t_minus = t
            t = t_plus
            t_plus = cv2.cvtColor(capture_img(cam), cv2.COLOR_RGB2GRAY)
    def readframe(self, wait_on_motion=0):#wait_on_motion = treshold num of pixels changed 0 = disable
        if wait_on_motion < 0:
            raise ValueError("wait_on_motion must be positive!")
        if wait_on_motion:
