### Scraping
import requests
import pickle
import random
from bs4 import BeautifulSoup
import pandas as pd

URL = 'https://en.wikipedia.org/wiki/List_of_current_AFL_team_squads'
page = requests.get(URL)

soup = BeautifulSoup(page.content, 'html.parser')
teams = {}
tables = soup.find_all('table', class_='toccolours')
for table in tables:
    team = table.find('div').text.strip()[:-12]
    teams[team] = {}
    details = table.find('tbody').find_all('ul')
    count = 0
    for detail in details:
        if count < 3:
            names = detail.find_all('li')
            for name in names:
                lines = name.find_all('span')
                count1 = 0
                for line in lines:
                    if count1 == 1:
                        num = line.text.strip()
                    count1 =+ 1
                player = name.find('a').text.strip()
                teams[team][player] = num   
        if 2 < count < 5 and team == 'North Melbourne Football Club':
            names = detail.find_all('li')
            for name in names:
                lines = name.find_all('span')
                count1 = 0
                for line in lines:
                    if count1 == 1:
                        num = line.text.strip()
                    count1 =+ 1
                player = name.find('a').text.strip()
                teams[team][player] = num  
        count += 1
            
team_file = open("AFLPlayerData.pkl", "wb")
pickle.dump(teams, team_file)
team_file.close()