#!/usr/bin/env python3
# 1xbet.py
# Gets cybersports bet data from 1-x-bet.com
# Can be either called directly (outputs to stdout), or imported.
# If you import this file, use get_data method.
# Several assumptions about page format are made. If any of them is violated, ParseError is raised.

from datetime import datetime
import bs4
from bet_parser import BetParser

# temporary
import re

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
			try:
#				print(bet.prettify())
				bet_data = {'source':self.resource_name}
				# Let's get IDs of game and league
				bet_name = self.find_only(bet, 'td', class_='name')
				bet_data.update(self.parse_bet_name(bet_name))
				# Here we can find team names, game name and league name
				game_title = self.find_only(bet, class_='gname hotGameTitle')
				bet_data.update(self.parse_game_title(game_title))

				# Now, lets go for time and date. We use UTC, and so do they, apparently
				# I don't know why they've called it this way.
				dt_string = str(self.find_only(bet, 'td', class_='score'))
				bet_data['datetime'] = self.parse_datetime_string(dt_string)
				
				# Finally, let's get odds we need
				bet_data.update(self.get_odds(bet))
			except self.InvalidPiece:
				#TODO: probably log that we had to omit this entry
				continue
			except self.ParsingError:
				# Now that's serious.
				# TODO: definitely log this
				print(bet.prettify())
				continue
			yield bet_data
	
	def get_odds(self, bet):
		'''
	Provided with bs4-parsed HTML of a bet, return odds for 2 teams.

	Example:
	...
	<div data-betname="П1" data-coef="1.81" data-evid="5548734701" data-gameid="55487347" data-group="1" data-param="0" data-player="0" data-type="1" title="">
		1.81
	</div>
	...
	<div data-betname="П2" data-coef="1.9" data-evid="5548734703" data-gameid="55487347" data-group="1" data-param="0" data-player="0" data-type="3" title="">
		1.9
	</div>
	...

	Returns {'team1_wins':1.81, 'team2_wins':1.9}
		'''
		def get_odd(bet, betname):
			'''
	Provided with bs4-parsed HTML of a bet, return odd with a given name
	
	For example, for
	<div data-betname="П1" data-coef="1.81" data-evid="5548734701" data-gameid="55487347" data-group="1" data-param="0" data-player="0" data-type="1" title="">
		1.81
	</div>
	return value will be 1.81
			'''
			odd = self.find_only_maybe(bet, 'div', {'data-betname':betname})
			return float(odd.string.strip())

		result = {}
		try:
			result['team1_wins'] = get_odd(bet, 'П1')
			result['team2_wins'] = get_odd(bet, 'П2')
		except ValueError:
			raise self.ParsingError
		return result

	def parse_bet_name(self, bet_name):
		'''
Return dictionary with game_id and league_id retrieved from bet name.

Input - bs4 made from HTML, like:
<td class="name">
	<a href="line/KiberSport/995719-Kibersport-Counter-Strike-Global-Offensive---ESL-ESEA-Pro-Le/55322249-Liquid-Method/" onclick="showIgrok_(40, '995719', 55322249, this, event);">
	1207 | КиберСпорт
	<span class="gname hotGameTitle" title="Киберспорт. Counter-Strike: Global Offensive - ESL ESEA Pro Le">
	Liquid — Method
	</span>
	</a>
</td>

Desired output - {'game_id':55322249, 'league_id':995719}		
'''
		result = {}
		try:
			# If the name is clicked, script is called
			call = bet_name.a['onclick']
			arguments = call.replace(')', '(').split('(')[1].split(', ')
			league_id = arguments[1]
			self.assume(league_id[0] == league_id[-1] == "'")
			result['league_id'] = int(league_id[1:-1])
			result['game_id'] = int(arguments[2])
			return result
		except ValueError:
			raise self.Error
		

	def parse_datetime_string(self, dt_string):
		'''Return datetime object based on a datetime string (bs4 from HTML)

Typical input - bs4 from html like:
<td class="score">
	19.06 | 01:00
	<span class="timer_line" title="До начала осталось: 7 часов 04 минуты 47 секунд">
	7:04:47
	</span>
	<a ,="" class="hot_table_plus" data-idgame="55322249" data-idsport="40" onclick="showMore(this);">
	2
	</a>
	<!-- a class="stat_icon"></a -->
</td>

Desired return value - datetime object, corresponding to 19.06 of this year, 01:00 UTC.
'''
		try:
			# We'll have to do it the ugly way. Use '>' and '<' as separators.
			dt_string = dt_string.replace('>', '<').split('<')[2]
			date, time = dt_string.split(' | ')
			day, month = date.split('.')
			day, month = int(day), int(month)
			year = datetime.now().year
			# Bet info is provided a bit in advance.
			# We shall work properly on a new year.
			if 12 == datetime.now().month and 1 == month:
				year += 1
			hour, minute = time.split(':')
			hour, minute = int(hour), int(minute)
			return datetime(year, month, day, hour, minute, tzinfo=self.UTC)
		except ValueError:
			raise self.Error
		

	def parse_game_title(self, game_title):
		'''
Extract some fields from bs4-parsed title of match.

Return dictionary with team names, league name and discipline name exctracted from provided piece of bs4-parsed HTML. HTML piece in question is supposed to look like:
<span class="gname hotGameTitle" title="КиберСпорт. Dota 2. ESL One">
	Invictus Gaming — Fnatic
</span>
Result will be {'team1':'Invictus Gaming', 'team2':'Fnatic',
                'discipline':'Dota2','league_name':'ESL One'}
'team1', 'team2' and 'discipline' contain normalized/recognized names
'''
		result = {}
		# Let's get competing teams' names
		match_name = game_title.string.strip()
		# We assume that teams' names don't contain '—'
		self.assume_maybe(1 == match_name.count('—'))
		result['team1'], result['team2'] = map(self.recognize_name, match_name.split(' — '))
		# Done with names, let's get discipline and league
		self.assume('title' in game_title.attrs)
		title_string = game_title.attrs['title'].strip()
		title_string_splitted = self.split_with_discipline(title_string)
		result['discipline'] = title_string_splitted[1]
		league_name_string = title_string_splitted[2].strip()
		while league_name_string[0] in "-.,:; ":
			self.assume(league_name_string)
			league_name_string = league_name_string[1:]
		result['league_name'] = league_name_string
		return result
	
		
#TODO: implement this
	def split_with_discipline(self, string):
		'''
Return normalised name of discipline and remainder of the string

'КиберСпорт. Dota 2. ESL One' -> ('КиберСпорт. ', 'Dota2', '. ESL One',)
'Киберcпорт. Counter-Strike: Global Offensive - ESL ESEA Pro' -> ('Киберcпорт. ', 'CSGO', ' - ESL ESEA Pro',)
'''
		exp = {}
#	print(gamename)
		exp['CSGO'] = re.compile('counter.?.?.?strike|CS', re.IGNORECASE)
		exp['HOTS'] = re.compile('heroes.*storm|HOTS', re.IGNORECASE)
		exp['SC2'] = re.compile('starcraft', re.IGNORECASE)
		exp['DOTA2'] = re.compile('dota', re.IGNORECASE)
		exp['HS'] = re.compile('heartstone', re.IGNORECASE)
		exp['LOL'] = re.compile('League.*Legends|LoL', re.IGNORECASE)
		exp['WOT'] = re.compile('World.*Tanks|WOT', re.IGNORECASE)
		for e in exp:
			m = exp[e].search(string)
			if m:
				head, tail = string.split(m.group(), maxsplit=1)
				# We use maxsplin because of stuff like 'Киберспорт. Dota 2 - Dotapit League'
				return head, e, tail
		return ('NOT_IMPLEMENTED', "UNKNOWN_GAME", 'NOT_IMPLEMENTED',)


		return ('NOT_IMPLEMENTED', 'NOT_IMPLEMENTED', 'NOT_IMPLEMENTED',)
#TODO: implement this
	def recognize_name(self, string):
		'''
Return normalised name of team / player
'NatusVincere' -> 'NaVi'
'Natus.Vinsere' -> 'NaVi'
'Virtus-pro' -> 'VirtusPro'
'''
		return string

def main():
	Parser().print_results_pretty()
			
if __name__ == "__main__":
	main()
