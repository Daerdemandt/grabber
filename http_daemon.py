#!/usr/bin/env python3
from server import run_server

from config import http_port

from generic_daemon import GenericDaemon
import sys

class HTTPDaemon(GenericDaemon):
	'''
	Runs HTTP server
	'''
	def __init__(self, port=80):
		super().__init__()
		self.port = port
	def run(self):
		run_server(self.port)
	

if __name__ == "__main__":
	daemon = HTTPDaemon(port=http_port)
	if len(sys.argv) == 2:
		if 'start' == sys.argv[1]:
			daemon.start()
		elif 'stop' == sys.argv[1]:
			daemon.stop()
		elif 'restart' == sys.argv[1]:
			daemon.restart()
		else:
			print("Unknown command")
			sys.exit(2)
		sys.exit(0)
	else:
		print("usage: %s start|stop|restart" % sys.argv[0])
		sys.exit(2)

