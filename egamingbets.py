#!/usr/bin/env python3
# egamingbets.py
# Gets cybersports bet data from egamingbets.com
# Can be either called directly (outputs to stdout), or imported.
# If you import this file, use get_data method.
# Several assumptions about page format are made. If any of them is violated, ParseError is raised.

from datetime import datetime
from urllib.request import urlopen, Request
import json


from misc import *

URL = 'http://egamingbets.com/ajax.php?key=modules_tables_update_UpdateTableBets&act=UpdateTableBets&ajax=update&fg=1&ind=tables&st=0&type=modules&ut=0'

#TODO: rewrite ParseError so it could be raised with the same message with only URL provided

# Move this to misc.py
#TODO: add catching network errors
#TODO: use this in other files too
def fetch(URL):
	source = urlopen(Request(URL, headers={'User-Agent': 'Mozilla'}))
	return source.readall().decode('utf-8')

# ['datetime', 'team1', 'team2', 'team1_wins', 'team2_wins']

def parse_bet(bet_jsoned):
	result = {}
	fields_we_need_here = ['gamer_1', 'gamer_2', 'coef_1', 'coef_2', 'date', 'date_t']
	if not all(field in bet_jsoned for field in fields_we_need_here):
		raise ParseError('Error: page at ' + URL + "doesn't comply to assumed format")
	if not 'nick' in bet_jsoned['gamer_1'] or not 'nick' in bet_jsoned['gamer_2']:
		raise ParseError('Error: page at ' + URL + "doesn't comply to assumed format")
	result['team1'] = bet_jsoned['gamer_1']['nick'].strip()
	result['team2'] = bet_jsoned['gamer_2']['nick'].strip()
	result['team1_wins'] = float(bet_jsoned['coef_1'])
	result['team2_wins'] = float(bet_jsoned['coef_2'])
	# I don't know the difference between these. Let's assume they're equal and pick first one
	if bet_jsoned['date'] != bet_jsoned['date_t']:
		raise ParseError('Error: page at ' + URL + "doesn't comply to assumed format")
	result['datetime'] = datetime.fromtimestamp(int(bet_jsoned['date']))
	return result

def parse_bet_list(bet_list_jsoned):
	for bet in bet_list_jsoned:
		if bet['deleted'] == 0: # Haven't seen single record that had this not 0. But, it can happen one day.
			if 'nb_arr' in bet: # there are nested bets
				pass
				# Uncomment this line if you need nested bets, like "will win 1st round" or "will take FB". There seem to be only top-level bets and 1-nested, not deeper.
#				yield from parse_bet_list(bet['nb_arr'])
			else:
				yield parse_bet(bet)		

def get_data():
	whole_thing = json.loads(fetch(URL))
	yield from parse_bet_list(whole_thing['bets'])

def main():
	print_bets(get_data())
			
if __name__ == "__main__":
	main()
