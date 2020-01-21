import requests
import lxml.html as lh
import pandas as pd
import json
from datetime import date

class TeamDataLog:
    def __init__(self, team_name):
        # super().__init__()
        self.team_name = team_name
        self.game_log = [] # list of game objects where 'played' is true; in chronological order (by the instance-attribute 'date')
        self.next_games = [] # list of 7 upcoming games where 'played' atrribute is false
        self.due_for_win = None # true is due for win. If true, due_for_loss must inherently be false
        self.due_for_loss = None # true if due for loss. If true, due_for_win must inherently be false


    def data_collection(self):
        counter = 0
        while counter < 8:
            counter += 1
            try:
                team_url = 'http://www.donbest.com/nba/ats-stats/?page=nba/nbateam&teamid={}&season=2020'.format(self.team_name)
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
                self.game_log = game_log
                team_map = {self.team_name: self.game_log}
                today = date.today()
                d = today.strftime("%m/%d")
                team_map["LAST_SCAN"] = d

                # Dumping the team map of team_name: game_log to json file
                with open('/Users/Fritz/Fritz/SoftwareDev/nba_cover_checker/team_data/{}_data.txt'.format(self.team_name.strip()), 'w+') as outfile:
                    json.dump(team_map, outfile)

            except:
                continue
            break