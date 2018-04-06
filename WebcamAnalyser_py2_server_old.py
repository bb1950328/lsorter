#THIS IS FOR PYTHON 2.7!!!
from __future__ import division
import time
import cv2
#import PIL
#import numpy
#import imutils
import socket
#from threading import Thread
from imutils.video import WebcamVideoStream, FPS
import sys
import numpy
from Tkinter import *
import pickle
import colorsys
"""
R    G    B     Index   Name
(255,   0,   0)     0   Red
(  0, 100,  10)     1   Green
(  0,  35, 255)     2   Blue
(255, 255,   0)     3   Yellow
(160, 160, 160)     4   Light Gray
( 30,  30,  30)     5   Dark Gray
(  0,   0,   0)     6   Black
( 30, 100, 100)     7   White
"""
class WebcamAnalyser():
    def __init__(self, camport = 0):
        self.camport = camport
        self.vstream = WebcamVideoStream(src=0).start()
        self.fps = FPS().start()
        self.rgbcolors = numpy.array(((255,   0,   0), (  0, 100,   10), (  0,  35, 255), (255, 255,   0), (160, 160, 160), ( 30,  30,  30), (  0,   0,   0), (30, 100, 100)))
        self.wordcolors = ["Red", "Green", "Blue", "Yellow", "Light Gray", "Dark Gray", "Black", "White"]
        self.rowfile = open("./captured/captured.db", "ab")
        self.isender = ImageSender()
        #self.isender.accept()
        try:
            self.tkroot = Tk()
            self.tkcanvas = Canvas(tkroot, width = 320, height=320)
            self.tkcanvas.pack()
        except:
            pass
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
                print (nz, "px are enough >", treshold)
                return nz
            print nz, "px are not enough."
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
                
                print
                print "xy: ", x, y
                rgb = frame[x, y]
                print "BGR=", rgb
                print "Stat=", stat
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
    def analyse_frame2(self, frame, ppxjump=4, tr=400, bt=20, xlen=640, ylen=480, x1crop=0, x2crop=0, y1crop=0, y2crop=0, show_img=False):
        "returns color (0=Red, 1=Green, 2=Blue)"
        stat= [0, 0, 0]
        #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #frame=frame[:, x1crop:-x2crop]
        if show_img:
            matplotlib.pyplot.imshow(frame)
        pxcount = 0
        pxjump = ppxjump
        x, y = x1crop, y1crop
        x2crop, y2crop = xlen-x2crop-1, ylen-y2crop-1
        print frame.size
        while y<y2crop:
            while x<x2crop:
                #print
                #print "xy: ", x, y
                rgb = frame[y, x]
                #print "BGR=", rgb
                #print "Stat=", stat
                #print
                r = rgb[2]
                g = rgb[1]
                b = rgb[0]
                if (g<= 50) and (b<= 50) and (r>= 60):# and sum(rgb)>200:
                    stat[0] +=1
                    print "found red px."
                    pxjump = 1
                elif (r<= 50) and (b<= 50) and (g>= 60):
                    stat[1] +=1
                    print "found green px."
                    pxjump = 1
                elif (r<= 50) and (g<= 50) and (b>= 60):
                    stat[2] +=1
                    print "found blue px."
                    pxjump = 1
                else:
                    pxjump = ppxjump
                    #print "found nothing."
                if stat[0]-tr>stat[1] and stat[0]-tr>stat[2]:
                    return "Red"
                elif stat[1]-tr>stat[0] and stat[1]-tr>stat[2]:
                    return "Green"
                elif stat[2]-tr>stat[0] and stat[2]-tr>stat[1]:
                    return "Blue"
                #if pxcount>100000:
                    #return "white"
                pxcount += 1
                x += pxjump
            x = x1crop
            y += pxjump
            print y
        print "not enough stat"
        r = stat[0]
        g = stat[1]
        b = stat[2]
        if r>g and r>b:
            return "Red"
        elif g>r and g>b:
            return "Green"
        else:
            return "Blue"
    def next_color(self, value):
        sums = []
        for i in range(8):
            s = numpy.sum(numpy.abs(value-self.rgbcolors[i]))
            sums.append(s)
        sums = numpy.array(sums)
        am = numpy.argmin(sums)
        print value, "appears to be ", am
        return am
    def analyse_firstrow(self, pxjump=4, tr=400, bt=30, x1crop=75, x2crop=75, save_on_desktop=False):
        frame = self.vstream.read()
        if save_on_desktop:
            cv2.imwrite("captured" + str(time.time()) + ".png", frame)
        stat= [0, 0, 0]
        x = x1crop
        ppxjump = pxjump
        x2crop = 640-x2crop-1
        while x < x2crop:
            rgb = frame[1, x]
            #print "BGR=", rgb
            #print "Stat=", stat
            #print
            r = rgb[2]
            g = rgb[1]
            b = rgb[0]
            if (g<= 50) and (b<= 50) and (r>= 60):# and sum(rgb)>200:
                stat[0] +=1
                print "found red px."
                pxjump = 1
            elif (r<= 50) and (b<= 50) and (g>= 60):
                stat[1] +=1
                print "found green px."
                pxjump = 1
            elif (r<= 50) and (g<= 50) and (b>= 60):
                stat[2] +=1
                print "found blue px."
                pxjump = 1
            else:
                pxjump = ppxjump
            if stat[0]-tr>stat[1] and stat[0]-tr>stat[2]:
                return "Red"
            elif stat[1]-tr>stat[0] and stat[1]-tr>stat[2]:
                return "Green"
            elif stat[2]-tr>stat[0] and stat[2]-tr>stat[1]:
                return "Blue"
            x += pxjump
        return
    def analyse_firstrow2(self, pxjump=4, tr=400, bt=30, x1crop=75, x2crop=75, save_on_desktop=False):
        frame = self.vstream.read()
        pickle.dump(frame[1], self.rowfile)
        cv2.imwrite("./captured/captured" + str(time.time()) + ".png", frame[1,])
        stat= numpy.zeros(8)
        x = x1crop
        ppxjump = pxjump
        x2crop = 640-x2crop-1
        while x < x2crop:
            stat[self.next_color(frame[1, x])] += 1
            if numpy.max(stat) >= tr:
                am = numpy.argmax(stat)
                if am != 7 and save_on_desktop:
                    cv2.imwrite("captured" + str(time.time()) + ".png", frame)
                return am
            x += 1
    def analyse_firstrow3(self, frame, pxjump=4, tr=400, bt=30, x1crop=75, x2crop=75, save_on_desktop=False):
        #stat= numpy.zeros(8)
        x = x1crop
        ppxjump = pxjump
        x2crop = 64-x2crop-1
        while x < x2crop:
            #print frame[1, x]
            r, g, b = frame[1, x]
            print x, r, g, b
            if r > 180 and g > 180 and b > 180:#white px
                x += 1
                continue
            r = r/255
            g = g/255
            b = b/255
            h, l, s = colorsys.rgb_to_hls(r, g, b)
            h, l, s = h*255, l*255, s*255
            print h, l
            f = open("black_hls.csv", "a")
            f.write(str(h)+", "+str(l)+", "+str(s)+"\n")
            f.close()
            x += 1
        return 0
    def process_frame(self, wait_on_motion=0, analyse=True, pxjump=4, tr=400, bt=30, x1crop=75, x2crop=75, save_on_desktop=False):
        "wait_on_motion = treshold num of pixels changed 0 = disable, if not analyse -> returns frame else color (0=Red, 1=Green, 2=Blue)"
        if wait_on_motion < 0:
            raise ValueError("wait_on_motion must be positive!")
        if wait_on_motion:
            self.wait_for_brick(0, treshold=wait_on_motion)
            #time.sleep(4)
        frame = self.vstream.read()
        height, width = frame.shape[:2]
        frame = cv2.resize(frame,(int(0.1*width), int(0.1*height)), interpolation=cv2.INTER_AREA)
        #self.isender.send_pickled(frame)

        cv2.imwrite("captured" + str(time.time()) + ".png", frame)
        if not analyse:
            return frame
        else:
            start = time.time()
            n = self.wordcolors[self.analyse_firstrow3(frame, pxjump=pxjump, tr=tr, bt=bt, x1crop=x1crop, x2crop=x2crop)]
            stop = time.time()
            return (n, max(0, 8.25-(stop-start)))
    def whitelog(self, n=10):
        f = open("whitelog.csv", "a")
        for i in range(10):
            frame = self.vstream.read()
            for row in frame:
                for px in row:
                    #print px
                    f.writelines(str(px[0]) + ", " + str(px[1]) +", " +  str(px[2]) + "\n")
        f.close()
class ImageSender():
    def __init__(self, addr=("", 9868)):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(addr)
        self.s.listen(1)
    def accept(self):
        self.komm, self.client_addr = self.s.accept()
    def send_pickled(self, data):
        data = pickle.dumps(data, protocol=0)
        print "sending", len(data), "bytes to", self.client_addr
        try:
            self.komm.send(data)
        except:
            self.komm.close()

so = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
si = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
wc = WebcamAnalyser()
wait_on_motion=0
analyse=True
pxjump=16
tr=5
bt=30
x1crop=8
x2crop=8
###
###
try:
    si.bind(("localhost", 12345))
    print "listening on port 12345..."
    data = "wait"
    while True:
        if data == "wait":
            c = None
            while not c:
                c, d = wc.process_frame(wait_on_motion, analyse, pxjump, tr, bt, x1crop, x2crop, save_on_desktop = True)
                print c, d
            so.sendto(c.encode(), ("localhost", 54321))
            so.sendto(str(d).encode(), ("localhost", 54321))
            print "sent back " + c, d
            time.sleep(0.1)
        data, addr = si.recvfrom(1024)
        data = data.decode()
        print "[" + str(addr) + "] has sent \"" + data + "\""
finally:
    so.close()