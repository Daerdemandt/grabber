import sys # so we can import GP; is to be removed when everything is made as a package
sys.path.append('./..')
from generic_parser import GenericParser

from datetime import timedelta, tzinfo # create UTC timezone - BP
from inspect import getfile # to get instance's filename
from os import path # to strip filename of unneeded stuff
import re # poor man's name recognising

class UTC(tzinfo):
	"""UTC"""
	def utcoffset(self, dt):
		return timedelta(0)
	def tzname(self, dt):
		return "UTC"
	def dst(self, dt):
		return timedelta(0)

class BetParser(GenericParser):
	def __init__(self, url, resource_type):
		fields_we_need = ['source', 'game_id', 'datetime', 'team1', 'team2', 'team1_wins', 'team2_wins', 'league_id', 'discipline']
		# let's keep it 1 resource per file, ok?
		resource_name = self.name_from_filename(getfile(self.__class__))
		GenericParser.__init__(self, url, resource_name, resource_type, fields_we_need)
		self.UTC = UTC()

	def print_result_pretty(self, bet_data):
		name_length = 20
		odds_length = 5
		def pretty_odds(odds):
			return '{0:*^{2}.{1}f}'.format(odds, 2 if odds >= 10 else 3, odds_length)
		dt_string = bet_data['datetime'].strftime("%B %d %H:%M")
		t1_string = bet_data['team1'].rjust(name_length)
		t2_string = bet_data['team2'].ljust(name_length)
		p1_string = pretty_odds(bet_data['team1_wins'])
		p2_string = pretty_odds(bet_data['team2_wins'])
		print(dt_string, t1_string, 'vs', t2_string, p1_string, p2_string)
	
	@staticmethod
	def name_from_filename(filename):
		return path.basename(filename).replace('.py', '')
	
	#TODO: it is a stub, reimplement properly		
	@staticmethod
	def recognize_discipline(gamename):
		'''
	Return normalized name of the game, provided with game name

	Counter-Strike: Global Offensive -> CSGO
	LoL -> LOL
		'''
		exp = {}
	#	print(gamename)
		exp['CSGO'] = re.compile('counter.?.?.?strike|CS', re.IGNORECASE)
		exp['HOTS'] = re.compile('heroes.*storm|HOTS', re.IGNORECASE)
		exp['SC2'] = re.compile('starcraft', re.IGNORECASE)
		exp['DOTA2'] = re.compile('dota', re.IGNORECASE)
		exp['HS'] = re.compile('hearthstone', re.IGNORECASE)
		exp['LOL'] = re.compile('League.*Legends|LoL', re.IGNORECASE)
		exp['WOT'] = re.compile('World.*Tanks|WOT', re.IGNORECASE)
		for e in exp:
			if exp[e].search(gamename):
				return e
		return "UNKNOWN_GAME"
#TODO: implement this
	@staticmethod
	def split_with_discipline(string):
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
		exp['HS'] = re.compile('hearthstone', re.IGNORECASE)
		exp['LOL'] = re.compile('League.*Legends|LoL', re.IGNORECASE)
		exp['WOT'] = re.compile('World.*Tanks|WOT', re.IGNORECASE)
		for e in exp:
			m = exp[e].search(string)
			if m:
				head, tail = string.split(m.group(), maxsplit=1)
				# We use maxsplit because of stuff like 'Киберспорт. Dota 2 - Dotapit League'
				return head, e, tail
		return ('NOT_IMPLEMENTED', "UNKNOWN_GAME", 'NOT_IMPLEMENTED',)

#TODO: implement this
	@staticmethod
	def recognize_name(string):
		'''
Return normalised name of team / player
'NatusVincere' -> 'NaVi'
'Natus.Vinsere' -> 'NaVi'
'Virtus-pro' -> 'VirtusPro'
'''
		return string
# end of BetParser
