fields_we_need = ['datetime', 'team1', 'team2', 'team1_wins', 'team2_wins']

from datetime import timedelta, tzinfo
import urllib.request, os, os.path
from bs4 import BeautifulSoup, element
from hashlib import md5

class UTC(tzinfo):
	"""UTC"""
	def utcoffset(self, dt):
		return timedelta(0)
	def tzname(self, dt):
		return "UTC"
	def dst(self, dt):
		return timedelta(0)
		

class ParseError(Exception):
	pass

def read_soup(filename):
	with open(filename) as input_file:
		return BeautifulSoup(input_file)

tmpdir = '/tmp/bets_grabber'

def get_file(filename, address):
	if not os.path.exists(tmpdir):
		os.mkdir(tmpdir)
	if not os.path.exists(filename):
		urllib.request.urlretrieve(address, filename)

def remove_file(filename):
	os.remove(filename)

def soup_find_only(where, *args, **kwargs):
	results = where.find_all(*args, **kwargs)
	if len(results) != 1:
		raise ParseError('Error: page at ' + URL + "doesn't comply to assumed format")
	return results[0]

def get_filename(url):
	for header in ['https://', 'http://', 'www.']:
		if url.startswith(header):
			url = url.replace(header, '')
	domain_name = url.split('/')[0]
	assert len(domain_name) > 0
	addr_digest = md5(url.encode('utf-8')).hexdigest()
	return tmpdir + '/' + domain_name + '.' + addr_digest

def print_bet_pretty(bet_data):
	dt_string = bet_data['datetime'].strftime("%B %d, %Y %H:%M")
	name_length = 20
	t1_string = bet_data['team1'].rjust(name_length)
	t2_string = bet_data['team2'].ljust(name_length)
	odds_length = 5
	p1_string = str(bet_data['team1_wins']).ljust(odds_length)
	p2_string = str(bet_data['team2_wins']).ljust(odds_length)
	print(dt_string, t1_string, 'vs', t2_string, p1_string, p2_string)
	
def print_bet_simple(bet_data):
	print("'" + "', '".join(str(bet_data[field]) for field in fields_we_need) + "'")

def print_bets(bets):
	for bet in bets:
		print_bet_pretty(bet)

def print_bets_simple(bets):
	for bet in bets:
		print_bet_simple(bet)
