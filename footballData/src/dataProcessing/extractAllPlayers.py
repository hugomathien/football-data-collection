'''
Created on Jun 15, 2016

@author: hugomathien
'''
import os
import xml.etree.ElementTree as ET
import collections 

playersListDirectory = '/Users/hugomathien/Documents/workspace/footballdata/players_list/'
matchDirectory = '/Users/hugomathien/Documents/workspace/footballdata/matches/'
count = 0
playersDict = collections.OrderedDict()
print "Player extract started..."

for (dirname, dirs, files) in os.walk(matchDirectory):
    for filename in files:
        if filename.endswith('.xml'):
            thefile = os.path.join(dirname,filename)
            fh = open(thefile)
            xmlstr = fh.read()
            try:
                parsedXML = ET.fromstring(xmlstr)
                lstHomeId = parsedXML.findall('homePlayersId/value') 
                lstAwayId = parsedXML.findall('awayPlayersId/value') 
                lstHome = parsedXML.findall('homePlayers/value') 
                lstAway = parsedXML.findall('awayPlayers/value') 
                homeTeamFullName = parsedXML.findall('homeTeamFullName')[0].text
                awayTeamFullName = parsedXML.findall('awayTeamFullName')[0].text
                 
                for i in range(0,11):
                    playerHomeId = lstHomeId[i].text
                    playerAwayId = lstAwayId[i].text
                    playerHome = lstHome[i].text
                    playerAway = lstAway[i].text
            
                    if playerHomeId in playersDict: #Existing Player
                        playerHomeDict = playersDict[playerHomeId]
                        clubs = playerHomeDict['clubs']
                        if homeTeamFullName not in clubs:
                            playerHomeDict['clubs'].append(homeTeamFullName)
                    else: #New Player
                        playerHomeDict = dict()
                        playerHomeDict['name'] = playerHome
                        clubs = list()
                        clubs.append(homeTeamFullName)
                        playerHomeDict['clubs'] = clubs
                        playersDict[playerHomeId] = playerHomeDict
                        
                    if playerAwayId in playersDict: #Existing Player
                        playerAwayDict = playersDict[playerAwayId]
                        clubs = playerAwayDict['clubs']
                        if awayTeamFullName not in clubs:
                            playerAwayDict['clubs'].append(awayTeamFullName)
                    else: #New Player
                        playerAwayDict = dict()
                        playerAwayDict['name'] = playerAway
                        clubs = list()
                        clubs.append(awayTeamFullName)
                        playerAwayDict['clubs'] = clubs
                        playersDict[playerAwayId] = playerAwayDict
                    
            except:
                print 'Error with file: ' + thefile
                
            count = count + 1 

with open(playersListDirectory + "1_players_list_all.txt","w+") as f:
    for player in playersDict:
        name = playersDict[player]['name']
        clubs = playersDict[player]['clubs']
        string = player + ',' + name
        for club in clubs:
            string = string + ',' + club
        string = string + '\n'
        f.write(string)

print 'Files:', count
print 'Players:', len(playersDict)