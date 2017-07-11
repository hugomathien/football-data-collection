'''
Created on Jun 27, 2016

@author: hugomathien
'''
import os
import xml.etree.ElementTree as ET
import re
import sys
import re
from datetime import datetime
from datetime import timedelta
from time import strptime
import time
import xml.etree.ElementTree as ET
import collections
import math
from operator import truediv

#Player stat files
players_directory = 'D:\\OneDrive\\Projects\\BettingSerivce\\FootballDataCollection\\footballData\\DATA\\players\\'
#Match with embedded stats 
match_directory = 'D:\\OneDrive\\Projects\\BettingSerivce\\FootballDataCollection\\footballData\\DATA\\matches_with_stats'
#Where to write the learning file
output_directory = 'D:\\OneDrive\\Projects\\BettingSerivce\\FootballDataCollection\\footballData\\DATAlearning_vector\\'
#Name of the learning file
ts = time.time()
runTime = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
output_filename = str(runTime) + '_learningVector_3class.txt'
totalFile = 0
classificationCount = [0] * 3
# Historical real match data per team
teamMatchHistory = dict()
countryList = list() # Countries
write_country_to_vector = False
runRealMatchStatsForXFiles = False
teamStatsOperand = 'substract'
#positionXYClusers = [ [[1],[1]],[[2,3],[2,3]],[[2,3],[4,5,6]]... ]
# All positions clusters
#positionClusters = [positionXClusters,positionYClusters]
#positionClustersStatsList = [positionXClusters,positionYClusters]
#Momentum features
teamMomentumFeatures = [[20,'Home Goal Diff'],
                [20,'Away Goal Diff'],
                [20,'Home Win'],
                [20,'Home Draw'],
                [20,'Home Lost'],
                [20,'Away Win'],
                [20,'Away Draw'],
                [20,'Away Lost'],
                [10,'Home Goal Diff'],
                [10,'Away Goal Diff'],
                [10,'Home Win'],
                [10,'Home Draw'],
                [10,'Home Lost'],
                [10,'Away Win'],
                [10,'Away Draw'],
                [10,'Away Lost'],
                [5,'Home Goal Diff'],
                [5,'Away Goal Diff'],
                [5,'Home Win'],
                [5,'Home Draw'],
                [5,'Home Lost'],
                [5,'Away Win'],
                [5,'Away Draw'],
                [5,'Away Lost']]

# Core statistics of FIFA FOOTBALL video games
statsList = ['Crossing',
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
             'Sliding Tackle']

# General stats
generalStatList = ['Overall rating',
             'Potential']
# Attacking stats
attackingStatList = ['Crossing',
             'Finishing',
             'Heading Accuracy',
             'Short Passing',
             'Volleys']
# Goalkeeper stats
gkStatList = ['GK Diving',
             'GK Handling',
             'GK Kicking',
             'GK Positioning',
             'GK Reflexes']
# Skills stats
skillStatList = ['Dribbling',
             'Curve',
             'Free Kick Accuracy',
             'Long Passing',
             'Ball Control']
# Movement stats
movementStatList = ['Acceleration',
             'Sprint Speed',
             'Agility',
             'Reactions',
             'Balance']
# Power stats
powerStatList = ['Shot Power',
             'Jumping',
             'Stamina',
             'Strength',
             'Long Shots']
# Mentality stats
mentalityStatList = ['Aggression',
             'Interceptions',
             'Positioning',
             'Vision',
             'Penalties']
# Defensive stats
defensiveStatList = ['Marking',
             'Standing Tackle',
             'Sliding Tackle']

attackCustomStatList = ['Finishing',
             'Heading Accuracy',
             'Volleys',
             'Shot Power',
             'Jumping',
             'Strength',
             'Long Shots',
             'Dribbling',
             'Curve',
             'Free Kick Accuracy'
             ]

teamPlayCustomStatList = ['Short Passing',
                    'Long Passing',
                    'Ball Control',
                    'Stamina',
                    'Crossing',
                    'Positioning',
                    'Vision']

defenseCustomStatList = ['Marking',
             'Standing Tackle',
             'Sliding Tackle',
             'Jumping',
             'Strength',
             'Aggression',
             'Interceptions',
             'Positioning',
             'Vision']

totStats = len(statsList) # total number of fifa statistics

# Stats to work with
goalKeeperStats = [gkStatList,generalStatList]
fieldplayerStats = list()
for statField in statsList:
    fieldplayerStats.append([statField])

fieldplayerStats = [defenseCustomStatList,teamPlayCustomStatList,attackCustomStatList]

# Cluster of horizontal pitch position
positionYClusters = [[1],[2,3,4,5,6,7,8,9,10,11,12]]
# Cluster of vertical pitch position
positionXClusters = [[1],[2,3,4,5,6,7,8,9,10,11,12]]

positionClusters = list()
positionClusters.append([[1],[1]])
positionClustersStatsList = list()
positionClustersStatsList.append(goalKeeperStats)

for x in positionXClusters[1:]:
    for y in positionYClusters[1:]:
        xyCluster = list()
        xyCluster = [x,y]
        positionClusters.append(xyCluster)
        positionClustersStatsList.append(fieldplayerStats)

#statCategoryList = [gkStatList,generalStatList] + [[x] for x in statsList[:-5]]
# -----------------------------------------------------
# Add a feature to the feature vector
# -----------------------------------------------------
def writeFeature(featureVector,featureIndex,featureValue,carriage):
    if carriage:
        featureVector = featureVector + ' ' + str(featureIndex) + ':' + str(featureValue) + '\n'   
    else:
        featureVector = featureVector + ' ' + str(featureIndex) + ':' + str(featureValue)
        
    return featureVector
# -----------------------------------------------------
# Classify the outcome
# -----------------------------------------------------
def getClassification(scoreDiff):
    classification = 0
    if scoreDiff > 0:
        classification = 1  
    elif scoreDiff < 0:
        classification = 0
    else:
        classification = 0
    
    return classification
    '''
    if scoreDiff > 3:
        classification = 8  
    elif scoreDiff == 3:
        classification = 7
    elif scoreDiff == 2:
        classification = 6
    elif scoreDiff == 1:
        classification = 5
    elif scoreDiff == 0:
        classification = 4
    elif scoreDiff == -1:
        classification = 3
    elif scoreDiff == -2:
        classification = 2
    elif scoreDiff == -3:
        classification = 1
    else:
        classification = 0
    '''  
        
    
# -----------------------------------------------------
# Compute the momentum feature vector
# -----------------------------------------------------
def computeMomentumFeatureVector(homeTeamMatchHistory,awayTeamMatchHistory):
    
    teamMatchHistory = [homeTeamMatchHistory,awayTeamMatchHistory]
    featureVector = list()
    for momentumFeature in teamMomentumFeatures:
        size = momentumFeature[0]
        feature = momentumFeature[1]
        featureSum = 0
        for matchHistory in teamMatchHistory:
            for matchId,matchStat in matchHistory.items()[-size:]:
                featureValue = matchStat[feature]
                featureSum += featureValue
            featureAverage = float(featureSum) / float(size)
            featureVector.append(featureAverage)
    return featureVector
# -----------------------------------------------------
# Compute real match statistics per team
# -----------------------------------------------------
def computeRealMatchStatistics():
    countFileLoop = 0
    for (dirname, dirs, files) in os.walk(match_directory):
        for filename in files:
            if filename.endswith('.xml'):
                thefile = os.path.join(dirname,filename)
                fh = open(thefile)
                xmlstr = fh.read()
                try:  
                    start = xmlstr.find('<item>') 
                    end = xmlstr.find('</item>') + len('</item>') 
                    matchXml = xmlstr[start:end]
                    parsedMatchXml = ET.fromstring(matchXml)
                    countryLst = parsedMatchXml.findall('country')
                    country = countryLst[0].text
                    if not country in countryList:
                        countryList.append(country)
                    
                    homeTeamIdLst = parsedMatchXml.findall('homeTeamId')
                    awayTeamIdLst = parsedMatchXml.findall('awayTeamId') 
                    homeGoalLst = parsedMatchXml.findall('homeTeamGoal')
                    awayGoalLst = parsedMatchXml.findall('awayTeamGoal') 
                    matchIdLst = parsedMatchXml.findall('matchId')
                    
                    homeTeamGoal = int(homeGoalLst[0].text)
                    awayTeamGoal = int(awayGoalLst[0].text)
                    homeTeamId = homeTeamIdLst[0].text
                    awayTeamId = awayTeamIdLst[0].text
                    matchId = int(matchIdLst[0].text)
                    
                    scoreDiff = homeTeamGoal - awayTeamGoal
                    homeTeamStat = dict()
                    homeTeamStat['Home/Away'] = 1 # 1 for Home, 0 for Away
                    homeTeamStat['Home Goal Scored'] = homeTeamGoal
                    homeTeamStat['Home Goal Against'] = awayTeamGoal
                    homeTeamStat['Away Goal Scored'] = 0
                    homeTeamStat['Away Goal Against'] = 0
                    homeTeamStat['Home Goal Diff'] = scoreDiff
                    homeTeamStat['Away Goal Diff'] = 0
                    homeTeamStat['Home Win'] = 1 if (homeTeamGoal - awayTeamGoal) > 0 else 0
                    homeTeamStat['Home Draw'] = 1 if (homeTeamGoal - awayTeamGoal) == 0 else 0
                    homeTeamStat['Home Lost'] = 1 if (homeTeamGoal - awayTeamGoal) < 0 else 0
                    homeTeamStat['Away Win'] = 0
                    homeTeamStat['Away Draw'] = 0
                    homeTeamStat['Away Lost'] = 0
                    homeTeamStat['Class'] = getClassification(scoreDiff)
                    homeTeamStat['Opponent'] = awayTeamId
                    
                    awayTeamStat = dict()
                    awayTeamStat['Home/Away'] = 0 # 1 for Home, 0 for Away
                    awayTeamStat['Home Goal Scored'] = 0
                    awayTeamStat['Home Goal Against'] = 0
                    awayTeamStat['Away Goal Scored'] = awayTeamGoal
                    awayTeamStat['Away Goal Against'] = homeTeamGoal
                    awayTeamStat['Home Goal Diff'] = 0
                    awayTeamStat['Away Goal Diff'] = -scoreDiff
                    awayTeamStat['Home Win'] = 0
                    awayTeamStat['Home Draw'] = 0
                    awayTeamStat['Home Lost'] = 0
                    awayTeamStat['Away Win'] = 1 if (homeTeamGoal - awayTeamGoal) < 0 else 0
                    awayTeamStat['Away Draw'] = 1 if (homeTeamGoal - awayTeamGoal) == 0 else 0
                    awayTeamStat['Away Lost'] = 1 if (homeTeamGoal - awayTeamGoal) > 0 else 0
                    awayTeamStat['Class'] = getClassification(-scoreDiff)
                    awayTeamStat['Opponent'] = homeTeamId
                    
                    matchHistoryHome = teamMatchHistory.get(homeTeamId,collections.OrderedDict())
                    matchHistoryHome[matchId] = homeTeamStat
                    teamMatchHistory[homeTeamId] = matchHistoryHome
                    matchHistoryAway = teamMatchHistory.get(awayTeamId,collections.OrderedDict())
                    matchHistoryAway[matchId] = awayTeamStat
                    teamMatchHistory[awayTeamId] = matchHistoryAway
                    
                    countFileLoop += 1
                    print ('Computed real match statistics match #' + str(countFileLoop ) )
                    if countFileLoop == runRealMatchStatsForXFiles:
                        return
                except:
                    'File Error - Cannot compute real match statistics'
# -----------------------------------------------------
# Create a learning vector per match
# -----------------------------------------------------
def createLearningVectors():
    countFileLoop = 0
    totalFile = 0
    #Learning file output
    output = open(output_directory + output_filename,'a')
    for (dirname, dirs, files) in os.walk(match_directory):
        for filename in files:
            if filename.endswith('.xml'):
                thefile = os.path.join(dirname,filename)
                fh = open(thefile)
                xmlstr = fh.read()
                try:  
                    start = xmlstr.find('<item>') 
                    end = xmlstr.find('</item>') + len('</item>') 
                    matchXml = xmlstr[start:end]
                    parsedMatchXml = ET.fromstring(matchXml)
                    
                    #Country
                    countryLst = parsedMatchXml.findall('country')
                    country = countryLst[0].text
                    countryIdx = countryList.index(country) + 1
                    
                    #Players positions on the pitch
                    homePlayersX = parsedMatchXml.findall('homePlayersX/value') 
                    awayPlayersX = parsedMatchXml.findall('awayPlayersX/value') 
                    homePlayersY = parsedMatchXml.findall('homePlayersY/value') 
                    awayPlayersY = parsedMatchXml.findall('awayPlayersY/value')
                    playersXPosition = homePlayersX + awayPlayersX
                    playersYPosition = homePlayersY + awayPlayersY
           
                    #Team stats
                    homeGoalLst = parsedMatchXml.findall('homeTeamGoal')
                    awayGoalLst = parsedMatchXml.findall('awayTeamGoal') 
                    homeTeamIdLst = parsedMatchXml.findall('homeTeamId')
                    awayTeamIdLst = parsedMatchXml.findall('awayTeamId') 
                    homeTeamId = homeTeamIdLst[0].text
                    awayTeamId = awayTeamIdLst[0].text
                    matchIdLst = parsedMatchXml.findall('matchId')
                    matchId = int(matchIdLst[0].text)
                    
                    #Compute class
                    homeTeamGoal = homeGoalLst[0].text
                    awayTeamGoal = awayGoalLst[0].text
                    scoreDiff = int(homeTeamGoal) - int(awayTeamGoal)
                    classification = getClassification(scoreDiff)
                    classificationCount[classification] = classificationCount[classification] + 1
                    #Compute team momentum
                    homeTeamMatchHistory = teamMatchHistory[homeTeamId]
                    awayTeamMatchHistory = teamMatchHistory[awayTeamId]
                    homeTeamMatchHistorySubset = dict((k,v) for k, v in homeTeamMatchHistory.items() if k < matchId)
                    awayTeamMatchHistorySubset = dict((k,v) for k, v in awayTeamMatchHistory.items() if k < matchId)
                    
                    momentumFeatureVector = computeMomentumFeatureVector(homeTeamMatchHistorySubset,awayTeamMatchHistorySubset)
                    #line =  homeTeamGoal + ',' + awayTeamGoal + ','
                    #line = str(scoreDiff)
                    #line =  str(matchId)
                    
                    featureVector = str(classification)
                    if(write_country_to_vector):
                        featureVector = writeFeature(featureVector,1,countryIdx,False)
                        featureIndex = 2
                    else:
                        featureIndex = 1
                        
                    for featureValue in momentumFeatureVector:
                        featureVector = writeFeature(featureVector,featureIndex,featureValue,False)
                        featureIndex += 1
                    # -----------------------------------------------------
                    # Write players' statistics to vector
                    # -----------------------------------------------------   
                    start = xmlstr.find('<fifaStats>') + len('fifaStats') + 2
                    end = xmlstr.find('</fifaStats>') 
                    fifaStats = xmlstr[start:end]
                    
                    # ------------------------------------------------------------------------
                    # CLUSTERING: aggregate statistics per player's position on the pitch
                    # ------------------------------------------------------------------------
                    homeClusterStats = list()
                    awayClusterStats = list()
                    i_cluster = 0
                    for positionClusterXY in positionClusters:
                        stats = list()
                        positionStatList = positionClustersStatsList[i_cluster]
                        for stat in positionStatList:
                            stats.append(0)
                        i_cluster += 1
                        homeClusterStats.append(stats)
                        awayClusterStats.append(list(stats))
                 
                    # ------------------------------------------------------------------------
                    # STATISTICS: compute players statistics and allocate to clusters
                    # ------------------------------------------------------------------------
                    for i in range(1,23):
                        start = fifaStats.find('<player'+str(i)+'>')+ len('<player'+str(i)+'>')
                        end = fifaStats.find('</player'+str(i)+'>') 
                        playerStats = fifaStats[start:end]
                        yPosition = int(playersYPosition[i-1].text)
                        xPosition = int(playersXPosition[i-1].text)
                 
                        # FIND THE PLAYER CLUSTER
                        i_cluster = 0
                        for positionClusterXY in positionClusters:
                            xCluster = positionClusterXY[0]
                            yCluster = positionClusterXY[1]
                            if xPosition in xCluster and yPosition in yCluster:
                                positionStatList = positionClustersStatsList[i_cluster]
                                #found the player's cluster on the pitch
                                if i <= 11:
                                    clusterStat = homeClusterStats[i_cluster]
                                    break
                                else:
                                    clusterStat = awayClusterStats[i_cluster]
                                    break
                                
                            i_cluster += 1
             
                        sumStat = 0
                        countStat = 0
                        statLabelCounter = 0
                        # COMPUTE THE PLAYER STATISTICS FOR HIS CLUSTER
                        # Example: [attacking,defending...]
                        for positionStatLabels in positionStatList:
                            # Example: attacking = [shooting,cross,passing...]
                            for statLabel in positionStatLabels:
                                start = playerStats.find('<'+statLabel+'>') + len('<'+statLabel+'>')
                                end = playerStats.find('</'+statLabel+'>') 
                                statValueStr = playerStats[start:end]
                                try:
                                    statValue = int(statValueStr)
                                except:
                                    statValue = 50 # average for missing stats
    
                                sumStat += statValue
                                countStat += 1
                            avgStat = sumStat / countStat
                            clusterStat[statLabelCounter] = clusterStat[statLabelCounter] + avgStat
                            statLabelCounter +=1
                    
                    # COMPARE THE HOME AND AWAY TEAM STATISTICS AND WRITE AS A FEATURE VECTOR
                    clusterStatLoopCount=1
                    size = sum(len(x) for x in homeClusterStats)
                    for i, homeCluster in enumerate(homeClusterStats):
                        awayCluster = awayClusterStats[i]
                        for j, homeStat in enumerate(homeCluster):
                            awayStat = awayCluster[j]
                            if awayStat != 0 and teamStatsOperand == 'divide':
                                stat = float(homeStat) / float(awayStat)
                            elif teamStatsOperand == 'substract':
                                stat = homeStat - awayStat
                            elif teamStatsOperand == 'exppct':
                                stat = math.exp((float(homeStat) - float(awayStat))/100)
                            else:
                                stat = float(0)
                                
                            if clusterStatLoopCount == size:
                                featureVector = writeFeature(featureVector,featureIndex,stat,True) 
                            else:
                                featureVector = writeFeature(featureVector,featureIndex,stat,False) 
                            
                            clusterStatLoopCount += 1
                            featureIndex += 1
                        
                    output.write(featureVector)
                    print ('Computed feature vector #' + str(countFileLoop))
                    countFileLoop += 1
                except:
                    e = sys.exc_info()[0]
                    print ('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
                    print ('Error with file: ' + thefile + str(e))
                totalFile = totalFile + 1
                
    output.close()
    print ('Processed:', str(countFileLoop))
    print ('Files:', str(totalFile))
    print ('Classification count = ' + str(classificationCount))
    
if __name__ == "__main__":
    computeRealMatchStatistics()
    createLearningVectors()
