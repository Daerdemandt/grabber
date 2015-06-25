#!/usr/bin/env python3
import http.server
import socketserver

from misc import load_existing_data
import json

Handler = http.server.SimpleHTTPRequestHandler

class MyHandler(http.server.SimpleHTTPRequestHandler):
	# TODO: I don't know what this is. Maybe I should remove it.
	def respond(self, content, content_type='text/html', code=200):
		self.send_response(code)
		self.send_header("Content-type", content_type)
		self.end_headers()
		self.wfile.write(bytes(content, 'UTF-8'))
		
	def do_PUT(self):
		print("----- SOMETHING WAS PUT!! ------")
		print(self.headers)
		length = int(self.headers['Content-Length'])
		content = self.rfile.read(length)
		self.send_response(200)
		print(content)

	def not_implemented(self):
		doc = []
		doc += ["<html><head><title>Not implemented.</title></head>"]
		doc += ["<body><p>{} is not implemented yet.</p>".format(self.path)]
		doc += ["</body></html>"]
		self.respond('\n'.join(doc))

	def not_found(self):
		doc = []
		doc += ["<html><head><title>404 Not found</title></head>"]
		doc += ["<body><p>There is no {} here.</p>".format(self.path)]
		doc += ["</body></html>"]
		self.respond('\n'.join(doc), code=404)
	
	def return_matches(self):
		def transform(entry):
			result = {}
			result['id'] = '{}::{}'.format(entry['source'], entry['game_id'])
			result['entrant1'] = entry['team1']
			result['entrant2'] = entry['team2']
			result['timestamp'] = entry['datetime'].timestamp()
			result['entrant1_odds'] = entry['team1_wins']
			result['entrant2_odds'] = entry['team2_wins']
			return result
		data = load_existing_data()
		transformed_data = list(map(transform, data.values()))
		j = json.dumps(transformed_data)
		self.respond(j, content_type="application/json")

	def do_GET(self):
		def wr(string):
			self.wfile.write(bytes(string, 'UTF-8'))
		"""Respond to a GET request."""


		actions = {}
		actions['/entrants'] = self.not_implemented
		actions['/matches'] = self.return_matches
		actions['/services'] = self.not_implemented

		if self.path in actions:
			actions[self.path]()
		else:
			self.not_found()

def run_server(port):
	httpd = socketserver.TCPServer(("", port), MyHandler)
	print("serving at port", port)
	httpd.serve_forever()
