#!/usr/bin/env python3
# Calls other scripts that get the data.
from os import listdir
from importlib import import_module

def read_parsers():
	parsers = {}
	stoplist = set(['main.py', 'misc.py', '__pycache__'])
	targets = set(f for f in listdir() if f[0] != '.') - stoplist
	targets = [f.replace('.py', '') for f in targets]
	result = {}
	for target in targets:
		module = import_module(target)
		Parser = getattr(module, 'Parser')
		parser = Parser()
		parsers[target] = parser
	return parsers

def main():
	parsers = read_parsers()
	for name in parsers:
#		print('From ' + name + ':')
		parsers[name].print_results_pretty()

if __name__ == "__main__":
	main()
