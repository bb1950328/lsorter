#THIS IS FOR PYTHON 2.7!!!
import time
import cv2
#import PIL
#import numpy
#import imutils
import socket
#from threading import Thread
from imutils.video import WebcamVideoStream, FPS

class WebcamAnalyser():
    def __init__(self, camport = 0):
        self.camport = camport
        self.vstream = WebcamVideoStream(src=0).start()
        self.fps = FPS().start()
    def capture_img(self, cam):
        return self.vstream.read()
    def diffImg(self, t0, t1, t2):
        d1 = cv2.absdiff(t2, t1)
        d2 = cv2.absdiff(t1, t0)
        return cv2.bitwise_and(d1, d2)
    def wait_for_brick(self, cam=0, treshold=10000):
        t_minus = cv2.cvtColor(self.capture_img(cam), cv2.COLOR_RGB2GRAY)
        t = cv2.cvtColor(self.capture_img(cam), cv2.COLOR_RGB2GRAY)
        t_plus = cv2.cvtColor(self.capture_img(cam), cv2.COLOR_RGB2GRAY)
        while True:
            dimg=self.diffImg(t_minus, t, t_plus)
            nz = cv2.countNonZero(dimg)
            if nz > treshold:
                print (nz, "px are enough <", treshold)
                return nz
            print(nz, "px are not enough.")
            t_minus = t
            t = t_plus
            t_plus = cv2.cvtColor(self.capture_img(cam), cv2.COLOR_RGB2GRAY)
    def analyse_frame(self, frame, pxjump=4, tr=400, bt=20, ylen=640, xlen=480, x1crop=0, x2crop=0, y1crop=0, y2crop=0, show_img=False):
        "returns color (0=Red, 1=Green, 2=Blue)"
        stat= [0, 0, 0]
        #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #frame=frame[:, x1crop:-x2crop]
        if show_img:
            matplotlib.pyplot.imshow(frame)
        pxcount = 0
        for y in range(y1crop, ylen-y2crop, pxjump):
            for x in range(x1crop, xlen-x2crop, pxjump):
                #print stat
                rgb = frame[x, y]
                #print rgb
                #print
                r = rgb[2]
                g = rgb[1]
                b = rgb[0]
                if (r-bt>= g) and (r-bt>= b):# and sum(rgb)>200:
                    stat[0] +=1
                elif (g-bt>= r) and (g-bt>= b):
                    stat[1] +=1
                elif (b-bt>= r) and (b-bt>= g):
                    stat[2] +=1
                if stat[0]-tr>stat[1] and stat[0]-tr>stat[2]:
                    return "Red"
                elif stat[1]-tr>stat[0] and stat[1]-tr>stat[2]:
                    return "Green"
                elif stat[2]-tr>stat[0] and stat[2]-tr>stat[1]:
                    return "Blue"
                #if pxcount>100000:
                    #return "white"
                pxcount += 1
        r = stat[0]
        g = stat[1]
        b = stat[2]
        if r>g and r>b:
            return 0
        elif g>r and g>b:
            return 1
        else:
            return 2
    def process_frame(self, wait_on_motion=0, analyse=True, pxjump=4, tr=400, bt=30, x1crop=75, x2crop=75, save_on_desktop=False):
        "wait_on_motion = treshold num of pixels changed 0 = disable, if not analyse -> returns frame else color (0=Red, 1=Green, 2=Blue)"
        if wait_on_motion < 0:
            raise ValueError("wait_on_motion must be positive!")
        if wait_on_motion:
            self.wait_for_brick(0, treshold=wait_on_motion)
        frame = self.vstream.read()
        if save_on_desktop:
            cv2.imwrite("/home/pi/Desktop/captured.png", frame)
        if not analyse:
            return frame
        else:
            return self.analyse_frame(frame, pxjump=pxjump, tr=tr, bt=bt, x1crop=x1crop, x2crop=x2crop)
so = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
si = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
wc = WebcamAnalyser()
wait_on_motion=350000
analyse=True
pxjump=4
tr=400
bt=30
x1crop=75
x2crop=75
try:
    si.bind(("localhost", 12345))
    while True:
        data, addr = si.recvfrom(1024)
        data = data.decode()
        print "[" + str(addr) + "] has sent \"" + data + "\""
        if data == "wait":
            aw = wc.process_frame(wait_on_motion, analyse, pxjump, tr, bt, x1crop, x2crop, save_on_desktop = True)
            so.sendto(aw.encode(), ("localhost", 54321))
            print "sent back " + aw
finally:
    so.close()