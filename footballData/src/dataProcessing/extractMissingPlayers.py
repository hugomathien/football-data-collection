'''
Created on Jul 2, 2016

@author: hugomathien
'''
import os
import re 

playersFileDirectory = os.getcwdu() + '..\\..\\DATA\\players_list\\'
allPlayersFile = os.getcwdu() + '..\\..\\DATA\\players_list\\1_players_list_all.txt'
output = os.getcwdu() + '..\\..\\DATA\\players_list\\1_players_list_all.txt'
count = 0
allPayersFile = set()
allPlayers = set()
playersDict = dict()

print "Player extract started..."
for (dirname, dirs, files) in os.walk(playersFileDirectory):
    for filename in files:
        if filename.endswith('.xml'):
            underscore = [m.start() for m in re.finditer('_', filename)]
            matchId = int(filename[underscore[0]+1:underscore[1]])
            allPayersFile.add(matchId)
            count += 1
            
print "Player file count: " + str(count)

count = 0

with open(allPlayersFile,"r") as f:
    for line in f:
        line = line.rstrip()
        comma = line.find(',') + 1
        matchId = int(line[:comma-1])
        line = line[comma:]
        comma = line.find(',')
        line = line[:comma]
        playerName = line
        allPlayers.add(matchId)
        playersDict[matchId] = playerName
        count += 1

print "Players in list count: " + str(count)

with open(output,"w") as f:
    for key in playersDict.keys():
        if key in allPayersFile:
            pass
        else:
            f.write(str(key) + ',' + playersDict[key] + '\n')
        
#with open("_PlayersMissing5.txt","w") as f:
