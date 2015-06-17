#!/usr/bin/env python3
# egamingbets.py
# Gets cybersports bet data from egamingbets.com
# Can be either called directly (outputs to stdout), or imported.
# If you import this file, use get_data method.
# Several assumptions about page format are made. If any of them is violated, ParseError is raised.

from datetime import datetime
from misc import BetParser

class Parser(BetParser):
	def __init__(self):
		url = 'http://egamingbets.com/ajax.php?key=modules_tables_update_UpdateTableBets&act=UpdateTableBets&ajax=update&fg=1&ind=tables&st=0&type=modules&ut=0'
		BetParser.__init__(self, url, 'json')

	def get_data(self):
		yield from self.parse_bet_list(self.resource['bets'])
	
	def parse_bet_list(self, bet_list_jsoned):
		print('parse_bet_list is called on list of len', len(bet_list_jsoned))
		for bet in bet_list_jsoned:
			if bet['deleted'] == 0: # Haven't seen single record that had this not 0. But, it can happen one day.
				yield self.parse_bet(bet)
				
	def parse_bet(self, bet_jsoned):
		result = {'source':self.resource_name}
		fields_we_need_here = ['gamer_1', 'gamer_2', 'coef_1', 'coef_2', 'date', 'date_t', 'id']
		self.assume(all(field in bet_jsoned for field in fields_we_need_here))
		self.assume('nick' in bet_jsoned['gamer_1'] and 'nick' in bet_jsoned['gamer_2'])
		result['game_id'] = bet_jsoned['id'].strip()
		result['team1'] = bet_jsoned['gamer_1']['nick'].strip()
		result['team2'] = bet_jsoned['gamer_2']['nick'].strip()
		result['team1_wins'] = float(bet_jsoned['coef_1'])
		result['team2_wins'] = float(bet_jsoned['coef_2'])
		# I don't know the difference between these. Let's assume they're equal and pick first one
		self.assume(bet_jsoned['date'] == bet_jsoned['date_t'])
		result['datetime'] = datetime.fromtimestamp(int(bet_jsoned['date']))
		return result
		

def main():
	Parser().print_results_pretty()
			
if __name__ == "__main__":
	main()
