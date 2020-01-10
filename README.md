# nbamodel
*I have not proofread this one bit, so if it makes zero sense just text me. The comments in the actual code should also help out a bit.*

## Downloading a copy of this project
You can either download a copy of this project as a zip, somewhere in the top right, or actually clone the repo so you can make commits. For right now, just download the zip and open the project that way. I can show you how to clone the repo and make your own branch if you want help with that.


## Explanation of the current project structure
Everything runs through the `main()` funciton in `run.py`. 
The primary function of this project is to scan every NBA team's game log for the 2019-2020 season, save each team's updated game log in separate text files, be analyzed to make betting predictions, and finally email recepients the "algorithm's" picks (this isn't the most statistically-backed algorithm, by any means). To run the entire thing, simply run `python3 run.py` inside the main directory.


##  Workflow of project
`main()` in `run.py` will call every other script in this project package at some point with the current setup of the project. 
1. Checks if the most recent scan was today (it checks the `LAST_SCAN`attribute attached to every team file)
2. If the most recent scan was not today, then it will scan each team's current season game log, updating the team_data files for each team.
    * A `TeamDataLog` object is created, which lives in the `nbabettingmodel.py` file, and for each team it scans it's current game log, updating its respective file in the `team_data` directory.
3. After collecting each team's most recent data, the script in `teamanalysis.py` will be run for each team. In that script, it will count consecutive ats outcomes for every team. If a team has won or lost 3+ consecutive games against the number, it is added to the `teamstobeton.txt` file. 
    * The structure of `teamstobeton.txt` is a dictionary where there are two main keys: `teams_due_for_win` and `teams_due_for_loss`. Teams due for one or the other will be added as values to those keys. The teams also are keys themselves, mapping to the number of consecutive outcomes it has produced.
4. Finally, the `emailsender.py` is called, which will go through each team due for a win and loss and will construct a message of HTML structure including the teams next game (date, time, opponent), and automatically sends the email to a list of recipients who have requested the daily email.

* `seasonanalysis.py` is a file to analyze this method and get an accurate success rate. Currently under production, it is producing incorrect results still.

* Currently building an AWS Lambda to automatically run the `main()` method daily so it does not have to be run manually. Springing a cron expression is an alternative to automatically running these scripts, but that is run through a user's system, and is dependent on the machine being alive, other factors.


## Using `nbabettingmodel.py` to gather different types of data
Analyzing this stuff comes in two steps - actually collecting the data and storing it so it is easily accessible, then going through your means of storing it and analzying the numbers. This is the first, collecting the data.

This file create an object that takes in a team name, and currently it just collects data on that team based on the url it is plugged into (`team_url` in the `data_collection()` method). In the current case, this collects the game log from each team's current season. If you want to get a different season's data, simply change the url to your liking. For example, if you wanted to get every team's 2018-2019 game log, you just need to simply change the year in the url to 2019. You can browse [Don Best](donbest.com) and look through all kinds of information. Typically, I go to a sport I am trying to analyze, then go to ATS stats, and navigate through there.

This module utilizes the `pandas` data analysis library to actually parse through the information and save data in an easy-to-parse list. In this script, it parses through the HTML source code of the given url, and for anything between the `tr` elements (table row), it will save into a list (`tr_elements`). If I were to save this who list, it would include stuff I don't necessarily want at the moment, like the upcoming games, division standings, injuries, etc. 

To get just the game log I want, I have to go to the 32nd element of `tr_elements`, and take the rest of the table row elements too. `tr_elements[31]` are the column headers, like opponent, date, spread, etc (look at the actual web page if this doesn't make sense). So, I make a list of size 14 - an entry representing each column header. In each entry there is another list; the first element being the string of the column header, and the second element being the list of each entry in that column. *It is possible to map the name of the column header to the list of its entries, it's personal preference and how you feel comfortable accessing data for future use.*

The for-loop around line 50 in the code goes through each row from entry 32 until the end of the table. Again, entry 32 is the most-recent game log. For each row, it will populate the game_log list initialized previously. Once this list is created, it will creates a map of the team name to the actual list, and that map is then dumped into a json file in the `/team_data/TEAM_NAME_data.txt` directory. It will also add a key-value pair of `LAST_SCAN` to today's date in the form of "MM/DD". So, the structure of each file will roughly look like:
      
      {team_name: [ [column_header, [entry_value0, entry_value1, ... entry_valuen]]], LAST_SCAN: "MM/DD"}

Just a disclaimer - the reason I add a last scan element to each file is to avoid having to pull this data every time I want to run any kind of test. I collect the data once, then I am done with it. Opening and reading a file is wayyy faster than contacting 30 different urls, parsing each one's source code, and then analyzing it that way. 


## Using `teamanalysis.py` to actually analyze the data you pulled
This is the second part: analyzing the data. Now you have all your data scraped and neatly placed into the `team_data` directory. Great. Now how do you actually parse through all those files?
In my `main()` method, I iterate through each team, and run an analysis on that team calling the `team_analysis(team_name)` method each iteration. The high-level idea of analyzing one of these files is opening the file, storing the data into a variable, and parsing through the map you stored in some variable.

In the current script, all I really care about is a team's ats record. I just look and see if there are 3+ consecutive Ws or Ls, if so I add that team to the `teamstobeton.txt`. So, the only list I parse through is `data[team_name][6][1]`. `data` is my variable that saves the json_file. Element 6 contains the array of size 2, with the first element being the column header, in this case "ats", and the second element being the list of every ats outcome.

I create a list of teams due for a win and loss, then push those into the `teamstobeton.txt` file.
