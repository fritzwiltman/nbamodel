from nbabettingmodel import TeamDataLog
import teamanalysis as ta
import emailsender
import json
from datetime import date
import time

#########################################################################
# run.py iterates through each team in the teams.txt file, and gather   #
# each team's game log data and store them in a global dictionary.      #
#                                                                       #
# Will eventually have to store the game log info in a database.        #
#########################################################################

# Dictionary to hold game log of each team
team_game_log_dictionary = {}

def gather_team_game_logs():
    teams_file = open("teams.txt", "r")
    for team in teams_file.readlines():
        print(team)


def main():
    print("Gathering information on each team...")

    # Checking to see when last scan was; if not today, then it will re-scan
    with open("team_data/ATLANTA_data.txt", "r") as json_file:
        data = json.load(json_file)
        if "LAST_SCAN" in data:
            last_scan = data["LAST_SCAN"]
        else: 
            last_scan = ""

    # Getting today's date to compare to the last scan's date
    today = date.today()
    d = today.strftime("%m/%d")

    # Need to add error handling to nbabettingmodel.py when gathering data
    if last_scan != d:
        team_file = open("teams.txt", "r")
        for team in team_file:
            time.sleep(.300)
            team = team.strip()
            print("Gathering information from {}".format(team))
            team_data = TeamDataLog(team)
            team_data.data_collection()


    print("Analyzing each team's recent games...")
    with open("teamstobeton.txt", "r") as json_file:
        data = json.load(json_file)
        team_file = open("teams.txt", "r")
        for team in team_file:
            team = team.strip()
            ta.team_analysis(team)

    print("Sending emails with new information...")
    emailsender.create_and_send_email()

    print("Done")

if __name__ == '__main__':
    main()