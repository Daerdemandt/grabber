#!/usr/bin/env python3
from misc import update_data
from generic_daemon import GenericDaemon

import time, sys

seconds_between_updates = 10

class UpdaterDaemon(GenericDaemon):
	'''
	Updates bet data regularily
	'''
	def run(self):
		while True:
			data = update_data()
#			print('{} entries total'.format(len(data)))
			time.sleep(seconds_between_updates)
	def drop_all_data(self):
		pass
	def drop_old_data(self):
		pass

if __name__ == "__main__":
	daemon = UpdaterDaemon()
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

