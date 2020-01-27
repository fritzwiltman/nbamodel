import json
from datetime import date
import requests
import lxml.html as lh
import pandas as pd
from nbabettingmodel import TeamDataLog

def team_analysis(team_name):
    # print("Analyzing {}".format(team_name))
    ats_list = []
    # Opening the team_name_data text file and saving the ats results in ats_list
    with open('team_data/{}_data.txt'.format(team_name.strip())) as json_file:
        data = json.load(json_file)
        if 6 < len(data[team_name]) and 1 < len(data[team_name][6]):
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
                    data["due_for_win"][team_name] = [consecutive_outcomes]     
                    data["due_for_win"][team_name].append(get_next_game(team_name))
                elif latest_outcome == "W":
                    data["due_for_loss"][team_name] = [consecutive_outcomes]
                    data["due_for_loss"][team_name].append(get_next_game(team_name))


            json_file.seek(0)  # rewind to first line and character, rewrite entire file
            json.dump(data, json_file)
            json_file.truncate()

    except IOError:
        print(IOError)


def get_next_game(team_name):
    while True:
        try:
            team_url = 'http://www.donbest.com/nba/ats-stats/?page=nba/nbateam&teamid={}&season=2020'.format(team_name)
            
            # Create a handle, page, to handle the contents of the website
            page = requests.get(team_url)

            # Store the contents of the website under doc
            doc = lh.fromstring(page.content)

            # Parse data that are stored between <tr>..</tr> of HTML
            tr_elements = doc.xpath('//tr')

            # Create empty string to hold next game info
            next_game = []
            i=0
            sanity_check = ""
            inc = 0

            while sanity_check != "Date":
                inc += 1
                if inc > 10: break
                next_game = []
                # For each row, store each first element (header) and an empty list
                for t in tr_elements[6]:
                    i += 1
                    name = t.text_content()
                    if i == 1: 
                        sanity_check = name

                    # Remove any unicode spaces
                    try: name = name.replace(u'\xa0', u'')
                    except: pass
                    next_game.append((name, []))
                
            for j in range(7, 14):
                T = tr_elements[j]

                # If row is not of size 3, the //tr data the game log we are searching for
                if len(T) != 3: break
                i = 0

                for t in T.iterchildren():
                    data = t.text_content()

                    # Convert numerical values to integers
                    try: data = int(data)
                    except: pass

                    # Replace any unicode spaces with normal spaces
                    try: data = data.replace(u'\xa0', u' ')
                    except: pass

                    # Append the data to the empty list of the i'th column
                    next_game[i][1].append(data)
                    i += 1

            if 'at' or 'vs' in next_game[2][1][0]:
                opponent = next_game[2][1][0].split(" ")
                print(opponent)
                if len(opponent) == 2:
                    opponent_name = opponent[1]
                elif len(opponent) == 3:
                    opponent_name = opponent[1] + "+" + opponent[2]

            if next_game[0][1][0] == date.today().strftime("%m/%d"):
                message = "Next game <u><strong>(TODAY)</strong></u>: " + " " + next_game[0][1][0] + " " + next_game[1][1][0] + " " + next_game[2][1][0]
            else: 
                message = "Next game: " + " " + next_game[0][1][0] + " " + next_game[1][1][0] + " " + next_game[2][1][0]
            
            return (message, opponent_name)

        except:
            continue
        break