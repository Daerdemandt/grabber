#!/usr/bin/env python3
# Calls other scripts that get the data.
from os import listdir
from importlib import import_module

from misc import print_bets

def get_all_data():
	stoplist = set(['main.py', 'misc.py', '__pycache__'])
	targets = set(f for f in listdir() if f[0] != '.') - stoplist
	targets = [f.replace('.py', '') for f in targets]
	result = {}
	for target in targets:
		module = import_module(target)
		get_data = getattr(module, 'get_data')
		result[target] = get_data()
	return result

def main():
	all_data = get_all_data()
	for source in all_data:
		print(source, ':')
		print_bets(all_data[source])
		

if __name__ == "__main__":
	main()
