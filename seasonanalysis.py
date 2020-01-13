import json

total_win, total_loss, total_push = 0,0,0
team_file = open("teams.txt", "r")
for team in team_file:
    team = team.strip()
    with open("team_data/{}_data.txt".format(team), "r") as json_file:
        data = json.load(json_file)
        ats_list = data[team][6][1] # ats outcomes of current team in reverse chronological order
        ats_list.reverse() # making order chronological
        win, loss, push, counter, consecutive_outcome = 0, 0, 0, 0, "W"
        print(ats_list)

        # Counting record only after consecutive Ws
        for outcome in ats_list:
            print(consecutive_outcome, outcome, counter, win, loss)            
            if outcome == "L":
                print("outcome: " + outcome + " counter : {}".format(counter))
                if counter == 3 or counter == 4:    win += 1  
                elif counter == 5 or counter == 6:  win += 2
                elif counter > 6:                   win += 3
                counter = 0
            if outcome == "W":
                if counter == 3 or counter == 4:    loss += 1
                elif counter == 5 or counter == 6:  loss += 2
                elif counter > 6:                   loss += 3
                counter += 1
            elif outcome == "P": continue


        print()
        # Now counting record only after consecutive Ls
        counter, consecutive_outcome = 0, "L"
       
        for outcome in ats_list:
            print(consecutive_outcome, outcome, counter, win, loss)            
            if outcome == "W":
                print("outcome: " + outcome + " counter : {}".format(counter))
                if counter == 3 or counter == 4:    win += 1  
                elif counter == 5 or counter == 6:  win += 2
                elif counter > 6:                   win += 3
                counter = 0
            if outcome == "L":
                if counter == 3 or counter == 4:    loss += 1
                elif counter == 5 or counter == 6:  loss += 2
                elif counter > 6:                   loss += 3
                counter += 1
            elif outcome == "P": continue
        total_win += win
        total_loss += loss
        total_push = push
        print("{} win-loss-push: {}-{}-{}".format(team,win,loss,push))
    

print("Total win-loss-push: {}-{}-{}".format(total_win,total_loss,total_push))
print("Assuming a price of -110 for each bet, and you bet a $10 unit at that price, here is the actual outcome: ")
actual_win = win * 9.09
actual_loss = loss * 10
outcome = actual_win - actual_loss
success_rate = 100*win/(win+loss)

if outcome > 0:
    print('+%.3f'%(outcome), " Success rate: {}%".format(success_rate))
else: 
    print('%.3f'%(outcome), " Success rate: {}%".format(success_rate))