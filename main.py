#!/usr/bin/env python3
# Calls other scripts that get the data.
from os import listdir, path # to get files in the directory
from importlib import import_module

# TODO: make it either relative to this file or sth.
# Can change if everything is made into package
bet_parsers_dir = './bet_parsers'

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

def main():
	parsers = read_bet_parsers(bet_parsers_dir)
	for name in parsers:
		parsers[name].print_results_pretty()

if __name__ == "__main__":
	main()
