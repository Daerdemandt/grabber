from urllib.request import urlopen, Request # fetching data
from bs4 import BeautifulSoup, element # parsing html
import json # parsing json
import csv # printing in csv
import sys # redirecting output
from abc import ABCMeta, abstractmethod # GenericParser is an abstract class

#class ParseError(Exception):
#	pass

class GenericParser(object):
	__metaclass__ = ABCMeta

	@abstractmethod
	def get_data(self):
		pass
	@abstractmethod
	def set_url(self):
		pass
	@abstractmethod
	def set_resource_name(self):
		pass
	@abstractmethod
	def set_resource_type(self):
		pass
	@abstractmethod
	def set_fields_we_need(self):
		pass
	
	def __init__(self, url, resource_name, resource_type, fields_we_need):
		self.url = url

		self.resource_name = resource_name
		self.resource_type = resource_type
		
		resource_types = ['html', 'json', 'raw', None]
		if hasattr(self, 'valid_resource_types'):
			self.valid_resource_types |= set(resource_types)
		else:
			self.valid_resource_types = set(resource_types)
		assert self.resource_type in self.valid_resource_types
		
		resource_raw = self.fetch()
		self.resource = None
		# Time to do some generic parsing
		if self.resource_type == 'html':
			self.resource = BeautifulSoup(resource_raw)
		elif self.resource_type == 'json':
			self.resource = json.loads(resource_raw)
		elif self.resource_type == 'raw':
			self.resource = resource_raw
		
		self.fields_we_need = fields_we_need
		
		#TODO: Probably it would be better to make factory for these
		class AbstractParsingException(Exception):
			'''
	Abstract parsing exception.
	
	Any way to express how exactly things can go wrong while
	parsing something probably should be inherited from it.
			'''
			__metaclass__ = ABCMeta
			def __init__(self, message):
				full_message = '{} at {}( {} )'.format(message, resource_name, url)
				super().__init__(message)
		
		self.AbstractParsingException = AbstractParsingException

		
		class ParsingError(AbstractParsingException):
			'''
	Exception that is thrown when source we're parsing does not conform
	to assumed structure and thus can not be parsed at all.
	
	This is a serious thing.
			'''
		self.ParsingError = ParsingError
		
		class InvalidPiece(AbstractParsingException):
			'''
	Exception to skip further parsing of piece.
	
	EAFP. Sometimes, the easiest way to see whether the piece can be
	parsed is to actually try to parse it and see what happens.
	If we have the piece that can be unparseable and it is OK, then
	we should raise this exception to skip the rest of parsing.
	
	This is a part of normal process.
			'''
		self.InvalidPiece = InvalidPiece
		
		self.results = self.get_data()
	
	def find_only_maybe(self, where, *args, **kwargs): # beatifulsoup-only
		'''
	Similar to bs4.find, but raises InvalidPiece if there're more or
	less than 1 results found.
		'''
		assert self.resource_type == 'html'
		results = where.find_all(*args, **kwargs)
		self.assume_maybe(len(results) == 1)
		return results[0]

	def find_only(self, where, *args, **kwargs): # beatifulsoup-only		
		'''
		Similar to bs4.find, but raises ParsingError if there're more
		or less than 1 results found.
		'''
		assert self.resource_type == 'html'
		results = where.find_all(*args, **kwargs)
		self.assume(len(results) == 1)
		return results[0]
	
	def assume_maybe(self, check=False):
		if not check:
			raise self.InvalidPiece('Assumption about document format failed')

	def assume(self, check=False):
		if not check:
			raise self.ParsingError('Assumption about document format failed')

	def do_static_cast(self):
		self.results = tuple(self.results)

	@abstractmethod
	def print_result_pretty(self, result, output_file):
		pass
	
	# TODO: check if this rerouting magic works.
	def print_results_pretty(self, output_file=sys.stdout):
		stdout_save = sys.stdout
		sys.stdout = output_file
		if self.resource_name:
			print('From', self.resource_name, ':')
		for result in self.results:
			self.print_result_pretty(result)
		sys.stdout = stdout_save

	def print_results_csv(self, csvfile=sys.stdout):
		stdout_save = sys.stdout
		sys.stdout = csvfile
		writer = csv.writer(csvfile, dialect='unix')
		writer.writerows(self.export())
		sys.stdout = stdout_save
	
	def export(self, fields=None):
		fields_were_requested = bool(fields)
		if not fields:
			fields = self.fields_we_need
		structured = 'unknown'
		# This is ugly, but I can't change local variable in nested scope
		def export_fields(record, flagreference):
			assert issubclass(record.__class__, (list, tuple, dict))
			if issubclass(record.__class__, dict):
				assert structured
				if 'unknown' == structured:
					flagreference[0] = True
				return tuple(record[field] for field in self.fields_we_need)
			else:
				assert True != structured
				if 'unknown' == structured:
					flagreference[0] = False			
				return tuple(record)
		return tuple(export_fields(item, [structured]) for item in self.results)

#TODO: add catching network errors
	def fetch(self, url=None):
		if not url:
			url = self.url
		source = urlopen(Request(url, headers={'User-Agent': 'Mozilla'}))
		return source.readall().decode('utf-8')

# end of GenericParser
