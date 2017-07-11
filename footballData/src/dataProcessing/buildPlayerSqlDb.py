import json
import sqlite3
import os
import re 
import xml.etree.ElementTree as ET
import collections 
from datetime import datetime
from datetime import timedelta
from time import strptime
import time
import operator
import sys
import string
from dateutil.parser import parse

#Player files to work with
playersFileDirectory = 'D:\\OneDrive\\Projects\\BettingSerivce\\FootballDataCollection\\footballData\\DATA\\match_error.txt\\players\\'
db = 'D:\\OneDrive\\Projects\\BettingSerivce\\FootballDataCollection\\footballData\\DATA\\database.sqlite'
errorFile = 'D:\\OneDrive\\Projects\\BettingSerivce\\FootballDataCollection\\footballData\\DATA\\match_error.txt'
startIntFifa = 154994
startDateFifa = datetime(2007,2,22)
conn = sqlite3.connect(db)
cur = conn.cursor()

featureField = ['Preferred Foot',
             'Attacking Work Rate',
             'Defensive Work Rate']

generalStatsField = ['Overall rating',
             'Potential']

shortStatsField = ['Crossing',
             'Finishing',
             'Heading Accuracy',
             'Short Passing',
             'Dribbling',
             'Free Kick Accuracy',
             'Long Passing',
             'Ball Control',
             'Acceleration',
             'Sprint Speed',
             'Reactions',
             'Shot Power',
             'Stamina',
             'Strength',
             'Long Shots',
             'Aggression',
             'Interceptions',
             'Positioning',
             'Penalties',
             'Marking',
             'Standing Tackle',
             'GK Diving',
             'GK Handling',
             'GK Kicking',
             'GK Positioning',
             'GK Reflexes']

longStatsField = ['Crossing',
             'Finishing',
             'Heading Accuracy',
             'Short Passing',
             'Volleys',
             'Dribbling',
             'Curve',
             'Free Kick Accuracy',
             'Long Passing',
             'Ball Control',
             'Acceleration',
             'Sprint Speed',
             'Agility',
             'Reactions',
             'Balance',
             'Shot Power',
             'Jumping',
             'Stamina',
             'Strength',
             'Long Shots',
             'Aggression',
             'Interceptions',
             'Positioning',
             'Vision',
             'Penalties',
             'Marking',
             'Standing Tackle',
             'Sliding Tackle',
             'GK Diving',
             'GK Handling',
             'GK Kicking',
             'GK Positioning',
             'GK Reflexes']

def printError(player_name,player_api_id,player_fifa_id,):
    outputFile = open(errorFile,'a')
    url = 'http://sofifa.com/player/' + str(player_fifa_id)
    outputFile.write(str(player_api_id) + ',' + player_name + ',' + url + '\n')  
            
def savePlayer(filename,count):
    underscore = [m.start() for m in re.finditer('_', filename)]
    player_name = filename[:underscore[0]]
    player_api_id = int(filename[underscore[0]+1:underscore[1]])
    player_fifa_api_id = int(filename[underscore[1]+1:-4])
    filePath = playersFileDirectory + filename
    
    playerStats = ''
    with open(filePath,'r') as file_Player:
        count += 1
        playerStats = file_Player.read()
        start = playerStats.find('<birthday>')
        end = playerStats.find('</weight>') + len('</weight>')
        generalStats = playerStats[start:end]
        generalStats = "".join(generalStats.lower().split())
        generalStats = '<general_stats>' + generalStats + '</general_stats>'
        parsedXMLGeneralStats = ET.fromstring(generalStats)
        birthday = parsedXMLGeneralStats.find('birthday').text
        birthday = parse(birthday)
        height = float(parsedXMLGeneralStats.find('height').text)
        weight = float(parsedXMLGeneralStats.find('weight').text)
        
        try:
            cur.execute('''INSERT OR IGNORE INTO Player (player_api_id,player_fifa_api_id,player_name,birthday,height,weight) 
                VALUES ( ?, ?, ?, ?, ?, ? )''', ( player_api_id, player_fifa_api_id,player_name,birthday,height,weight) )
            print 'Inserted Player #' + str(count) +  ' - ' +filename
            conn.commit()
            
            cur.execute('SELECT id FROM Player WHERE player_api_id = ? ', (player_api_id, ))
            player_id = cur.fetchone()[0]
        except:
            printError(player_name,player_api_id,player_fifa_api_id)
            return count
        
        allStatsNodes = re.findall('<Timestamp>([0-9]+)</Timestamp>',playerStats)
        for node in allStatsNodes:
            try:
                deltaDays = int(node) - startIntFifa
                datePlayerStatUpdate = startDateFifa + timedelta(days=deltaDays)
                
                start = playerStats.find('<Timestamp>' + node + '</Timestamp>') + len ('<Timestamp>' + node + '</Timestamp>')
                detailedStats = playerStats[start:]
                end = detailedStats.find('</value>')
                detailedStats = detailedStats[:end]
                detailedStats = "_".join(detailedStats.lower().split())
                detailedStats = '<detailed_stats>' + detailedStats + '</detailed_stats>'
                parsedXMLDetailedStats = ET.fromstring(detailedStats)
            except:
                printError(player_name,player_api_id,player_fifa_api_id)
                return count
            
            cur.execute('''INSERT OR IGNORE INTO Player_Stats (player_api_id,player_fifa_api_id,date_stat) 
            VALUES ( ?, ?, ? )''', ( player_api_id, player_fifa_api_id, datePlayerStatUpdate) )
            cur.execute('SELECT id FROM Player_Stats WHERE player_api_id = ? AND date_stat = ?', (player_api_id, datePlayerStatUpdate, ))
            player_stats_id = cur.fetchone()[0]
        
            xmlLength = len(parsedXMLDetailedStats)
            if xmlLength == 31:
                detailedStatsField = shortStatsField
            elif xmlLength == 38:
                detailedStatsField = longStatsField
            else:
                printError(player_name,player_api_id,player_fifa_api_id)
                return count
        
            field_count = 0
            for field in generalStatsField + detailedStatsField:
                field = "_".join(field.lower().split())
                try:
                    stat = int(parsedXMLDetailedStats.find(field).text)
                except:
                    printError(player_name,player_api_id,player_fifa_api_id)
                    return count
                try:
                    cur.execute('Update Player_Stats SET ' + field + '=? WHERE id=?', (stat,player_stats_id))
                except:
                    cur.execute('Update Player_Stats SET ' + field + '=? WHERE id=?', (None,player_stats_id))
                field_count += 1
                
            for field in featureField:
                field = "_".join(field.lower().split())
                try:
                    stat = str(parsedXMLDetailedStats.find(field).text)
                except:
                    printError(player_name,player_api_id,player_fifa_api_id)
                    return count
                try:
                    cur.execute('Update Player_Stats SET ' + field + '=? WHERE id=?', (stat,player_stats_id))
                except:
                    cur.execute('Update Player_Stats SET ' + field + '=? WHERE id=?', (None,player_stats_id))
                field_count += 1
            conn.commit()
    return count


print "Player lookup started..."
count = 0
for (dirname, dirs, files) in os.walk(playersFileDirectory):
    for filename in files:
        if filename.endswith('.xml'):
            count = savePlayer(filename,count)