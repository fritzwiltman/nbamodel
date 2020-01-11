import requests
import lxml.html as lh
import pandas as pd
import json
from datetime import date
import os


def data_collection(team_name, year):
    counter = 0
    while counter < 8:
        counter += 1
        try:
            team_url = 'http://www.donbest.com/nba/ats-stats/?page=nba/nbateam&teamid={}&season={}'.format(team_name, year)
                # Create a handle, page, to handle the contents of the website
            page = requests.get(team_url)

            # Store the contents of the website under doc
            doc = lh.fromstring(page.content)

            # Parse data that are stored between <tr>..</tr> of HTML
            tr_elements = doc.xpath('//tr')

            # Check the length of the first 50 rows - use this to see where the different tables are located
            # print([len(T) for T in tr_elements[:50]])

            # Create empty game log list of 2020 season for team
            game_log = []
            i = 0

            # For each row, store each first element (header) and an empty list
            for t in tr_elements[31]:
                i += 1
                name = t.text_content()
                # print('%d:"%s"'%(i,name))

                # Remove any unicode spaces
                try: name = name.replace(u'\xa0', u'')
                except: pass
                game_log.append((name, []))

            for j in range(32, len(tr_elements)):
                T = tr_elements[j]

                # If row is not of size 14, the //tr data the game log we are searching for
                if len(T) != 14: break

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
                    game_log[i][1].append(data)
                    i += 1
            
            # Storing game_log then mapping the team name to game_log used to dump to json file
            team_map = {team_name: game_log}
            today = date.today()
            d = today.strftime("%m/%d")
            team_map["LAST_SCAN"] = d

            
            # Dumping the team map of team_name: game_log to json file to specified directory
            file_directory_name = "yearly_data/{}/{}_data.txt".format(year, team_name)
            os.makedirs(os.path.dirname(file_directory_name), exist_ok=True) # Checks if the directory exists - if not, creates it
            with open(file_directory_name, 'w') as outfile:
                json.dump(team_map, outfile)

        except:
            continue
        break


def main():
    print("running yearly analysis collection")
    # data_collection("ATLANTA", 2019)
    # data_collection("ATLANTA", 2020)

    # If you want to run this on every team for the last five years, loop through every team,
    # and do it 5 times, incrementing the outerloop and adding that incrementer to the year
    # starting in 2015. Uncomment line 98 to have it actually run.
    incrementer = 0
    while incrementer < 5:
        team_file = open("teams.txt", "r")
        year = 2015
        for team in team_file:
            team = team.strip() # each line holds a newline character at the end that must be removed when put into url
            print("Gathering {} information from {}".format(year + incrementer, team))
            # data_collection(team, year + incrementer)
        incrementer += 1


if __name__ == '__main__':
    main()