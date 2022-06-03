"""
Baseball Model

Authors: CTB & JES

First draft: June 2021
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin
from urllib.request import urlretrieve
import os
import shutil
import time
import pandas as pd
import mlbgame as mlb
from datetime import date, timedelta
import numpy as np

from baseball_model_functions import *

# get today's date
today = date.today()
today_formatted = today.strftime("%Y-%m-%d")
ten_days_ago = today - timedelta(days=10)
ten_days_ago_formatted = ten_days_ago.strftime("%Y-%m-%d")
year = today.year
month = today.month
day = today.day
print(today_formatted, 'Schedule:\n')
# get today's games
games_today = mlb.day(year=year, month=month, day=day)
# make each game a nested list
schedule = []
for game in games_today:
    schedule.append([game.home_team, game.away_team])
print(schedule, '\n')
# initialize firefox browser session
# set up the firefox profile so that we don't have to click on the download pop-up and choose our download folder
profile = webdriver.FirefoxProfile()
profile.set_preference("browser.download.panel.shown", False)
profile.set_preference("browser.download.folderList", 2)
profile.set_preference("browser.download.manager.showWhenStarting", False)
dl_path = '/Users/chadbloxham/Downloads/fangraphs/'
today_path = dl_path + today_formatted # folder specifically for our fangraphs .csv downloads
if not os.path.isdir(today_path):
    os.mkdir(today_path)
profile.set_preference("browser.download.dir", today_path)
profile.set_preference("browser.helperApps.neverAsk.openFile","text/csv,application/vnd.ms-excel,application/csv")
profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv,application/vnd.ms-excel,application/csv")
# create the firefox browser session
driver = webdriver.Firefox(executable_path="/Applications/geckodriver", firefox_profile=profile)
wait = WebDriverWait(driver, 10)
# advanced_pitch_url = "https://www.fangraphs.com/leaders.aspx?pos=all&stats=pit&lg=all&qual=0&type=1&season=2021&month=0&season1=2021&ind=0&team=0&rost=0&age=0&filter=&players=p" + today_formatted
advanced_pitch_url = 'https://www.fangraphs.com/leaders.aspx?pos=all&stats=pit&lg=all&qual=0&type=1&season=' + str(year) + '&month=0&season1=' + str(year) + '&ind=0&team=0&rost=0&age=0&filter=&players=p' + today_formatted
driver.get(advanced_pitch_url)
# execute the javascript code which downloads the table as a csv
advanced_pitch_javascript = "__doPostBack('LeaderBoard1$cmdCSV','')"
wait.until(EC.element_to_be_clickable((By.ID, 'LeaderBoard1_cmdCSV')))
driver.execute_script(advanced_pitch_javascript)
# wait a moment so that the new file can arrive before renaming
time.sleep(1)
# rename the newest file in Downloads/fangraphs
filename = max([today_path + "/" + f for f in os.listdir(today_path)],key=os.path.getctime)
advanced_pitch_name = today_path + "/advanced_pitch_" + today_formatted + ".csv"
shutil.move(filename, advanced_pitch_name)

# the splitArr option can be set to get batting statistcs against LHP or RHP
lhp = 1
rhp = 2
hands = [lhp, rhp]
bat_names = []
for left_or_right in hands:
    # advanced_bat_url = "https://www.fangraphs.com/leaders/splits-leaderboards?splitArr=" + str(left_or_right) + "&splitArrPitch=&position=B&autoPt=false&splitTeams=false&statType=team&statgroup=2&startDate=2021-03-01&endDate=2021-11-01&players=&filter=&groupBy=season&sort=-1,1"
    advanced_bat_url = 'https://www.fangraphs.com/leaders/splits-leaderboards?splitArr=' + str(left_or_right) + '&splitArrPitch=&position=B&autoPt=false&splitTeams=false&statType=team&statgroup=2&startDate=' + str(year) + '-03-01&endDate=' + str(year) + '-11-01&players=&filter=&groupBy=season&sort=-1,1'
    driver.get(advanced_bat_url)
    export_data_button = driver.find_elements_by_class_name("data-export")[0]
    export_data_url = export_data_button.get_attribute('href')
    csv_url = urljoin(advanced_bat_url, export_data_url)
    wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'data-export')))
    if left_or_right == lhp:
        hand = 'LHP'
    else:
        hand = 'RHP'
    csv_name = today_path + '/advanced_bat_' + hand + '_' + today_formatted + '.csv'
    bat_names.append(csv_name)
    urlretrieve(csv_url, csv_name)

recent_bat_url = 'https://www.fangraphs.com/leaders/splits-leaderboards?splitArr=&splitArrPitch=&position=B&autoPt=false&splitTeams=false&statType=team&statgroup=2&startDate=' + ten_days_ago_formatted + '&endDate=' + today_formatted + '&players=&filter=&groupBy=season&sort=-1,1'
driver.get(recent_bat_url)
export_data_button = driver.find_elements_by_class_name("data-export")[0]
export_data_url = export_data_button.get_attribute('href')
csv_url = urljoin(recent_bat_url, export_data_url)
wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'data-export')))
recent_bat_csv_name = today_path + '/recent_advanced_bat_' + today_formatted + '.csv'
urlretrieve(csv_url, recent_bat_csv_name)

depth_chart_url = 'https://www.fangraphs.com/depthcharts.aspx?position=RP'
driver.get(depth_chart_url)
depth_chart_headers = driver.find_elements_by_class_name('tablesorter-header-inner')[-5:]
depth_chart = driver.find_elements_by_class_name('depth_team')

headers = []
for item in depth_chart_headers:
    headers.append(item.text)

i = 0
depth_chart_csv = today_path + '/depth_chart_' + today_formatted + '.csv'
f = open(depth_chart_csv, 'w')
for header in headers:
    f.write(header)
    if i == 4:
        f.write('\n')
        i = 0
    else:
        f.write(',')
        i += 1

for team_row in depth_chart:
    tds = team_row.find_elements_by_tag_name('td')
    i = 0
    for td in tds:
        f.write(td.text)
        if i == 4:
            f.write('\n')
        else:
            f.write(',')
            i += 1

f.close()

advanced_pitch_df = pd.read_csv(advanced_pitch_name)
advanced_bat_lhp_df = pd.read_csv(bat_names[0])
advanced_bat_rhp_df = pd.read_csv(bat_names[1])
recent_bat_df = pd.read_csv(recent_bat_csv_name)
depth_chart_df = pd.read_csv(depth_chart_csv)
pitcher_hands_df = pd.read_csv(dl_path + '/pitcher_hands.csv')
team_abbrev_df = pd.read_csv(dl_path + '/team_abbreviations.csv')
non_pitchers_df = pd.read_csv(dl_path + '/non_pitchers.csv')
# print(recent_bat_df)
"""
Get the probable pitcher and get their xFip, SIERA, K%, and HR9. Then, look up RHP or LHP, then go into batting
stats and get opposing team's wRC+, K%, and ISO.
"""
j = 1
for game in schedule:
    print('GAME', j, ':', game[0], 'vs', game[1], '\n')
    for i in range(len(game)):
        team = game[i]
        if i == 0:
            opposing_team = game[i+1]
        else:
            opposing_team = game[i-1]
        # see comment above
        print(team, ':\n')
        team_abbrev = team_abbrev_df[team_abbrev_df['team'] == team]['abbreviation'].iloc[0]
        opp_abbrev = team_abbrev_df[team_abbrev_df['team'] == opposing_team]['abbreviation'].iloc[0]
        opposing_pitchers = advanced_pitch_df[advanced_pitch_df['Team'] == opp_abbrev]['Name']
        # apparently there can be multiple probable pitchers
        for i in range(len(opposing_pitchers.index)):
            is_pitcher = False
            pitcher = opposing_pitchers.iloc[i]
            # print(pitcher)
            pitcher_stats = advanced_pitch_df[advanced_pitch_df['Name'] == pitcher][['xFIP', 'SIERA', 'K%', 'HR/9', 'playerid']].iloc[0]
            player_id = pitcher_stats['playerid']
            if pitcher in pitcher_hands_df.pitcher.unique():
                is_pitcher = True
            elif pitcher not in non_pitchers_df.player.unique():
            # if pitcher not in pitcher_hands_df.pitcher.unique() and pitcher not in non_pitchers_df.player.unique():
                # DO need to fetch LHP/RHP from fangraphs
                lowercase_pitcher = pitcher.lower()
                lowercase_pitcher = lowercase_pitcher.replace('.', '')
                lowercase_pitcher_sep = lowercase_pitcher.split(' ')
                pitcher_name = lowercase_pitcher[0] + '-' + lowercase_pitcher[1]
                player_url = 'https://www.fangraphs.com/players/' + pitcher_name + '/' + str(player_id)
                driver.get(player_url)
                plyr_pos = driver.find_elements_by_class_name("player-info-box-pos")[0]
                plyr_pos = plyr_pos.get_attribute('innerHTML')
                # print(plyr_pos)
                if plyr_pos == 'P':
                    # print("ADDED to Pitcher Table")
                    is_pitcher = True
                    plyr_items = driver.find_elements_by_class_name("player-info-box-item")
                    bats_throws = plyr_items[1].get_attribute('innerHTML').split('/')
                    pitcher_hand = bats_throws[2]

                    # need to add to the pitcher hands dataframe
                    num_pitchers = len(pitcher_hands_df.index)
                    pitcher_hands_df.loc[num_pitchers] = [pitcher, pitcher_hand]
                else:
                    # print("ADDED to Non-Pitcher Table")
                    num_non_pitchers = len(non_pitchers_df.index)
                    non_pitchers_df.loc[num_non_pitchers] = [pitcher]

            if is_pitcher:
                # DON'T need to fetch LHP/RHP from fangraphs
                pitcher_hand = pitcher_hands_df[pitcher_hands_df['pitcher'] == pitcher]['left_right'].iloc[0]
                print('Opposing Pitcher (Probable):', pitcher)
                print('Throws:', pitcher_hand)
                xFIP = pitcher_stats['xFIP']
                print('xFIP:', xFIP)
                SIERA = pitcher_stats['SIERA']
                print('SIERA:', SIERA)
                k_perc = pitcher_stats['K%']
                print('K%:', k_perc)
                HR9 = pitcher_stats['HR/9']
                print('HR/9:', HR9)
                if opposing_team == 'Indians':
                    rp_war = depth_chart_df[depth_chart_df['Team'] == 'Cleveland']['WAR'].iloc[0]
                elif opposing_team == 'D-backs':
                    rp_war = depth_chart_df[depth_chart_df['Team'] == 'Diamondbacks']['WAR'].iloc[0]
                else:
                    rp_war = depth_chart_df[depth_chart_df['Team'] == opposing_team]['WAR'].iloc[0]
                print(opposing_team, 'RP WAR:', rp_war, '\n')
                hand_str = pitcher_hand + 'HP'
                # get batting stats
                print(team, 'Batting Stats Against', hand_str, ':')
                if pitcher_hand == 'R':
                    bat_stats = advanced_bat_rhp_df[advanced_bat_rhp_df['Tm'] == team_abbrev][['wRC+', 'K%', 'ISO']].iloc[0]
                else:
                    bat_stats = advanced_bat_lhp_df[advanced_bat_lhp_df['Tm'] == team_abbrev][['wRC+', 'K%', 'ISO']].iloc[0]
                wrc_p = bat_stats['wRC+']
                print('wRC+:', wrc_p)
                k_perc_hit = bat_stats['K%']
                print('K%:', k_perc_hit)
                iso = bat_stats['ISO']
                print('ISO:', iso)
                rec_wrc_p = recent_bat_df[recent_bat_df['Tm'] == team_abbrev]['wRC+'].iloc[0]
                print('Recent wRC+ (since', ten_days_ago_formatted, '):', rec_wrc_p)

                """
                STEINY FUNCTIONS START. Plug the variables created above - xFIP, SIERA, etc. into your functions
                imported from baseball_model_functions.py
                """

                #Create numbers
                weather_stad = 1.0
                siera_xfip = xfipsiera_num(xFIP,SIERA,weather_stad,wrc_p)
                print('\nGame number (custom stat):', siera_xfip)

                # convert k_perc from string to float. Remove percentage character first
                k_perc = k_perc[:-1]
                k_perc = np.float64(k_perc)
                strike_out = k_rate(k_perc,k_perc_hit)
                print('K-Rate (custom stat):',strike_out)

                """
                STEINY FUNCTIONS END.
                """

        print('\n')
    j += 1
    print('\n')


pitcher_hands_df.to_csv(dl_path + '/pitcher_hands.csv', index=False)
non_pitchers_df.to_csv(dl_path + '/non_pitchers.csv', index=False)
# close firefox browser window and quit engine
driver.close()
driver.quit()
