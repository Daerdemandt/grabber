#!/usr/bin/env python3
from http_daemon import HTTPDaemon
from updater_daemon import UpdaterDaemon
import time, sys, os

PORT = 8000

class App(object):
	def __init__(self):
		self.http = HTTPDaemon(PORT)
		self.updater = UpdaterDaemon()
	
	def start(self):
		if not os.fork():
			self.updater.start()
		self.http.start()
	
	def stop(self):
		self.updater.stop()
		self.http.stop()
		
	def restart(self):
		self.updater.restart()
		self.http.restart()

def main():
	app = App()
	if len(sys.argv) == 2:
		if 'start' == sys.argv[1]:
			app.start()
		elif 'stop' == sys.argv[1]:
			app.stop()
		elif 'restart' == sys.argv[1]:
			app.restart()
		else:
			print("Unknown command")
			sys.exit(2)
		sys.exit(0)
	elif len(sys.argv) == 3:
		if 'http' == sys.argv[1]:
			if 'start' == sys.argv[1]:
				app.http.start()
			elif 'stop' == sys.argv[1]:
				app.http.stop()
			elif 'restart' == sys.argv[1]:
				app.http.restart()
		elif 'updater' == sys.argv[1]:
			if 'start' == sys.argv[1]:
				app.updater.start()
			elif 'stop' == sys.argv[1]:
				app.updater.stop()
			elif 'restart' == sys.argv[1]:
				app.updater.restart()
			elif 'drop-all' == sys.argv[1]:
				app.updater.drop_all_data()
			elif 'drop-old' == sys.argv[1]:
				app.updater.drop_old_data()
		else:
			print("Unknown command")
			sys.exit(2)

	else:
		print("usage: %s start|stop|restart" % sys.argv[0])
		sys.exit(2)
		
if __name__ == "__main__":
	main()

