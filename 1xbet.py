#!/usr/bin/env python3
# 1xbet.py
# Gets cybersports bet data from 1-x-bet.com
# Can be either called directly (outputs to stdout), or imported.
# If you import this file, use get_data method.
# Several assumptions about page format are made. If any of them is violated, ParseError is raised.

from datetime import datetime

from misc import *

URL='https://1-x-bet.com/line/KiberSport/'

def get_data():
	filename = get_filename(URL)
	get_file(filename, URL)
	yield from extract_data(filename)
	remove_file(filename)

def extract_data(filename):
	whole_soup = read_soup(filename)
	body = whole_soup.html.body
	bets_table = list(soup_find_only(body, class_="hot_live_bet"))
	# Last etnry is just a string, is it?
	if not isinstance(bets_table[-1], element.NavigableString):
		raise ParseError('Error: page at ' + URL + "doesn't comply to assumed format")
	# Last entry is just a string so we don't parse it
	for bet in bets_table[:-1]:
		bet_data = {}
		
		# Let's start with competing teams' names
		game_name = soup_find_only(bet, class_='gname hotGameTitle')
		game_name = game_name.string.strip()
		# We assume that teams' names don't contain '—'
		if 1 != game_name.count('—'):
			raise ParseError('Error: page at ' + URL + "doesn't comply to assumed format")
		bet_data['team1'], bet_data['team2'] = game_name.split(' — ')
		
		# Now, lets go for time and date. We use UTC, and so do they, apparently
		# I don't know why they've called it this way.
		datetime_string = str(soup_find_only(bet, 'td', class_='score'))
		# TODO: try-catch this for ValueError, transform it to ParseError
		# We'll have to do it the ugly way. Use '>' and '<' as separators.
		datetime_string = datetime_string.replace('>', '<').split('<')[2]
		date, time = datetime_string.split(' | ')
		day, month = date.split('.')
		day, month = int(day), int(month)
		year = datetime.now().year
		# Bet info is provided a bit in advance.
		# We shall work properly on a new year.
		if 12 == datetime.now().month and 1 == month:
			year += 1
		hour, minute = time.split(':')
		hour, minute = int(hour), int(minute)
		bet_data['datetime'] = datetime(year, month, day, hour, minute, tzinfo=UTC())
		
		# Finally, let's get odds we need
		def get_odds(betname):
			return float(soup_find_only(bet, 'div', {'data-betname':betname}).string.strip())
		bet_data['team1_wins'] = get_odds('П1')
		bet_data['team2_wins'] = get_odds('П2')
		yield bet_data
		
def main():
	print_bets(get_data())
			
if __name__ == "__main__":
	main()
