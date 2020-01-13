import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date
import json
import requests
import lxml.html as lh
import pandas as pd


def create_and_send_email(): 
    fromaddr = "drewpeacockslocks@gmail.com"
    toAddr = ["fgwilt1@gmail.com", "fwiltman@terpmail.umd.edu"]
    # toAddr = ["fgwilt1@gmail.com", "mbrdgrs6@gmail.com", "grant.abrams1@gmail.com", "ken.newmeyer@gmail.com", "jrwilt3@icloud.com", "benborucki13@gmail.com",  "jtoom13@gmail.com", "jacklombardo17@gmail.com", "rileycollins8244@gmail.com"]
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = ', '.join(toAddr)
    subject = create_subject_header()
    msg['Subject'] = subject
    # plain_body = create_plain_body()
    html_body = create_html_body()
    plain_body = "BODY"
    msg.attach(MIMEText(html_body, 'html'))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, "jtJGSVhyse9rzsV3")
    text = msg.as_string()
    server.sendmail(fromaddr, toAddr, text)
    server.quit()


def create_subject_header():
    today = date.today()
    d = today.strftime("%B %d, %Y")
    full_subject_header = "Drew Peacock's NBA Locks - " + d
    # print(full_subject_header)
    return full_subject_header


def create_plain_body():
    teams_due_for_win = "Teams due for a win:\n"
    with open('teamstobeton.txt', 'r+') as json_file:
        data = json.load(json_file)
        for team in data["due_for_win"]:
            teams_due_for_win += "\t"
            # print(data["due_for_win"][team])


def create_html_body():
    teams_due_for_win = []
    teams_due_for_loss = []
    with open('teamstobeton.txt', 'r+') as json_file:
        data = json.load(json_file)                
        for team in data["due_for_win"]:
            next_game = get_next_game(team)
            formatted_team = "<li>{} has lost {} in a row.<br>{}.<br>{}.</li><br>".format(team, data["due_for_win"][team], get_recommended_units(int(data["due_for_win"][team])), next_game)
            teams_due_for_win.append(formatted_team) 

        for team in data["due_for_loss"]:
            next_game = get_next_game(team)
            formatted_team = "<li>{} has won {} in a row.<br>{}.<br>{}.</li><br>".format(team, data["due_for_loss"][team], get_recommended_units(int(data["due_for_loss"][team])), next_game)
            teams_due_for_loss.append(formatted_team)

        # teams_due_for_win = sort_games(teams_due_for_win)
        # teams_due_for_loss = sort_games(teams_due_for_loss)

    html = """\
    <html>
    <head></head>
    <body>
        <h1 style="text-align:center">Drew Peacock's NBA Locks</h1><br>
        <h2>Teams due for a win</h2>
        <ul>
            {}
        </ul>
        <h2>Teams due for a loss</h2>
        <ul>
            {}
        </ul><br>
        <!-- <h4>Currently under implementation:</h4>
        <ul>
            <li>Overall season record (unit-based) using this method. Trying to finish this by Thursday afternoon.</li>
            <li>Info about yesterday's picks and their outcome.</li>
            <li>Organizing games that are today versus games that are upcoming.</li>
            <li>If a team is due for a win or loss and playing a team that is due for the same outcome, making an obvious note of that when added to the list.</li>
        </ul> -->
    </body>
    </html>
    """.format(sort_games(teams_due_for_win), sort_games(teams_due_for_loss))

    return html


def sort_games(games_list):
    game_today = ""
    game_upcoming = ""
    for team in games_list:
        if "TODAY" in team:
            game_today += team
        else: game_upcoming += team
    all_games = game_today + game_upcoming
    return all_games


def get_recommended_units(consecutive_outcomes):
    recommended_units_string = "Recommended wager: "
    if (consecutive_outcomes <= 4): recommended_units_string += "1 unit"
    elif (consecutive_outcomes == 5 or consecutive_outcomes == 6): recommended_units_string += "2 units"
    else: recommended_units_string += "3 units"
    return recommended_units_string


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

            if next_game[0][1][0] == date.today().strftime("%m/%d"):
                message = "Next game <u><strong>(TODAY)</strong></u>: " + " " + next_game[0][1][0] + " " + next_game[1][1][0] + " " + next_game[2][1][0]
            else: 
                message = "Next game: " + " " + next_game[0][1][0] + " " + next_game[1][1][0] + " " + next_game[2][1][0]
            
            return message

        except:
            continue
        break