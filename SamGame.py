import pickle
import random

# Load in the team data
team_file = open("AFLPlayerData.pkl", "rb")
teams = pickle.load(team_file)
team_file.close()

# Have them pick a team
team_list = list(teams.keys())
team_pick = input("Pick a team:\n"+"1. "+team_list[0]+"\n"+"2. "+team_list[1]+"\n"+
                  "3. "+team_list[2]+"\n"+"4. "+team_list[3]+"\n"+"5. "+team_list[4]+"\n"+
                  "6. "+team_list[5]+"\n"+"7. "+team_list[6]+"\n"+"8. "+team_list[7]+"\n"+
                  "9. "+team_list[8]+"\n"+"10. "+team_list[9]+"\n"+"11. "+team_list[10]+"\n"+
                  "12. "+team_list[11]+"\n"+"13. "+team_list[12]+"\n"+"14. "+team_list[13]+"\n"+
                  "15. "+team_list[14]+"\n"+"16. "+team_list[15]+"\n"+"17. "+team_list[16]+"\n"+
                  "18. "+team_list[17]+"\n"+"19. all teams"+"\n")
# Playing with all teams
if team_pick == '19':
    num_games = input('How many games you want shmuckduck?')
    correct = 0
    games = 0
    for game in range(0,int(num_games)):
    
        team_num = random.randint(0, len(team_list)-1)
        team = team_list[team_num]
        player_dict = teams[team]
        if list(player_dict.values())[-1]:
            max_num = int(list(player_dict.values())[-1])
        else:
            max_num = int(list(player_dict.values())[-2])  

        selection = random.randint(0,len(player_dict.values()))
        player_name_list = list(player_dict.keys())
        player = player_name_list[selection]
        player_num = player_dict[player]
        if str(player_num) in player_dict.values():
            guess = input(player+' ('+team+')'+': ')
            if guess == player_num:
                print("Congratulations! You are on your way to achieving your goal! Keep up the good work champion!")
                correct += 1
            else:
                print("Wrong shmucko! Back to the drawing board. Correct answer was "+player_num)
        games += 1
    print("You got "+str(correct)+" out of "+str(games))
#playing with a specific team selection
else:
    picked_team = team_list[int(team_pick)-1]
    num_games = input('How many games you want shmuckduck?')
    correct = 0
    games = 0
    for game in range(0,int(num_games)):
        team = picked_team
        player_dict = teams[team]
        if list(player_dict.values())[-1]:
            max_num = int(list(player_dict.values())[-1])
        else:
            max_num = int(list(player_dict.values())[-2])  

        selection = random.randint(0,len(player_dict.values()))
        player_name_list = list(player_dict.keys())
        player = player_name_list[selection]
        player_num = player_dict[player]
        if str(player_num) in player_dict.values():
            guess = input(player+' ('+team+')'+': ')
            if guess == player_num:
                print("Congratulations! You are on your way to achieving your goal! Keep up the good work champion!")
                correct += 1
            else:
                print("Wrong shmucko! Back to the drawing board. Correct answer was "+player_num)
        games += 1
    print("You got "+str(correct)+" out of "+str(games))