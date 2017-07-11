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
matchFileDirectory = 'D:\\OneDrive\\Projects\\BettingSerivce\\FootballDataCollection\\footballData\\DATA'
db = 'D:\\OneDrive\\Projects\\BettingSerivce\\FootballDataCollection\\footballData\\DATA\\database.sqlite'
errorFile = 'D:\\OneDrive\\Projects\\BettingSerivce\\FootballDataCollection\\footballData\\DATA\\match_error.txt'
startIntFifa = 154994
startDateFifa = datetime(2007,2,22)
conn = sqlite3.connect(db)
cur = conn.cursor()
count = 0

def printError(country,season,id,count):
    outputFile = open(errorFile,'a')
    outputFile.write(str(country) + ',' + str(season) + ',' + str(id) + '\n')  
    return count

def saveMatch(dirname,filename,count):
    thefile = os.path.join(dirname,filename)
    fh = open(thefile)
    xmlstr = fh.read()
    
    if xmlstr.find('</items>') > -1:
        xmlstr = xmlstr[:-8]
        print(xmlstr)
    try:
        parsedXML = ET.fromstring(xmlstr)
    except:
        return printError('None','None',thefile,count)
    
    lstHomePlayerId = parsedXML.findall('homePlayersId/value') 
    lstAwayPlayerId = parsedXML.findall('awayPlayersId/value') 
    country = parsedXML.find('country').text
    season = parsedXML.find('season').text
    league = parsedXML.find('league').text
    stage = parsedXML.find('stage').text
    matchApiId = parsedXML.find('matchId').text
    homeTeamApiId = int(parsedXML.find('homeTeamId').text)
    awayTeamApiId = int(parsedXML.find('awayTeamId').text)
    homeTeamFullName = parsedXML.find('homeTeamFullName').text
    awayTeamFullName = parsedXML.find('awayTeamFullName').text
    homeTeamAcronym = parsedXML.find('homeTeamAcronym').text
    awayTeamAcronym = parsedXML.find('awayTeamAcronym').text
    homeTeamGoal = int(parsedXML.find('homeTeamGoal').text)
    awayTeamGoal = int(parsedXML.find('awayTeamGoal').text)
    matchDateStr = parsedXML.find('date').text
    matchYear = matchDateStr[:4]
    matchMonth = matchDateStr[5:7]
    matchDay = matchDateStr[8:10]
    matchDate = datetime(int(matchYear),int(matchMonth),int(matchDay))
    
    cur.execute('''INSERT OR IGNORE INTO Country (name) VALUES ( ? )''', ( country, ) )
    cur.execute('SELECT id FROM Country WHERE name = ? ', (country, ))
    country_id = cur.fetchone()[0]
    
    cur.execute('''INSERT OR IGNORE INTO League (country_id, name) 
                VALUES ( ?, ? )''', (country_id, league, ) )
    cur.execute('SELECT id FROM League WHERE name = ? ', (league, ))
    league_id = cur.fetchone()[0]
    
    cur.execute('''INSERT OR IGNORE INTO Team (team_api_id,team_long_name,team_short_name) 
                VALUES ( ?, ?, ?)''', (homeTeamApiId, homeTeamFullName,homeTeamAcronym,))
    cur.execute('SELECT id FROM Team WHERE team_api_id = ? ', (homeTeamApiId, ))
    home_team_id = cur.fetchone()[0]
    
    cur.execute('''INSERT OR IGNORE INTO Team (team_api_id,team_long_name,team_short_name) 
                VALUES ( ?, ?, ? )''', (awayTeamApiId, awayTeamFullName,awayTeamAcronym,))
    cur.execute('SELECT id FROM Team WHERE team_api_id = ? ', (awayTeamApiId, ))
    away_team_id = cur.fetchone()[0]
    
    cur.execute('''INSERT OR IGNORE INTO Match (country_id,league_id,season,stage,match_api_id,
    home_team_goal,away_team_goal,home_team_id,away_team_id,date) 
                VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ? )''', ( country_id, league_id,season,stage,matchApiId,
                                                  homeTeamGoal,awayTeamGoal,home_team_id,away_team_id,matchDate,) )
    cur.execute('SELECT id FROM Match WHERE match_api_id = ? ', (matchApiId, ))
    match_id = cur.fetchone()[0]
    conn.commit()
    
    try:
        lstHomePlayerX = parsedXML.findall('homePlayersX/value') 
        lstHomePlayerY = parsedXML.findall('homePlayersY/value') 
        lstAwayPlayerX = parsedXML.findall('homePlayersX/value') 
        lstAwayPlayerY = parsedXML.findall('homePlayersY/value') 
    except:
        pass
    
    try:
        lstHomePlayerX = parsedXML.findall('homePlayersX/value') 
        lstHomePlayerY = parsedXML.findall('homePlayersY/value') 
        lstAwayPlayerX = parsedXML.findall('homePlayersX/value') 
        lstAwayPlayerY = parsedXML.findall('homePlayersY/value') 
    except:
        pass
    
    try:
        goal = parsedXML.find('goal')
        goaltxt = ET.tostring(goal)
        cur.execute('Update Match SET goal=? WHERE match_api_id=?', (goaltxt,matchApiId))
    except:
        pass
    
    try:
        shoton = parsedXML.find('shoton')
        shotontxt = ET.tostring(shoton)
        cur.execute('Update Match SET shoton=? WHERE match_api_id=?', (shotontxt,matchApiId))
    except:
        pass
    
    try:
        shotoff = parsedXML.find('shotoff')
        shotofftxt = ET.tostring(shotoff)
        cur.execute('Update Match SET shotoff=? WHERE match_api_id=?', (shotofftxt,matchApiId))
    except:
        pass
    
    try:
        foulcommit = parsedXML.find('foulcommit')
        foulcommittxt = ET.tostring(foulcommit)
        cur.execute('Update Match SET foulcommit=? WHERE match_api_id=?', (foulcommittxt,matchApiId))
    except:
        pass
    
    try:
        card = parsedXML.find('card')
        cardtxt = ET.tostring(card)
        cur.execute('Update Match SET card=? WHERE match_api_id=?', (cardtxt,matchApiId))
    except:
        pass
    
    try:
        cross = parsedXML.find('cross')
        crosstxt = ET.tostring(cross)
        cur.execute('Update Match SET cross=? WHERE match_api_id=?', (crosstxt,matchApiId))
    except:
        pass
    
    try:
        corner = parsedXML.find('corner')
        cornertxt = ET.tostring(corner)
        cur.execute('Update Match SET corner=? WHERE match_api_id=?', (cornertxt,matchApiId))
    except:
        pass
    
    try:
        possession = parsedXML.find('possession')
        possessiontxt = ET.tostring(possession)
        cur.execute('Update Match SET possession=? WHERE match_api_id=?', (possessiontxt,matchApiId))
    except:
        pass
    
    #Squad parsing
    for i in range(0,11):
        
            try:
                homePlayerApiId = int(lstHomePlayerId[i].text)
                awayPlayerApiId = int(lstAwayPlayerId[i].text)
            except:
                return printError(country,season,matchApiId,count)
            
            try:
                cur.execute('SELECT id FROM Player WHERE player_api_id = ? ', (homePlayerApiId, ))
                home_player_id = cur.fetchone()[0]
                cur.execute('Update Match SET home_player_' + str(i+1) + '=? WHERE match_api_id=?', (homePlayerApiId,matchApiId))
            except:
                pass
            
            try:
                cur.execute('SELECT id FROM Player WHERE player_api_id = ? ', (awayPlayerApiId, ))
                away_player_id = cur.fetchone()[0]
                cur.execute('Update Match SET away_player_' + str(i+1) + '=? WHERE match_api_id=?', (awayPlayerApiId,matchApiId))
            except:
                pass
        
            try:
                cur.execute('Update Match SET home_player_X' + str(i+1) + '=? WHERE match_api_id=?', (int(lstHomePlayerX[i].text),matchApiId))
                cur.execute('Update Match SET home_player_Y' + str(i+1) + '=? WHERE match_api_id=?', (int(lstHomePlayerY[i].text),matchApiId))
                cur.execute('Update Match SET away_player_X' + str(i+1) + '=? WHERE match_api_id=?', (int(lstAwayPlayerX[i].text),matchApiId))
                cur.execute('Update Match SET away_player_Y' + str(i+1) + '=? WHERE match_api_id=?', (int(lstAwayPlayerY[i].text),matchApiId))
            except:
                pass
            
    conn.commit()
    print ("Saved match #" + str(count))
    count += 1
    return count

print ("Match lookup started...")

for (dirname, dirs, files) in os.walk(matchFileDirectory):
    for filename in files:
        if filename.endswith('.xml'):
            count = saveMatch(dirname,filename,count)