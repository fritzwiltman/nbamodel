import json

total_win, total_loss, total_push = 0,0,0
team_file = open("teams.txt", "r")
for team in team_file:
    team = "BROOKLYN"
    with open("team_data/{}_data.txt".format(team), "r") as json_file:
        data = json.load(json_file)
        ats_list = data[team][6][1] # ats outcomes of current team in reverse chronological order
        ats_list.reverse() # making order chronological
        win, loss, push, counter, consecutive_outcome = 0, 0, 0, 0, "W"
        print(ats_list)
        # Counting record only after consecutive Ws
        for outcome in ats_list:
            print(consecutive_outcome, outcome, counter, win, loss)

            if outcome == consecutive_outcome:
                counter += 1
            else: counter = 0

            if counter >= 3:
                if outcome == "L":
                    if counter == 3 or counter == 4:    win += 1  
                    elif counter == 5 or counter == 6:  win += 2
                    elif counter > 6:                   win += 3
                    counter = 0
                if outcome == "W":
                    if counter == 3 or counter == 4:    loss += 1
                    elif counter == 5 or counter == 6:  loss += 2
                    elif counter > 6:                   loss += 3
                elif outcome == "P": continue
            else: counter = 0

        print()
        # Now counting record only after consecutive Ls
        counter, consecutive_outcome = 0, "L"
        for outcome in ats_list:
            print(consecutive_outcome, outcome, counter, win, loss)
            if outcome == consecutive_outcome and counter < 3:
                counter += 1
            # else: counter = 0
                
            elif counter >= 3:
                print("here with ", outcome, consecutive_outcome)
                if outcome == "W":
                    if counter == 3 or counter == 4:    win += 1  
                    elif counter == 5 or counter == 6:  win += 2
                    elif counter > 6:                   win += 3
                    counter = 0
                elif outcome == "L":
                    # print("here")
                    if counter == 3 or counter == 4:    loss += 1
                    elif counter == 5 or counter == 6:  loss += 2
                    elif counter > 6:                   loss += 3
                elif outcome == "P": continue

            else: counter = 0
        total_win += win
        total_loss += loss
        total_push = push
        print("{} win-loss-push: {}-{}-{}".format(team,win,loss,push))

print("Total win-loss-push: {}-{}-{}".format(total_win,total_loss,total_push))