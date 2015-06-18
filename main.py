#!/usr/bin/env python3
# Calls other scripts that get the data.
from os import listdir
from importlib import import_module
from bet_parser import BetParser

def read_parsers():
	parsers = {}
	stoplist = set(['main.py', 'misc.py', '__pycache__', 'generic_parser.py', 'bet_parser.py'])
	filenames = set(f for f in listdir() if f[0] != '.') - stoplist
	parsernames = [BetParser.name_from_filename(f) for f in filenames]
	result = {}
	for name in parsernames:
		module = import_module(name)
		Parser = getattr(module, 'Parser')
		parser = Parser()
		parsers[name] = parser
	return parsers

def main():
	parsers = read_parsers()
	for name in parsers:
#		print('From ' + name + ':')
		parsers[name].print_results_pretty()

if __name__ == "__main__":
	main()
