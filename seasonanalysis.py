import json

def seasonanalysis(team):
    total_win, total_loss, total_push = 0,0,0
    with open("team_data/{}_data.txt".format(team), "r") as json_file:
        data = json.load(json_file)
        date_list = data[team][0][1] 
        opponent_list = normalize_opponents(data[team][1][1])
        ats_list = data[team][6][1]
        date_list.reverse()         # making the lists' order chronological 
        ats_list.reverse()         
        win, loss, push, date_opp_counter, consecutive_counter, game_date, consecutive_outcome = 0, 0, 0, 0, 0, "", "W"
        # print(team, ats_list, date_list, opponent_list)

        # Counting record only after consecutive Ws
        for outcome in ats_list:
            opp_check = check_opponent(opponent_list[date_opp_counter], date_list[date_opp_counter], False, True)
            print(opponent_list[date_opp_counter], date_list[date_opp_counter])
            print(opp_check)
            # print(consecutive_outcome, outcome, counter, win, loss)   
            if not opp_check[1]: # if opposition is also due for a loss, move on
                if outcome == "L":
                    # check_opponent()
                    if 3 <= consecutive_counter <= 4:
                        win += 1  
                    elif 5 <= consecutive_counter <= 6:
                        win += 2
                    elif consecutive_counter > 6:
                        win += 3
                    consecutive_counter = 0

                if outcome == "W":
                    if 3 <= consecutive_counter <= 4:
                        loss += 1
                    elif 5 <= consecutive_counter <= 6:
                        loss += 2
                    elif consecutive_counter > 6:
                        loss += 3
                    consecutive_counter += 1

                elif outcome == "P": continue
            date_opp_counter += 1

        # Now counting record only after consecutive Ls
        date_opp_counter, consecutive_counter, consecutive_outcome = 0, 0, "L"
    
        for outcome in ats_list:
            opp_check = check_opponent(opponent_list[date_opp_counter], date_list[date_opp_counter], True, False)
            print(opp_check)
            # print(consecutive_outcome, outcome, counter, win, loss)            
            if not opp_check[0]:
                if outcome == "W":
                    if consecutive_counter == 3 or consecutive_counter == 4:    win += 1  
                    elif consecutive_counter == 5 or consecutive_counter == 6:  win += 2
                    elif consecutive_counter > 6:                               win += 3
                    consecutive_counter = 0
                if outcome == "L":
                    if consecutive_counter == 3 or consecutive_counter == 4:    loss += 1
                    elif consecutive_counter == 5 or consecutive_counter == 6:  loss += 2
                    elif consecutive_counter > 6:                               loss += 3
                    consecutive_counter += 1
                elif outcome == "P": continue
            date_opp_counter += 1
        total_win += win
        total_loss += loss
        total_push = push
        # print("{} win-loss-push: {}-{}-{}".format(team,win,loss,push))
        # print("Assuming a price of -110 for each bet, and you bet a $10 unit at that price, here is the actual outcome for {}: ".format(team))
        # team_actual_win = win * 9.09
        # team_actual_loss = loss * 10
        # team_outcome = team_actual_win - team_actual_loss
        # team_success_rate = (100*win)/(win+loss)

    #     if team_outcome > 0:
    #         print('+%.3f'%(team_outcome), " Success rate: %.1f"%(team_success_rate) + "%")
    #     else: 
    #         print('%.3f'%(team_outcome), " Success rate: %.1f"%(team_success_rate) + "%")
    # print()


    # print("Total win-loss-push: {}-{}-{}".format(total_win,total_loss,total_push))
    # print("Assuming a price of -110 for each bet, and you bet a $10 unit at that price, here is the actual outcome: ")
    # actual_win = total_win * 9.09
    # actual_loss = total_loss * 10
    # outcome = actual_win - actual_loss
    # success_rate = 100*total_win/(total_win+total_loss)

    # if outcome > 0: print('+%.3f'%(outcome), " Success rate: %.1f"%(success_rate) + "%")
    # else: print('%.3f'%(outcome), " Success rate: %.1f"%(success_rate) + "%")


# If a team is due for a win or loss, this helper will check that team's history, and 
# check to see if that team is due for a win or loss. Used to check if a team who 
# is due for a specific outcome is playing a team due for the same or opposite outcome.
def check_opponent(team_to_check, date, due_for_win, due_for_loss):
    consecutive_counter = 0
    with open("team_data/{}_data.txt".format(team_to_check), "r") as json_file:
        data = json.load(json_file)

        # Get index of game from given date using list.index(date)
        index_of_game = data[team_to_check][0][1].index(date)
        countdown_index = index_of_game - 1
        ats_list = data[team_to_check][6][1]
        ats_list.reverse()
        # do both if due for win and loss
        if due_for_win:
            # use index to get ats list, and look at the consecutive outcomes backwards
            # use a try/except statement, there is a chance that there are less than 3 outcomes before the one we are looking at
            try:
                while (countdown_index > 0):
                    outcome = ats_list[countdown_index]
                    if outcome == "L":      consecutive_counter += 1
                    if outcome == "W":      break
                    elif outcome == "P":    continue
                    countdown_index -= 1

                if consecutive_counter >= 3: 
                    return (True, False, consecutive_counter) # If a team is due for a win, return a tuple of (due_for_win: boolean, due_for_loss: boolean, consecutive_outcomes: int)
            except: 
                return "not due for win"

        elif due_for_loss:
            try:
                while (countdown_index > 0):
                    outcome = ats_list[countdown_index]
                    if outcome == "W":      consecutive_counter += 1
                    if outcome == "L":      break
                    elif outcome == "P":    continue
                    countdown_index -= 1
                
                    print("counter "+consecutive_counter)
                if consecutive_counter >= 3: 
                    return (False, True, consecutive_counter) # If a team is due for a loss, return a tuple of (due_for_win: boolean, due_for_loss: boolean, consecutive_outcomes: int)
            except:
                return "not due for loss"

        # Use this to determine if that team is due for win or due for loss
        # Might have to return a tuple that includes boolean due_for_win, due_for_loss, and then consecutive_outcomes for units


def normalize_opponents(opponent_list):
    ret_arr = []
    opponent_list.reverse()
    for team in opponent_list:
        opponent = team.split(" ")
        if len(opponent) == 2:
            opponent_name = opponent[1]
        elif len(opponent) == 3:
            opponent_name = opponent[1] + "+" + opponent[2]
        ret_arr.append(opponent_name)
    return ret_arr


def main():
    print("running yearly analysis collection")
    team_file = open("teams.txt", "r")
    for team in team_file:
        team = team.strip()
        seasonanalysis(team)


if __name__ == '__main__':
    main()