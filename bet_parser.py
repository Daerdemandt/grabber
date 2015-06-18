from generic_parser import GenericParser
from datetime import timedelta, tzinfo # create UTC timezone - BP
from inspect import getfile # to get instance's filename
from os import path # to strip filename of unneeded stuff

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
		fields_we_need = ['source', 'game_id', 'datetime', 'team1', 'team2', 'team1_wins', 'team2_wins', 'league_id']
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
# end of BetParser
