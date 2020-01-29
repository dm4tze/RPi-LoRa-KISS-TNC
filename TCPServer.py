#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

RECV_BUFFER_LENGTH	= 1024

from threading import Thread
import socket
from kiss import SerialParser

def logf(message):
	import sys
	print(message, file=sys.stderr)

class KissServer(Thread):
		'''TCP Server to be connected by the APRS digipeater'''
		def __init__(self, host, port, tx_queue=None):
			Thread.__init__(self)
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.socket.bind((host, port))
			self.socket.listen(1)
			self.data = str()
			self.tx_queue = tx_queue
			self.connection = None
		def run(self):
			parser = SerialParser(self.queue_frame)
			while True:
				self.connection = None
				self.connection, client_address = self.socket.accept()
				parser.reset()
				logf("KISS-Server: Connection from %s" % client_address[0])
				while True:
					data = self.connection.recv(RECV_BUFFER_LENGTH)
					if data:
						parser.parse(data)
					else:
						self.connection.close()
						break
		def queue_frame(self, frame):
			self.tx_queue.put(frame, block=False)
		def __del__(self):
			self.socket.shutdown()
		def send(self, data):
			if self.connection:
				self.connection.sendall(data)


if __name__ == '__main__':
		'''Test program'''
		import time
		from multiprocessing import Queue

		TCP_HOST = "0.0.0.0"
		TCP_PORT = 10001

		# frames to be sent go here
		KissQueue = Queue()

		server = KissServer(TCP_HOST, TCP_PORT, KissQueue)
		server.setDaemon(True)
		server.start()

		while True:
			#server.send("\xc0\x00\x82\xa0\xa4\xa6@@`\x9e\x8ar\xa8\x96\x90q\x03\xf0!4725.51N/00939.86E[322/002/A=001306 Batt=3.99V\xc0")
			data = KissQueue.get()
			print("Received KISS frame:" + repr(data))



