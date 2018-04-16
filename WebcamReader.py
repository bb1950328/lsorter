#!/usr/bin/python
#for python 2.7!
from __future__ import division
import time
import socket
import sys
import numpy
import pickle
from argparse import ArgumentParser
try:
	import cv2
	from imutils.video import WebcamVideoStream, FPS
except:
	pass
print(sys.version)
aparser = ArgumentParser(description = "script to capture and send webcam images via UDP")
aparser.add_argument("-c", "--camera", dest = "camera", metavar = "Video device", type = int, help = "Which video device to use", default = 0)
aparser.add_argument("-i", "--ip", dest = "ip", metavar = "IP", type = str, help = "IP Address of the frame analyzer", default = "127.0.0.1")
aparser.add_argument("-t", "--tx-port", dest = "txport", metavar = "TX Port", type = int, help = "Port to send the images (Default 50000)", default = 50000)
aparser.add_argument("-r", "--rx-port", dest = "rxport", metavar = "RX Port", type = int, help = "Port to receive commands (Default 50001)", default = 50001)
aparser.add_argument("-p", "--predictive-capturing", dest = "pcap", metavar = "Predictive capturing", type = str, help = "En/disable predictive capturing (yes or no)", default = "yes", choices=["yes", "no"])
args = aparser.parse_args()
txsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
txaddr = (args.ip, args.txport)
rxsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
rxsock.bind((args.ip, args.rxport))
vstream = WebcamVideoStream(src=args.camera).start()
try:
	data = "capture"
    while True:
        if data == "capture":
			n = False
			while not n:
				n, img = vstream.read()
            txsock.sendto("done".encode("utf-8"), txaddr)
		elif data == "1strow":
			txsock.sendto(pickle.dumps(img[0,:]).encode("utf-8"), txaddr)
		elif data == "allrows":
			for x in range(len(img[:,0])):
				txsock.sendto(pickle.dumps(img[x,:]).encode("utf-8"), txaddr)
        data, addr = rxsock.recvfrom(1024)
        data = data.decode()
        print "[" + str(addr) + "] has sent \"" + data + "\""
except:
	pass
finally:
    txsock.close()
	rxsock.close()