#!/usr/bin/env python3
from os import path
import json
def get_config():
	full_script_name = path.abspath(__file__)
	dirname = path.dirname(full_script_name)
	if dirname[-1] != '/':
		dirname += '/'
	config_name = dirname + 'config.json'
	return json.load(open(config_name))


config = get_config()
		
bet_parsers_dir = config['bet_parsers_dir']
data_filename = config['data_filename']
seconds_between_updates = config['seconds_between_updates']
pid_files_folder = config['pid_files_folder']
ignored_sources = set(config['ignored_sources'])
http_port = config['http_port']
