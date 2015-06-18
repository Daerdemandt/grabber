#!/usr/bin/env python3
# 1xbet.py
# Gets cybersports bet data from 1-x-bet.com
# Can be either called directly (outputs to stdout), or imported.
# If you import this file, use get_data method.
# Several assumptions about page format are made. If any of them is violated, ParseError is raised.

from datetime import datetime
import bs4
from bet_parser import BetParser

class Parser(BetParser):
	def __init__(self):
		BetParser.__init__(self, 'https://1-x-bet.com/line/KiberSport/', 'html')

	def get_data(self):
		body = self.resource.html.body
		bets_table = list(self.find_only(body, class_="hot_live_bet"))
		# Last etnry is just a string, is it?
		self.assume(isinstance(bets_table[-1], bs4.element.NavigableString))
		# Last entry is just a string so we don't parse it
		for bet in bets_table[:-1]:
			bet_data = {'source':self.resource_name}
			# Let's get IDs of game and league
			namestring = self.find_only(bet, 'td', class_='name')
			# If the name is clicked, script is called
			call = namestring.a['onclick']
			arguments = call.replace(')', '(').split('(')[1].split(', ')
			bet_data['league_id'] = arguments[1]
			bet_data['game_id'] = arguments[2]
			# Let's get competing teams' names
			game_name = self.find_only(bet, class_='gname hotGameTitle')
			game_name = game_name.string.strip()
			# We assume that teams' names don't contain '—'
			self.assume(1 == game_name.count('—'))
			bet_data['team1'], bet_data['team2'] = game_name.split(' — ')
		
			# Now, lets go for time and date. We use UTC, and so do they, apparently
			# I don't know why they've called it this way.
			datetime_string = str(self.find_only(bet, 'td', class_='score'))
			# We'll have to do it the ugly way. Use '>' and '<' as separators.
			try:
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
				bet_data['datetime'] = datetime(year, month, day, hour, minute, tzinfo=self.UTC)
			except ValueError:
				self.assume()	
			# Finally, let's get odds we need
			def get_odds(betname):
				return float(self.find_only(bet, 'div', {'data-betname':betname}).string.strip())
			try:
				bet_data['team1_wins'] = get_odds('П1')
				bet_data['team2_wins'] = get_odds('П2')
			except self.Error: # sometimes there's just handicap
				continue
			yield bet_data
		
def main():
	Parser().print_results_pretty()
			
if __name__ == "__main__":
	main()
