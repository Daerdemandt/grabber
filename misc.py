#!/usr/bin/env python3

from os import listdir, path # to get files in the directory
from importlib import import_module

# TODO: make it either relative to this file or sth.
# Can change if everything is made into package
bet_parsers_dir = './bet_parsers'
data_filename = 'data.bin'

import sys # so we can import BP; is to be removed when everything is made as a package
sys.path.append(bet_parsers_dir)
from bet_parser import BetParser

def read_bet_parsers(parsers_dir):
	parsers = {}
	ignored = set(['bet_parser.py'])
	def isfile(name):
		return path.isfile(path.join(parsers_dir, name))
	filenames = set(filter(isfile, listdir(parsers_dir))) - ignored
	parsernames = [BetParser.name_from_filename(f) for f in filenames]
	result = {}
	for name in parsernames:
		module = import_module(name)
		Parser = getattr(module, 'Parser')
		parser = Parser()
		parsers[name] = parser
	return parsers

def get_new_data(fields=None):
	parsers = read_bet_parsers(bet_parsers_dir)
	data = {}
	for name in parsers:
		parsers[name].do_static_cast()
		data[name] = parsers[name].results
	return data

from pickle import dump, load
from weakref import finalize

class file_set(set):
	'''
	Set that is initiated from a given file (if it exists) and
	writes its own contents to the same file on deletion.
	'''
	def __init__(self, filename):
		''' Read contents of set from file, set up deletion hook '''
		self.filename = filename
		super().__init__(self)
		if not isinstance(filename, str):
			return
		try:
			print(self.filename)
			with open(self.filename, 'rb') as cache_file:
				l = load(cache_file)
				print(l, type(l))
				self |= l
#				self |= load(cache_file)
		except FileNotFoundError:
			with open(self.filename, 'a'):
				pass # create the file if it does not exist
		# when object is deleted, update file
		finalize(self, lambda: self.dump_to_file())
	
	def dump_to_file(self):
		with open(self.filename, 'wb+') as cache_file:
			dump(self, cache_file)

def load_existing_data():
	try:
		with open(data_filename, 'rb') as cache_file:
			data = load(cache_file)
	except FileNotFoundError:
		with open(data_filename, 'a'):
			pass # create the file if it does not exist
		data = []
	return data

def dump_existing_data(data):
	with open(data_filename, 'wb+') as cache_file:
		dump(data, cache_file)


def update_data():
# TODO: find way to avoid duplicates
# TODO: find out why file_set doesn't work
	data = load_existing_data()
	new_data = get_new_data()
	for name in new_data:
		data += list(new_data[name])
	dump_existing_data(data)
	
	return data
