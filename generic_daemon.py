#!/usr/bin/env python3
# TODO: make the whole thing threadsafe singleton, or sth like that
# This way, one can rule the same daemon using several instances of it
# or should there be multiple interfaces?

from abc import ABCMeta, abstractmethod

import sys, os, time, atexit, signal
# to get instance's filename to generate default pidfile:
from inspect import getfile 
from hashlib import md5

import sys, os, time, atexit, signal

class GenericDaemon:
	'''
	Generic daemon abstract class.
	
	Inherit from it and implement 'run' method.
	'''
	__metaclass__ = ABCMeta
	@abstractmethod
	def run():
		'''Implement this in children classes.'''

	def __init__(self, pid_file_name=None):
		if not pid_file_name:
			source_filename = getfile(self.__class__)
			child_name = self.__class__.__name__
			unique_name = '{}:{}'.format(source_filename, child_name)
			# We use md5 because if one wants collision he will get them anyway
			unique_id = md5(unique_name.encode()).hexdigest()
			pid_file_folder = '/var/run'
			pid_file_name = '{}/{}-pidfile.{}'.format(pid_file_folder, child_name, unique_id)
		assert pid_file_name
		self.pid_file_name = pid_file_name
	
	def daemonize(self):
		"""Deamonize class. UNIX double fork mechanism."""

		try: 
			pid = os.fork() 
			if pid > 0:
				# exit first parent
				sys.exit(0) 
		except OSError as err: 
			sys.stderr.write('fork #1 failed: {0}\n'.format(err))
			sys.exit(1)
	
		# decouple from parent environment
		os.chdir('/') 
		os.setsid() 
		os.umask(0) 
	
		# do second fork
		try: 
			pid = os.fork() 
			if pid > 0:

				# exit from second parent
				sys.exit(0) 
		except OSError as err: 
			sys.stderr.write('fork #2 failed: {0}\n'.format(err))
			sys.exit(1) 
	
		# redirect standard file descriptors
		sys.stdout.flush()
		sys.stderr.flush()
		si = open(os.devnull, 'r')
		so = open(os.devnull, 'a+')
		se = open(os.devnull, 'a+')

		os.dup2(si.fileno(), sys.stdin.fileno())
		os.dup2(so.fileno(), sys.stdout.fileno())
		os.dup2(se.fileno(), sys.stderr.fileno())
	
		# write pidfile
		atexit.register(self.delpid)

		pid = str(os.getpid())
		with open(self.pid_file_name,'w+') as f:
			f.write(pid + '\n')
	
	def delpid(self):
		os.remove(self.pid_file_name)

	def start(self):
		"""Start the daemon."""

		# Check for a pidfile to see if the daemon already runs
		try:
			with open(self.pid_file_name,'r') as pf:

				pid = int(pf.read().strip())
		except IOError:
			pid = None
	
		if pid:
			message = "pidfile {0} already exist. " + \
					"Daemon already running?\n"
			sys.stderr.write(message.format(self.pid_file_name))
			sys.exit(1)
		
		# Start the daemon
		self.daemonize()
		self.run()

	def stop(self):
		"""Stop the daemon."""

		# Get the pid from the pidfile
		try:
			with open(self.pid_file_name,'r') as pf:
				pid = int(pf.read().strip())
		except IOError:
			pid = None
	
		if not pid:
			message = "pidfile {0} does not exist. " + \
					"Daemon not running?\n"
			sys.stderr.write(message.format(self.pid_file_name))
			return # not an error in a restart

		# Try killing the daemon process	
		try:
			while 1:
				os.kill(pid, signal.SIGTERM)
				time.sleep(0.1)
		except OSError as err:
			e = str(err.args)
			if e.find("No such process") > 0:
				if os.path.exists(self.pid_file_name):
					os.remove(self.pid_file_name)
			else:
				print (str(err.args))
				sys.exit(1)

	def restart(self):
		"""Restart the daemon."""
		self.stop()
		self.start()

	def run(self):
		"""You should override this method when you subclass Daemon.
		
		It will be called after the process has been daemonized by 
		start() or restart()."""

