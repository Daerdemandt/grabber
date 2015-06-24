#!/usr/bin/env python3
# Calls other scripts that get the data.
from misc import update_data

def main():
	data = update_data()
	print('{} entries total'.format(len(data)))

if __name__ == "__main__":
	main()
