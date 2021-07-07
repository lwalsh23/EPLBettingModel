#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 21 16:10:53 2020

@author: Linus
"""

# VERSION 1.6
# ****LIST DIFFERENCES FROM v1.5 HERE*****
# Trying to bet using draw no bet rather than including draw. 

import csv, math, ast, numpy as np

# Define poisson formula
def poisson(actual, mean):
    """returns the probability that a specific 'actual' result occurs given 
    a specific mean"""
    return math.pow(mean, actual) * math.exp(-mean) / math.factorial(actual)

# Import data, found at football-data.co.uk (for EPL)
csvFile = '20112016.csv'

# Create a list of the teams
team_list = []


# Make team list a txt file and open it so you can write into it
k = open('team_list.txt', 'w')
k.write("""{
""")

# Open the data
csvRead = csv.reader(open(csvFile))
next(csvRead)

# Add all the team names to the team list
for row in csvRead:
    if row[2] not in team_list:
        team_list.append(row[2])
    if row[3] not in team_list:
        team_list.append(row[3])

# Alphabetise the list
team_list.sort()

# Creating a file to display the results of betting
v = open('Results.csv', 'w')
v.write('Home Team, Away Team, Bet, Bet Outcome, Predicted Home Odds, Predicted Draw Odds, Predicted Away Odds, Home Expected Goals, Away Expected Goals, Bet365 Home Odds, Bet365 Draw Odds, Bet365 Away Odds, Home Goals, Away Goals, Home Team Home Games, Home Team Home For, Home Team Home Against, Home Team Away Games, Home Team Away For, Home Team Away Against, Away Team Home Games, Away Team Home For, Away Team Home Against, Away Team Away Games, Away Team Away For, Away Team Away Against, Avg League Home Goals, Avg League Away Goals, Home Team Home Form For, Home Team Away Form For, Home Team Home Form Against, Home Team Away Form Against, Away Team Home Form For, Away Team Away Form For, Away Team Home Form Against, Away Team Away Form Against, Avg League Home Form For, Avg League Away Form For, Avg League Home Form Against, Avg League Away Form Against')
v.write('\n')
v.close()

# Create columns for home goals, away goals, home goals conceded, away goals 
# conceded, home games, away games, scoring rate at home, conceding rate at 
# home, scoring rate away and conceding rate away. Scoring rates are based on
# the teams average scoring compared to the competition average (covered 
# later). Have added form (home and away scored and conceded) columns.
for team in team_list:
	k.write("""	'%s': {'home_goals': 0, 'away_goals': 0, 'home_conceded': 0, 
         'away_conceded': 0, 'home_games': 0, 'away_games': 0, 'alpha_h': 0, 
         'beta_h': 0, 'alpha_a': 0, 'beta_a': 0, 'form_scored_h': [], 
         'form_scored_a' : [], 'form_against_h' : [],'form_against_a': [], 
         'form_alpha_h': 0, 'form_alpha_a': 0, 'form_beta_h': 0, 
         'form_beta_a': 0},
""" % (team))

# Close the team list
k.write("}")
k.close()

# Transfer the data to a dictionary
s = open('team_list.txt', 'r').read()
dict = ast.literal_eval(s)

# Create tallies for games played and weeks to wait in order to create a lag
# Can play around with the lag a bit to see what works best, author went with
# lag of 4 weeks...
# Have added "FORM_LAG" in order to give the model the chance to account for 
# the form it wants to consider. Have also added "SEASONS" to indicate how 
# many seasons are being considered (i.e if you're using data from last season
# and this season "SEASONS" = 2). Adjusted "WEEKS_WAIT" to take these two new 
# variables into account, also added 2 to be safe with respect to the home and
# away mix at the start of a season.
GAMES_PLAYED = 0
HOME_WEIGHT = 0.8
FORM_WEIGHT = 0.1
FORM_LAG = 3
SEASONS = 5
WEEKS_WAIT = 38 * (SEASONS - 1) + FORM_LAG * 2 + 2
# Tally for total value so you can track how your betting strategy is going
TOTAL_VALUE = 0

OUTCOME = 0
pred_odds_h = 0
pred_odds_d = 0
pred_odds_a = 0
home_team_exp = 0
away_team_exp = 0
bet365odds_h = 0
bet365odds_d = 0
bet365odds_a = 0

# Open the data and skip the first line (column titles)
csvRead = csv.reader(open(csvFile))
next(csvRead)

# Iterate over the data in order to assign a home team and an away team, as 
# well as a result, probabilities and predictions to be added later.
# Added 'form_goals' and 'form_conceded' both home and away as well as 
# averages for the two
for game in csvRead:
    home_team = game[2]
    away_team = game[3]
    home_goals = int(game[4])
    away_goals = int(game[5])
    home_win_prob = 0
    draw_win_prob = 0
    away_win_prob = 0
    curr_home_goals = 0
    curr_away_goals = 0
    avg_home_goals = 1
    avg_away_goals = 1
    form_goals_h = 0
    form_goals_a = 0
    form_conceded_h = 0
    form_conceded_a = 0
    avg_form_goals_h = 1
    avg_form_goals_a = 1
    avg_form_conceded_h = 1
    avg_form_conceded_a = 1
    
	
    team_bet = ''
    ev_bet = ''
    RESULT = 0
	
	# Within the loop (to ensure current or future games aren't being used for 
    # prediction) add the number of goals scored at home and away 
    for key, value in dict.items():
        curr_home_goals += dict[key]['home_goals']
        curr_away_goals += dict[key]['away_goals']
        
		# If the count has passed the number of weeks waited, find the 
        # averages for the whole league
        # Added calculations forform scored and conceded for the league, as 
        # well as the associated averages.
        if GAMES_PLAYED > (WEEKS_WAIT * 10):
            avg_home_goals = curr_home_goals / (GAMES_PLAYED)
            avg_away_goals = curr_away_goals / (GAMES_PLAYED)    
            for score in dict[key]['form_scored_h']:
                form_goals_h += score
            avg_form_goals_h = form_goals_h / (20 * FORM_LAG)
            for score in dict[key]['form_scored_a']:
                form_goals_a += score
            avg_form_goals_a = form_goals_a / (20 * FORM_LAG)
            for score in dict[key]['form_against_h']:
                form_conceded_h += score
            avg_form_conceded_h = form_conceded_h / (20 * FORM_LAG)
            for score in dict[key]['form_against_a']:
                form_conceded_a += score
            avg_form_conceded_a = form_conceded_a / (20 * FORM_LAG)
                
	# Calculate the attacking rate (home and away) of the two teams, the 
    # defensive rate (home and away) and the expected scores of the home team 
    # and the away team (based on their average goals, their attacking rate 
    # and the other teams defensive rate).
    # Have added in the form alpha and betas.
    if GAMES_PLAYED > (WEEKS_WAIT * 10):
        home_team_a = ((HOME_WEIGHT * (1-FORM_WEIGHT)) * dict[home_team]['alpha_h'] + ((1 - HOME_WEIGHT) * (1-FORM_WEIGHT)) * dict[home_team]['alpha_a'] + (HOME_WEIGHT * FORM_WEIGHT) * dict[home_team]['form_alpha_h'] + ((1 - HOME_WEIGHT) * FORM_WEIGHT) * dict[home_team]['form_alpha_a'])
        away_team_a = (((1 - HOME_WEIGHT) * (1-FORM_WEIGHT)) * dict[away_team]['alpha_h'] + (HOME_WEIGHT * (1-FORM_WEIGHT)) * dict[away_team]['alpha_a'] + ((1 - HOME_WEIGHT) * FORM_WEIGHT) * dict[away_team]['form_alpha_h'] + (HOME_WEIGHT * FORM_WEIGHT) * dict[away_team]['form_alpha_a'])
        home_team_d = ((HOME_WEIGHT * (1-FORM_WEIGHT)) * dict[home_team]['beta_h'] + ((1 - HOME_WEIGHT) * (1-FORM_WEIGHT)) * dict[home_team]['beta_a'] + (HOME_WEIGHT * FORM_WEIGHT) * dict[home_team]['form_beta_h'] + ((1 - HOME_WEIGHT) * FORM_WEIGHT) * dict[away_team]['form_beta_a'])
        away_team_d = (((1 - HOME_WEIGHT) * (1-FORM_WEIGHT)) * dict[away_team]['beta_h'] + (HOME_WEIGHT * (1-FORM_WEIGHT)) * dict[away_team]['beta_a'] + ((1 - HOME_WEIGHT) * FORM_WEIGHT) * dict[away_team]['form_beta_h'] + (HOME_WEIGHT * FORM_WEIGHT) * dict[away_team]['form_beta_a'])
        home_team_exp = avg_home_goals * home_team_a * away_team_d
        away_team_exp = avg_away_goals * away_team_a * home_team_d
	
	
	# Create new document to calculate poisson values for each score
        l = open('poisson.txt', 'w')
		
        # Loop over a range of 10 to find the probability of each score 
        # occuring from 0-0, 1-0,...,9-0,...,1-1,...,9-9
        for i in range(10):
            for j in range(10):
                prob = poisson(i, home_team_exp) * poisson(j, away_team_exp)
                l.write("Prob%s%s = %s\n" % (i, j, prob))
		
        # Close as always
        l.close()
		
        # Read the poisson file and iterate over each line (each scoreline)
        with open('poisson.txt') as f:
            for line in f:
				
                # Assigns a value for each score from the poisson file 
                # e.g Prob31 (3-1) will take home_goals_m = 3 and away_goals_m = 1
                home_goals_m = int(line.split(' = ')[0][4])
                away_goals_m = int(line.split(' = ')[0][5])
				
                # Takes the probability for that score
                prob = float(line.split(' = ')[1])
				
                # If it is a probability of a score where the home team wins, 
                # the probability is added to home_win_prob etc.
                if home_goals_m > away_goals_m:
                    home_win_prob += prob
                elif home_goals_m == away_goals_m:
                    draw_win_prob += prob
                elif home_goals_m < away_goals_m:
                    away_win_prob += prob

        DNB_prob_home = home_win_prob / (home_win_prob + away_win_prob)
        DNB_prob_away = away_win_prob / (home_win_prob + away_win_prob)

# Gives the Bet365 odds for home win, draw and away win
        bet365odds_h, bet365odds_d, bet365odds_a = float(game[23]), float(game[24]), float(game[25])
        DNB_bet365odds_h = (bet365odds_h + bet365odds_a)/(bet365odds_h) * 0.93
        DNB_bet365odds_a = (bet365odds_h + bet365odds_a)/(bet365odds_a) * 0.93
		
        # Calculate the Expected Value of betting on home, draw or away 
        # (assumes a stake of 1 "unit")
        ev_h = (home_win_prob * (bet365odds_h - 1)) - (1 - home_win_prob)
        ev_d = 0 # This is zero for DNB (draw_win_prob * (bet365odds_d - 1)) - (1 - draw_win_prob)
        ev_a = (away_win_prob * (bet365odds_a - 1)) - (1 - away_win_prob)
		
        # Calculating the proportional EVs for each result, i.e the EV as a 
        # proportion of the bet365 odds
        prop_ev_h = ev_h / bet365odds_h
        prop_ev_d = ev_d / bet365odds_d
        prop_ev_a = ev_a / bet365odds_a
        
        # Calculating the predicted odds
        pred_odds_h = (1 - DNB_prob_home) / DNB_prob_home + 1
        # pred_odds_d = (1 - draw_win_prob) / draw_win_prob + 1
        pred_odds_a = (1 - DNB_prob_away) / DNB_prob_away + 1
        
        # Calculating how much greater (or less than) the predicted odds are 
        # as a proportion of the bet365 odds. The lower it is the better.
        prop_odds_h = (pred_odds_h - bet365odds_h) / bet365odds_h
        prop_odds_d = (pred_odds_d - bet365odds_d) / bet365odds_d
        prop_odds_a = (pred_odds_a - bet365odds_a) / bet365odds_a
        
        # Find the highest EV of all the betting options
        highestEV = max(ev_h, ev_d, ev_a)
        highestpropEV = max(prop_ev_h, prop_ev_d, prop_ev_a)
        lowestpropodds = min(prop_odds_h, prop_odds_d, prop_odds_a)
		
        # Basically make the home bet if its the highest EV and the EV is 
        # greater than 0 (a win). If your home win prediction is correct add 
        # the winnings to the total value, otherwise take the stake from the 
        # total value. RESULT added to record the result of the individual bet
        # for analysis purposes
        if (ev_h == highestEV) and (ev_h > 0):
            team_bet = home_team
            ev_bet = ev_h
            if home_goals > away_goals:
                RESULT = (DNB_bet365odds_h - 1)
                TOTAL_VALUE += (DNB_bet365odds_h - 1)
                OUTCOME = 'Win'
            else:
                RESULT = -1
                TOTAL_VALUE -= 1
                OUTCOME = 'Lose'
				
        # Same as above but for draw
        elif (ev_d == highestEV) and (ev_d > 0):
            team_bet = 'Draw'
            ev_bet = ev_d
            if home_goals == away_goals:
                RESULT = (bet365odds_d - 1)
                TOTAL_VALUE += (bet365odds_d - 1)
                OUTCOME = 'Win'
            else:
                RESULT = -1
                TOTAL_VALUE -= 1
                OUTCOME = 'Lose'
        
        # Same as above but for away win
        elif (ev_a == highestEV) and (ev_a > 0):
            team_bet = away_team
            ev_bet = ev_a
            if home_goals < away_goals:
                RESULT = (DNB_bet365odds_a - 1)
                TOTAL_VALUE += (DNB_bet365odds_a - 1)
                OUTCOME = 'Win'
            else:
                RESULT = -1
                TOTAL_VALUE -= 1
                OUTCOME = 'Lose'
                
        # A different betting strategy to the original (above). This one 
        # involves betting based on the highest proportional EV rather than 
        # the highest EV 
        """if (prop_ev_h == highestpropEV) and (prop_ev_h > 0):
            team_bet = home_team
            ev_bet = prop_ev_h
            if home_goals > away_goals:
                RESULT = (bet365odds_h - 1)
                TOTAL_VALUE += (bet365odds_h - 1)
            else:
                RESULT = -1
                TOTAL_VALUE -= 1
				
        # Same as above but for draw
        elif (prop_ev_d == highestpropEV) and (prop_ev_d > 0):
            team_bet = 'Draw'
            ev_bet = prop_ev_d
            if home_goals == away_goals:
                RESULT = (bet365odds_d - 1)
                TOTAL_VALUE += (bet365odds_d - 1)
            else:
                RESULT = -1
                TOTAL_VALUE -= 1
        
        # Same as above but for away win
        elif (prop_ev_a == highestpropEV) and (prop_ev_a > 0):
            team_bet = away_team
            ev_bet = prop_ev_a
            if home_goals < away_goals:
                RESULT = (bet365odds_a - 1)
                TOTAL_VALUE += (bet365odds_a - 1)
            else:
                RESULT = -1
                TOTAL_VALUE -= 1"""
                
                
        # A different betting strategy where you bet on the predicted odds 
        # that have the biggest difference (proportionally) to the bet365 odds.
        """if (prop_odds_h == lowestpropodds) and (ev_h > 0):
            team_bet = home_team
            ev_bet = ev_h
            if home_goals > away_goals:
                RESULT = (bet365odds_h - 1)
                TOTAL_VALUE += (bet365odds_h - 1)
            else:
                RESULT = -1
                TOTAL_VALUE -= 1
				
        # Same as above but for draw
        elif (prop_odds_d == lowestpropodds) and (ev_d > 0):
            team_bet = 'Draw'
            ev_bet = ev_d
            if home_goals == away_goals:
                RESULT = (bet365odds_d - 1)
                TOTAL_VALUE += (bet365odds_d - 1)
            else:
                RESULT = -1
                TOTAL_VALUE -= 1
        
        # Same as above but for away win
        elif (prop_odds_a == lowestpropodds) and (ev_a > 0):
            team_bet = away_team
            ev_bet = ev_a
            if home_goals < away_goals:
                RESULT = (bet365odds_a - 1)
                TOTAL_VALUE += (bet365odds_a - 1)
            else:
                RESULT = -1
                TOTAL_VALUE -= 1"""
        
        
        # This is pretty much to print the results to the console
        # WANT TO MAKE THIS EXPORT THE VALUES TO A CSV INSTEAD
        if (team_bet != '') and (ev_bet != ''):
            #print ("Bet on '%s' (EV = %s)" % (team_bet, ev_bet))
            print (TOTAL_VALUE)
    
    # Trying to export as much info as possible to a results csv file to 
    # better analyse what could make the model better.
    fields = [home_team, away_team, team_bet, OUTCOME, pred_odds_h, pred_odds_d, 
              pred_odds_a, home_team_exp, away_team_exp, bet365odds_h, 
              bet365odds_d, bet365odds_a, home_goals, away_goals,
              dict[home_team]['home_games'], dict[home_team]['home_goals'], 
              dict[home_team]['home_conceded'], dict[home_team]['away_games'], 
              dict[home_team]['away_goals'], dict[home_team]['away_conceded'],
              dict[away_team]['home_games'], dict[away_team]['home_goals'], 
              dict[away_team]['home_conceded'], dict[away_team]['away_games'], 
              dict[away_team]['away_goals'], dict[away_team]['away_conceded'],
              avg_home_goals, avg_away_goals, dict[home_team]['form_scored_h'], 
              dict[home_team]['form_scored_a'], dict[home_team]['form_against_h'], 
              dict[home_team]['form_against_a'], dict[away_team]['form_scored_h'], 
              dict[away_team]['form_scored_a'], dict[away_team]['form_against_h'], 
              dict[away_team]['form_against_a'], avg_form_goals_h, 
              avg_form_goals_a, avg_form_conceded_h, avg_form_conceded_a]
    with open('Results.csv', 'a') as m:
        writer = csv.writer(m)
        writer.writerow(fields)     

	# Add the goals for the game we are currently looking at to the dictionary
    dict[home_team]['home_goals'] += home_goals
    dict[home_team]['home_conceded'] += away_goals
    dict[home_team]['home_games'] += 1
    dict[away_team]['away_goals'] += away_goals
    dict[away_team]['away_conceded'] += home_goals
    dict[away_team]['away_games'] += 1
    
    # Creating a list of the number of goals scored and conceded in the team's 
    # last "FORM_LAG" home and away games. Starts from the begining of the 
    # season so by the time betting commences, it has collected form.
    if GAMES_PLAYED > ((WEEKS_WAIT - FORM_LAG * 2 - 2) * 10):
        dict[home_team]['form_scored_h'].append(home_goals)
        if len(dict[home_team]['form_scored_h']) > FORM_LAG:
            del(dict[home_team]['form_scored_h'][0])
        dict[away_team]['form_scored_a'].append(away_goals)
        if len(dict[away_team]['form_scored_a']) > FORM_LAG:
            del(dict[away_team]['form_scored_a'][0])
        dict[home_team]['form_against_h'].append(away_goals)
        if len(dict[home_team]['form_against_h']) > FORM_LAG:
            del(dict[home_team]['form_against_h'][0])
        dict[away_team]['form_against_a'].append(home_goals)
        if len(dict[away_team]['form_against_a']) > FORM_LAG:
            del(dict[away_team]['form_against_a'][0])
	
   # This assigns values to form alpha and betas for home and away. It adds 
   # the recent games (held in the form lists in dict), divides that by the 
   # number of games in that list (FORM_LAG) and then divides that by the 
   # league average. Thereby giving a comparison of how the teams form is 
   # compared to the rest of the league.
    if GAMES_PLAYED > (WEEKS_WAIT * 10):
        for key, value in dict.items():
            form_goals_h = 0
            form_goals_a = 0
            form_conceded_h = 0
            form_conceded_a = 0
            for score in dict[key]['form_scored_h']:
                form_goals_h += score
            form_alpha_h = (form_goals_h / FORM_LAG) / avg_form_goals_h
            dict[key]['form_alpha_h'] = form_alpha_h
            for score in dict[key]['form_scored_a']:
                form_goals_a += score
            form_alpha_a = (form_goals_a / FORM_LAG) / avg_form_goals_a
            dict[key]['form_alpha_a'] = form_alpha_a
            for score in dict[key]['form_against_h']:
                form_conceded_h += score
            form_beta_h = (form_conceded_h / FORM_LAG) / avg_form_conceded_h
            dict[key]['form_beta_h'] = form_beta_h
            for score in dict[key]['form_against_a']:
                form_conceded_a += score
            form_beta_a = (form_conceded_a / FORM_LAG) / avg_form_conceded_a
            dict[key]['form_beta_a'] = form_beta_a        
    
    # Add one to the tally of total games played
    GAMES_PLAYED += 1
	
	# Update the factors (for the whole league but only the two teams 
    # concerned will actually change). The factors are pretty much 
    # scoring rate @ home divided by the league's average scoring rate @ home 
    # and away and the same for conceding.
    if GAMES_PLAYED > (WEEKS_WAIT * 10):
        for key, value in dict.items():
            alpha_h = (dict[key]['home_goals'] / dict[key]['home_games']) / avg_home_goals
            beta_h = (dict[key]['home_conceded'] / dict[key]['home_games']) / avg_away_goals
            alpha_a = (dict[key]['away_goals'] / dict[key]['away_games']) / avg_away_goals
            beta_a = (dict[key]['away_conceded'] / dict[key]['away_games']) / avg_home_goals
            dict[key]['alpha_h'] = alpha_h
            dict[key]['beta_h'] = beta_h
            dict[key]['alpha_a'] = alpha_a
            dict[key]['beta_a'] = beta_a
    
    # Adding results to the results csv
    """fields = [team_bet, ev_bet, RESULT, TOTAL_VALUE]
    with open('Results.csv', 'a') as m:
        writer = csv.writer(m)
        writer.writerow(fields)"""
"""for key, value in dict.items():
    fields = [key, dict[key]['last_5_games_scored'][0], dict[key]['last_5_games_scored'][1], dict[key]['last_5_games_scored'][2], dict[key]['last_5_games_scored'][3], dict[key]['last_5_games_scored'][4]]
    with open('Results.csv', 'a') as m:
        writer = csv.writer(m)
        writer.writerow(fields)"""
        
"""# Checking if the form stuff is correct
for key, value in dict.items():
    fields = [key, dict[key]['form_scored_h'], dict[key]['form_alpha_h'], dict[key]['form_scored_a'], dict[key]['form_alpha_a'], dict[key]['form_against_h'], dict[key]['form_beta_h'], dict[key]['form_against_a'], dict[key]['form_beta_a'], avg_form_goals_h]
    with open('Results.csv', 'a') as m:
        writer = csv.writer(m)
        writer.writerow(fields)"""
        
"""HOME_TEAM = 'Southampton'
AWAY_TEAM = 'Liverpool'
HOME_ODDS = 1 + (5.1 - 1) * 0.95
DRAW_ODDS = 1 + (4.6 - 1) * 0.95
AWAY_ODDS = 1 + (1.7 - 1) * 0.95
home_win_prob = 0
draw_win_prob = 0
away_win_prob = 0

for key, value in dict.items():
    curr_home_goals += dict[key]['home_goals']
    curr_away_goals += dict[key]['away_goals']

avg_home_goals = curr_home_goals / (GAMES_PLAYED)
avg_away_goals = curr_away_goals / (GAMES_PLAYED)    

home_team_a = ((HOME_WEIGHT * (1-FORM_WEIGHT)) * dict[HOME_TEAM]['alpha_h'] + ((1 - HOME_WEIGHT) * (1-FORM_WEIGHT)) * dict[HOME_TEAM]['alpha_a'] + (HOME_WEIGHT * FORM_WEIGHT) * dict[HOME_TEAM]['form_alpha_h'] + ((1 - HOME_WEIGHT) * FORM_WEIGHT) * dict[HOME_TEAM]['form_alpha_a'])
away_team_a = (((1 - HOME_WEIGHT) * (1-FORM_WEIGHT)) * dict[AWAY_TEAM]['alpha_h'] + (HOME_WEIGHT * (1-FORM_WEIGHT)) * dict[AWAY_TEAM]['alpha_a'] + ((1 - HOME_WEIGHT) * FORM_WEIGHT) * dict[AWAY_TEAM]['form_alpha_h'] + (HOME_WEIGHT * FORM_WEIGHT) * dict[AWAY_TEAM]['form_alpha_a'])
home_team_d = ((HOME_WEIGHT * (1-FORM_WEIGHT)) * dict[HOME_TEAM]['beta_h'] + ((1 - HOME_WEIGHT) * (1-FORM_WEIGHT)) * dict[HOME_TEAM]['beta_a'] + (HOME_WEIGHT * FORM_WEIGHT) * dict[HOME_TEAM]['form_beta_h'] + ((1 - HOME_WEIGHT) * FORM_WEIGHT) * dict[HOME_TEAM]['form_beta_a'])
away_team_d = (((1 - HOME_WEIGHT) * (1-FORM_WEIGHT)) * dict[AWAY_TEAM]['beta_h'] + (HOME_WEIGHT * (1-FORM_WEIGHT)) * dict[AWAY_TEAM]['beta_a'] + ((1 - HOME_WEIGHT) * FORM_WEIGHT) * dict[AWAY_TEAM]['form_beta_h'] + (HOME_WEIGHT * FORM_WEIGHT) * dict[AWAY_TEAM]['form_beta_a'])
home_team_exp = avg_home_goals * home_team_a * away_team_d
away_team_exp = avg_away_goals * away_team_a * home_team_d

p = open('poisson.txt', 'w')
for i in range(10):
    for j in range(10):
        prob = poisson(i, home_team_exp) * poisson(j, away_team_exp)
        p.write("Prob%s%s = %s\n" % (i, j, prob))

p.close()

with open('poisson.txt') as f:
    for line in f:
        home_goals_m = int(line.split(' = ')[0][4])
        away_goals_m = int(line.split(' = ')[0][5])
        prob = float(line.split(' = ')[1])
        if home_goals_m > away_goals_m:
            home_win_prob += prob
        elif home_goals_m == away_goals_m:
            draw_win_prob += prob
        elif home_goals_m < away_goals_m:
            away_win_prob += prob

ev_h = (home_win_prob * (HOME_ODDS - 1)) - (1 - home_win_prob)
ev_d = (draw_win_prob * (DRAW_ODDS - 1)) - (1 - draw_win_prob)
ev_a = (away_win_prob * (AWAY_ODDS - 1)) - (1 - away_win_prob)
prop_ev_h = ev_h / HOME_ODDS
prop_ev_d = ev_d / DRAW_ODDS
prop_ev_a = ev_a / AWAY_ODDS

highestEV = max(ev_h, ev_d, ev_a)
highestpropEV = max(prop_ev_h, prop_ev_d, prop_ev_a)

if (ev_h == highestEV) and (ev_h > 0):
    print ("Bet on '%s' (EV = %s)" % (HOME_TEAM, ev_h))	
elif (ev_d == highestEV) and (ev_d > 0):
    print ("Bet on '%s' (EV = %s)" % ('Draw', ev_d))
elif (ev_a == highestEV) and (ev_a > 0):
    print ("Bet on '%s' (EV = %s)" % (AWAY_TEAM, ev_a))"""
        
"""if (prop_ev_h == highestpropEV) and (prop_ev_h > 0):
    print ("Bet on '%s' (EV = %s)" % (HOME_TEAM, prop_ev_h))	
elif (prop_ev_d == highestpropEV) and (prop_ev_d > 0):
    print ("Bet on '%s' (EV = %s)" % ('Draw', prop_ev_d))
elif (prop_ev_a == highestpropEV) and (prop_ev_a > 0):
    print ("Bet on '%s' (EV = %s)" % (AWAY_TEAM, ev_a))"""
    
"""print((1 - home_win_prob) / home_win_prob + 1)
print(home_win_prob)
print((1 - draw_win_prob) / draw_win_prob + 1)
print(draw_win_prob)
print((1 - away_win_prob) / away_win_prob + 1)
print(away_win_prob)"""

                                                        	
