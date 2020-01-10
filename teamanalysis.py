import json
from datetime import date
from nbabettingmodel import TeamDataLog

def team_analysis(team_name):
    # print("Analyzing {}".format(team_name))
    ats_list = []
    # Opening the team_name_data text file and saving the ats results in ats_list
    with open('team_data/{}_data.txt'.format(team_name.strip())) as json_file:
        data = json.load(json_file)
        ats_list = data[team_name][6][1]

    # Trying again if the list is messed up until it's not - sometimes there is a rotten data pull in nbabettingmodel.py
    inc = 1
    while ats_list == []:
        team = team_name.strip()
        print("{}. Error in initial scrape. Re-gathering information from {}".format(inc, team))
        team_data = TeamDataLog(team)
        team_data.data_collection()
        inc += 1

        with open('team_data/{}_data.txt'.format(team_name.strip())) as json_file:
            data = json.load(json_file)
            ats_list = data[team_name][6][1]
       
    latest_outcome = ats_list[0] # used to compare consecutive outcomes
    consecutive_outcomes = 0

    # Counting consecutive outcomes, it there is a push just ignore it but don't quit
    for outcome in ats_list:
        if outcome == latest_outcome:
            consecutive_outcomes += 1
            continue
        elif outcome == "P":
            continue
        else:
            break
    # print("consecutive outcomes of {}: {}".format(latest_outcome, consecutive_outcomes))

    try:
        with open("teamstobeton.txt", "r+") as json_file:
            # Must dumps the data back into the file, make sure it removes and repaces, not append
            data = json.load(json_file)

            # If consecutive outcomes is less than 3, remove the team's key from the textfile and data
            if consecutive_outcomes < 3:
                data["due_for_win"].pop(team_name, None)
                data["due_for_loss"].pop(team_name, None)
            else: 
                if latest_outcome == "L":
                    # Shouldnt have to check if team is in this map - if it is, it'll update, if not, it'll be added
                    data["due_for_win"][team_name] = consecutive_outcomes      
                elif latest_outcome == "W":
                    data["due_for_loss"][team_name] = consecutive_outcomes
            
            json_file.seek(0)  # rewind to first line and character, rewrite entire file
            json.dump(data, json_file)
            json_file.truncate()

    except IOError:
        print(IOError)
