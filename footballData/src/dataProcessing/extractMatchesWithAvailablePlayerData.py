'''
Created on Jun 15, 2016

@author: hugomathien
'''
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

# EXTRACT MATCHES WITH EMBEDDED STATISTICS

# ---- PARAMETERS ----
# --------------------
#List of players to work with



playersListDirectory = 'D:\\OneDrive\\Projects\\BettingSerivce\\FootballDataCollection\\footballData\\DATA\\players_list\\'
playersListDirectory = os.getcwdu() + '..\\..\\DATA\\players_list\\'
#Matches to work with
matchDirectory = 'D:\\OneDrive\\Projects\\BettingSerivce\\FootballDataCollection\\footballData\\footballData\\matches\\'
#Player files to work with
playersFileDirectory = 'D:\\OneDrive\\Projects\\BettingSerivce\\FootballDataCollection\\footballData\\DATA\\players\\'
#Where to output the match files with embedded statistics
output = 'D:\\OneDrive\\Projects\\BettingSerivce\\FootballDataCollection\\footballData\\DATA\\'
#Where to output the missing players list
missingPlayerFileName = 'missingPlayers.txt'
#How many missing players to output, ordered by their importance (i.e: the number of match they prevent to retrieve)
missingPlayerExtractSize = 1000
writeMatchFiles = True #Write the match files or just run an analysis ?
validMatch = set() #Matches that we can parse and for which we have the full lineup stats
existingPlayersFileDict = collections.OrderedDict()
missingPlayersDict = dict()
missingPlayerIdDict = dict()

print "Player lookup started..."
for (dirname, dirs, files) in os.walk(playersFileDirectory):
    for filename in files:
        if filename.endswith('.xml'):
            underscore = [m.start() for m in re.finditer('_', filename)]
            playerMatchId = int(filename[underscore[0]+1:underscore[1]])
            existingPlayersFileDict[playerMatchId] = filename

print "Match lookup started..."
for (dirname, dirs, files) in os.walk(matchDirectory):
    for filename in files:
        if filename.endswith('.xml'):
            thefile = os.path.join(dirname,filename)
            fh = open(thefile)
            xmlstr = fh.read()
            try:
                parsedXML = ET.fromstring(xmlstr)
                matchId = parsedXML.findall('matchId')[0].text
                lstHomeId = parsedXML.findall('homePlayersId/value') 
                lstAwayId = parsedXML.findall('awayPlayersId/value') 
                lstHome = parsedXML.findall('homePlayers/value') 
                lstAway = parsedXML.findall('awayPlayers/value') 
                homeTeamFullName = parsedXML.findall('homeTeamFullName')[0].text
                awayTeamFullName = parsedXML.findall('awayTeamFullName')[0].text
                matchDateLst = parsedXML.findall('date')
                matchDateStr = matchDateLst[0].text
                matchYear = matchDateStr[:4]
                matchMonth = matchDateStr[5:7]
                matchDay = matchDateStr[8:10]
                matchDate = datetime(int(matchYear),int(matchMonth),int(matchDay))
                
                fifaStats = ''
                playerHomeFiles = list()
                playerAwayFiles = list()
               
                #Squad parsing
                for i in range(0,11):
                    playerHomeId = int(lstHomeId[i].text)
                    playerAwayId = int(lstAwayId[i].text)
                    playerHome = lstHome[i].text
                    playerAway = lstAway[i].text
            
                    if playerHomeId in existingPlayersFileDict: #Existing Player
                        playerHomeFileName = existingPlayersFileDict[playerHomeId]
                        playerHomeFiles.append(playerHomeFileName)
                    else:
                        occurence = missingPlayersDict.get(playerHome,0)
                        missingPlayersDict[playerHome] = occurence + 1
                        missingPlayerIdDict[playerHome] = playerHomeId
                        
                    if playerAwayId in existingPlayersFileDict: #Existing Player
                        playerAwayFileName = existingPlayersFileDict[playerAwayId]
                        playerAwayFiles.append(playerAwayFileName)
                    else:
                        occurence = missingPlayersDict.get(playerAway,0)
                        missingPlayersDict[playerAway] = occurence + 1
                        missingPlayerIdDict[playerAway] = playerAwayId
                
                #Lookup players files and parse statistics
                playerFiles = playerHomeFiles + playerAwayFiles
                if len(playerFiles) == 22:
                    validMatch.add(filename)
                    playerCount = 1
                    for playerFile in playerFiles:
                       
                        filePath = playersFileDirectory + playerFile
                        playerStats = ''
                        with open(filePath,'r') as fPlayer:
                            playerStats = fPlayer.read()
                            allNodes = re.findall('<Timestamp>([0-9]+)</Timestamp>',playerStats)
                            
                            i=0
                            for node in allNodes:
                                selectedNode = node

                                i += 1
                                startIntFifa = 154994
                                startDateFifa = datetime(2007,2,22)
                                delta = int(node) - startIntFifa
                                datePlayerStatUpdate = startDateFifa + timedelta(days=delta)
                                if matchDate > datePlayerStatUpdate:
                                    break
                            
                            start = playerStats.find('<birthday>')
                            end = playerStats.find('</weight>') + len('</weight>')
                            generalStats = playerStats[start:end]
                            
                            start = playerStats.find('<Timestamp>' + selectedNode + '</Timestamp>') + len ('<Timestamp>' + selectedNode + '</Timestamp>')
                            detailedStats = playerStats[start:]
                            end = detailedStats.find('</value>')
                            detailedStats = detailedStats[:end]
                            fifaStats = fifaStats + '<player' + str(playerCount) + '>' + generalStats + detailedStats + '</player' + str(playerCount) + '>' 
                            playerCount += 1
                    
                    
                    #Output the match file with statistics
                    if writeMatchFiles is True:
                        subDir = dirname.split(matchDirectory,1)[1] 
                        outputFileName = output + subDir + '/' + filename
                        if not os.path.exists(os.path.dirname(outputFileName)):
                            try:
                                os.makedirs(os.path.dirname(outputFileName))
                            except OSError as exc: # Guard against race condition
                                print 'Cannot output match file ' + outputFileName
                        outputFile = open(outputFileName,'w')
                        outputFile.write(xmlstr)
                        outputFile.write('<fifaStats>' + fifaStats + '</fifaStats>')
                        outputFile.close()
                    
            except:
                e = sys.exc_info()[0]
                print 'Error on line {}'.format(sys.exc_info()[-1].tb_lineno)
                print 'Error with file: ' + thefile
                
            print 'Found ' + str(len(validMatch)) + ' valid match files'


#Extract missing players
sorted_x = sorted(missingPlayersDict.items(), key=operator.itemgetter(1))
outputFile = open(playersListDirectory + missingPlayerFileName,'w')
for x in sorted_x[-missingPlayerExtractSize:]:
    occurence = missingPlayersDict[x[0]]
    playerId = missingPlayerIdDict[x[0]]

    outputFile.write(str(playerId) + ',' + str(x[0]) + ',' + str(occurence) + '\n')
    print str(playerId) + ',' + str(x[0]) + ',' + str(occurence)

print 'Extracted ' + str(missingPlayerExtractSize) + ' missing players'
outputFile.close()