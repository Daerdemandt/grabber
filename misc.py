#!/usr/bin/env python3

from os import listdir, path # to get files in the directory
from importlib import import_module

from itertools import chain
from functools import reduce

# TODO: make it either relative to this file or sth.
# Can change if everything is made into package
import config

import sys # so we can import BP; is to be removed when everything is made as a package
sys.path.append(config.bet_parsers_dir)
from bet_parser import BetParser


from pickle import dump, load
from weakref import finalize

class file_dict(dict):
	'''
	Dictionary that is initiated from a given file (if it exists) and
	writes its own contents to the same file on deletion.
	'''
	def __init__(self, filename):
		''' Read contents of dictionary from file, set up deletion hook '''
		self.filename = filename
		dict.__init__(self)
		try:
			with open(self.filename, 'rb') as cache_file:
				self.update(load(cache_file))
		except FileNotFoundError:
			pass # on read, don't create the file if it does not exist
		# when object is deleted, update file
		finalize(self, lambda: self.dump_to_file())
	
	def dump_to_file(self):
		with open(self.filename, 'wb+') as cache_file:
			dump(self, cache_file)


class BetDataManager(object):
	def __init__(self):
		self.ignored_sources = config.ignored_sources | set(['bet_parser.py'])

	def export(self):
		with open(config.data_filename, 'rb') as cache_file:
			data = load(cache_file)
			return tuple(data.values())
	
	def update_data(self):
		print('Updating data:')
		if not hasattr(self, 'data'):
			self.data = file_dict(config.data_filename)
			print('{} entries loaded'.format(len(self.data)))
						
		new_data = self.get_new_data()
		print('{} new entries fetched'.format(len(new_data)))

		self.data.update(new_data)
		print('{} entries total'.format(len(self.data)))
		
		self.data.dump_to_file()
	
	def read_bet_parsers(self):
		parsers = {}
		def isfile(name):
			return path.isfile(path.join(config.bet_parsers_dir, name))
		filenames = set(filter(isfile, listdir(config.bet_parsers_dir))) - self.ignored_sources
		parsernames = [BetParser.name_from_filename(f) for f in filenames]
		result = {}
		for name in parsernames:
			module = import_module(name)
			Parser = getattr(module, 'Parser')
			parser = Parser()
			parsers[name] = parser
		return parsers

	def get_new_data(self):
		parsers = self.read_bet_parsers()
		data_by_parser = {}
		for name in parsers:
			parsers[name].do_static_cast()
			data_by_parser[name] = parsers[name].results
		def unique_id(entry):
			return '{}::{}'.format(entry['source'], entry['game_id'])
		data = {unique_id(entry):entry for entry in reduce(chain, data_by_parser.values())}
		return data	

