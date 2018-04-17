#!/usr/bin/python3
#for python 3 on raspberry pi
import time
import socket
import sys
import numpy
import pickle
from argparse import ArgumentParser
import pigpio

aparser = ArgumentParser(description = "script to analyse webcam images")
aparser.add_argument("-i", "--rx-ip", dest = "rxip", metavar = "RX IP", type = str, help = "IP Address of the webcam reader", default = "127.0.0.1")
aparser.add_argument("-k", "--tx-ip", dest = "txip", metavar = "TX IP", type = str, help = "IP Address of the central", default = "127.0.0.1")
aparser.add_argument("-t", "--tx-port", dest = "txport", metavar = "TX Port", type = int, help = "Port to send the colors (Default 50003)", default = 50003)
aparser.add_argument("-r", "--rx-port", dest = "rxport", metavar = "RX Port", type = int, help = "Port to receive images (Default 50001)", default = 50001)
args = aparser.parse_args()

txsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
txaddr = (args.txip, args.txport)
rxsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
rxsock.bind((args.rxip, args.rxport))

def measure_fps(num_frames = 100):
	start = time.perf_counter()
	for f in range(num_frames):
		txsock.sendto("allrows".encode("utf-8"), txaddr)
		data = "".encode("utf-8")
		datas = []
		while data.decode("utf-8") != "finish":
			data, addr = rxsock.recvfrom(1024)
			datas.append(pickle.loads(data.decode("utf-8")))
		print(f, len(datas))
	stop = time.perf_counter()
	print("Total time: {}s\tTime per frame:{}s\tFPS:{}s".format(stop-start, (stop-start)/num_frames, num_frames/(stop-start)))