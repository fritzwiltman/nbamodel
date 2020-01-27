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
    toAddr = ""
    bcc = ['fgwilt1@gmail.com', 'drewpeacockslocks@gmail.com', "fwiltman@umd.edu"]
    bcc = ["fgwilt1@gmail.com", "vrwilt1@gmail.com", "air.land96@gmail.com", "mbrdgrs6@gmail.com", "grant.abrams1@gmail.com", "ken.newmeyer@gmail.com", "jrwilt3@icloud.com", "benborucki13@gmail.com",  "jtoom13@gmail.com", "jacklombardo17@gmail.com", "rileycollins8244@gmail.com"]
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toAddr
    subject = create_subject_header()
    msg['Subject'] = subject
    html_body = create_html_body()
    msg.attach(MIMEText(html_body, 'html'))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, "jtJGSVhyse9rzsV3")
    text = msg.as_string()
    server.sendmail(fromaddr, bcc + [toAddr], text)
    server.quit()


def create_subject_header():
    today = date.today()
    d = today.strftime("%B %d, %Y")
    full_subject_header = "Drew Peacock's NBA Locks - " + d
    return full_subject_header


def create_html_body():
    teams_due_for_win = []
    teams_due_for_loss = []
    with open('/Users/Fritz/Fritz/SoftwareDev/nba_cover_checker/teamstobeton.txt', 'r+') as json_file:
        data = json.load(json_file)                
        for team in data["due_for_win"]:
            next_game = data["due_for_win"][team][1][0]
            next_opponent = data["due_for_win"][team][1][1]
            if next_opponent in data["due_for_win"]:
                formatted_team = "<li>{} has lost {} in a row, but playing {} who is also due for a win. <br>Recommended wager: <strong>Fade this game</strong>.</li><br>"\
                    .format(team, data["due_for_win"][team][0], next_opponent)
            elif next_opponent in data["due_for_loss"]:
                next_opp_losses = int(data["due_for_loss"][next_opponent][0])
                formatted_team = "<li>{} has lost {} in a row.<br>Their next opponent, {}, has won {} in a row and is due for a loss.<br>{}.<br>{}.</li><br>"\
                    .format(team, data["due_for_win"][team][0], next_opponent, next_opp_losses, \
                    (get_recommended_units_for_double_bet(int(data["due_for_win"][team][0]), next_opp_losses)), next_game)
            else:
                formatted_team = "<li>{} has lost {} in a row.<br>{}.<br>{}.</li><br>"\
                    .format(team, data["due_for_win"][team][0], get_recommended_units(int(data["due_for_win"][team][0])), next_game)
            teams_due_for_win.append(formatted_team) 

        for team in data["due_for_loss"]:
            next_game = data["due_for_loss"][team][1][0]
            next_opponent = data["due_for_loss"][team][1][1]
            if next_opponent in data["due_for_loss"]:
                formatted_team = "<li>{} has won {} in a row, but playing {} who is also due for a loss. <br>Recommended wager: <strong>Fade this game</strong>.</li><br>"\
                    .format(team, data["due_for_loss"][team][0], next_opponent)
            elif next_opponent in data["due_for_win"]:
                next_opp_losses = int(data["due_for_win"][next_opponent][0])
                formatted_team = "<li>{} has won {} in a row.<br>Their next opponent, {}, has lost {} in a row and is due for a win.<br>Recommended wager: \
                    Wager is listed above in <strong>\"Teams due for win\"</strong> list under {}.<br>{}.</li><br>"\
                    .format(team, data["due_for_loss"][team][0], next_opponent, next_opp_losses, next_opponent, next_game)
            else:
                formatted_team = "<li>{} has won {} in a row.<br>{}.<br>{}.</li><br>"\
                    .format(team, data["due_for_loss"][team][0], get_recommended_units(int(data["due_for_loss"][team][0])), next_game)
            teams_due_for_loss.append(formatted_team)

    no_games_prompt = ""
    no_games_today_win = True
    no_games_today_loss = True
    for line in teams_due_for_win:
        if "TODAY" in line:
            no_games_today_win = False
            break
    for line in teams_due_for_loss:
        if "TODAY" in line:
            no_games_today_loss = False
            break
    if no_games_today_win and no_games_today_loss:
        print("No games today!")
        no_games_prompt = "<h2 style=\"color:red; text-align:center\"><i><strong><u>There are no games scheduled for today that I recommend wagering.</u></strong></i></h2><br>"

    html = """\
    <html>
    <head></head>
    <body>
        <h1 style="text-align:center">Drew Peacock's NBA Locks</h1><br>
        {}
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
    """.format(no_games_prompt, sort_games(teams_due_for_win), sort_games(teams_due_for_loss))

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


def get_recommended_units_for_double_bet(consecutive_outcomes1, consecutive_outcomes2):
    recommended_units_string = "Recommended wager: <strong>(Double Wager) </strong>"
    total_outcomes = consecutive_outcomes1 + consecutive_outcomes2
    if (total_outcomes <= 7): recommended_units_string += "2 units"
    elif (8 < total_outcomes <= 10): recommended_units_string += "3 units"
    else: recommended_units_string += "4 units"
    return recommended_units_string
