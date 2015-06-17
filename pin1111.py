#!/usr/bin/env python3
# egamingbets.py
# Gets cybersports bet data from egamingbets.com
# Can be either called directly (outputs to stdout), or imported.
# If you import this file, use get_data method.
# Several assumptions about page format are made. If any of them is violated, ParseError is raised.

from misc import BetParser
from time import strptime, mktime
from datetime import datetime

def money_line_to_odds(ml):
	ml = float(ml)
	if ml > 0:
		return 1 + ml / 100
	else:
		return 1 - 100 / ml 

class LeagueParser(BetParser):
	def __init__(self, league_id):
		prefix = 'http://www.pin1111.com/webapi/1.13/api/v1/GuestLines/NonLive/12/'
		BetParser.__init__(self, prefix + league_id, 'json')
	def get_data(self):
		leagues = self.resource['Leagues']
		self.assume(1 == len(leagues))
		events = leagues[0]['Events']
		for event in events:
			fields_we_need_here = ['EventId', 'DateAndTime', 'Participants', 'IsOffline', 'IsMoneyLineEmpty']
			if event['IsOffline'] or event['IsMoneyLineEmpty']:
				continue
			self.assume(all(field in event for field in fields_we_need_here))
			bet_data = {'source':self.resource_name}
			bet_data['game_id'] = event['EventId']
			dt = strptime(event['DateAndTime'].strip(), '%Y-%m-%dT%H:%M:%SZ')
			bet_data['datetime'] = datetime.utcfromtimestamp(mktime(dt)) # check if it's really UTC
			team1, team2 = None, None
			for p in event['Participants']:
				fields_we_need_here = ['MoneyLine', 'Name', 'Type']
				self.assume(all(field in p for field in fields_we_need_here))
				if p['Type'] == 'Team1':
					self.assume(team1 == None)
					team1 = p
				if p['Type'] == 'Team2':
					self.assume(team2 == None)
					team2 = p
			if team1['MoneyLine'] == None or team2['MoneyLine'] == None:
				print("Found")
				print(self.url)
			bet_data['team1_wins'] = money_line_to_odds(team1['MoneyLine'])
			bet_data['team2_wins'] = money_line_to_odds(team2['MoneyLine'])
			bet_data['team1'] = team1['Name'].strip()
			bet_data['team2'] = team2['Name'].strip()

					
			yield bet_data
		pass




class Parser(BetParser):
	def __init__(self):
		BetParser.__init__(self, 'http://www.pin1111.com/en/esports/odds', 'html')

	def get_data(self):
		body = self.resource.html.body
		body = self.find_only(body, 'div', class_='esportsBody')
		all_leagues = body.find_all('a')
		for league in all_leagues:
			league_ref = league['href']
			#print(league.prettify())
			league_id = league_ref.split('=')[1]
			lp = LeagueParser(league_id)
			yield from lp.get_data()

def main():
#	Parser().do_static_cast()
	Parser().print_results_pretty()
			
if __name__ == "__main__":
	main()
