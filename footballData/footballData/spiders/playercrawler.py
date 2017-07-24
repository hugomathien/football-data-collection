import scrapy
import urllib
import sys
import os
import requests
import collections
from datetime import datetime
from datetime import timedelta
from time import strptime
import time
import re
from footballData.items import Player
from googleapiclient.discovery import build
import pprint


class PlayerSpider(scrapy.Spider):
    name = "player"
    myGoogleApiKey = "AIzaSyCq89KQUzX5ShZiqBEmtOjnmCFPGIN8bi4"
    myGoogleCseId = "007327452172099429540:1bhg1zcqlyw"
    searchEngine = None
    # 'Google'
    # 'http://www.bing.com/search?q='
    # 'http://uk.search.yahoo.com/search?p='
    firstPlayerIndex = 1  # Where to start looping players on the list provided
    lastPlayerIndex = 8  # Where to end the loop
    searchEngineResultLimit = 3
    parseSoFifaLinkFromFile = False
    birthDayCheck = False
    birthMonthCheck = False
    birthYearCheck = False
    countryCheck = False
    parseLastNameOnly = False
    playerFilePath = os.getcwd() + '..\\..\\DATA\\players_list\\1_players_list_all.txt'
    playerErrorFile = os.getcwd() + '..\\..\\DATA\\players_list\\fail.txt'
    baseUrlSoFifa = 'http://sofifa.com/players?keyword='
    baseUrlLiveScore = 'http://football-data.mx-api.enetscores.com/page/xhr/player/'
    fifaLatestRelease = 16
    fifaEarliestRelease = 7
    fifaFirstStatsTimestamp = 154994  # 22 February 2007
    allowed_domains = ["http://sofifa.com",
                       "sofifa.com",
                       "http://www.sofifa.com",
                       "http://sofifa.com/",
                       "sofifa.com/",
                       "http://www.sofifa.com/",
                       "http://sofifa.com/player",
                       "sofifa.com/player",
                       "http://www.sofifa.com/player",
                       "football-data.mx-api.enetscores.com",
                       'json.mx-api.enetscores.com',
                       "football-data.mx-api.enetscores.com/page/xhr/player/",
                       "http://uk.search.yahoo.com/search",
                       "http://uk.search.yahoo.com/",
                       "https://www.googleapis.com/customsearch/"]
    start_urls = [
        "http://sofifa.com/",
    ]

    def googleSearch(self, search_term, api_key, cse_id, **kwargs):
        service = build("customsearch", "v1", developerKey=api_key)
        res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
        return res['items']

    # Calculate the age of the player with respect to the number on Sofifa website
    def calculateAge(self, end, born):
        start = 154994
        startDateFifa = datetime(2007, 2, 22)
        delta = end - start
        date = startDateFifa + timedelta(days=delta)
        return date.year - born.year - ((date.month, date.day) < (born.month, born.day))

    # Read players in the file
    def parse(self, response):
        playerFile = open(self.playerFilePath, 'U')
        with playerFile:
            playerIndex = self.firstPlayerIndex - 1
            lines = playerFile.readlines()
            while playerIndex <= (self.lastPlayerIndex - 1):
                if len(lines) > 0:
                    line = lines[playerIndex]
                else:
                    line = ""
                line = line.rstrip()
                comma = line.find(',')
                matchId = line[:comma]
                line = line[comma + 1:]
                comma = line.find(',')

                if self.parseSoFifaLinkFromFile:
                    comma = line.find(',')
                    playerName = line[:comma]
                    url = line[comma + 1:]
                    playerIndex += 1
                    fifaIdList = re.findall('sofifa.com/player/([0-9]+)', url)
                    fifaId = fifaIdList[0]
                    # url = 'http://sofifa.com/player/' + fifaId
                    yield scrapy.Request(url,
                                         callback=self.parsePlayerFromSoFifa,
                                         dont_filter=True,
                                         meta={'dont_redirect': True,
                                               'handle_httpstatus_list': [302],
                                               'fifaVersion': self.fifaLatestRelease, 'playerIndex': playerIndex,
                                               'playerUrl': url, 'playerName': playerName, 'matchId': matchId,
                                               'fifaId': fifaId, 'birthDay': 0, 'birthMonth': 0, 'birthYear': 0,
                                               'country': 'none'})
                else:
                    if comma > -1:
                        line = line[:comma]
                    playerName = line
                    url = self.baseUrlLiveScore + matchId
                    playerIndex += 1
                    yield scrapy.Request(url,
                                         callback=self.parsePlayerBirthdayFromLivescore,
                                         meta={'playerName': playerName, 'matchId': matchId})

    # Parse the player's birthday from the same website where we got the match squad ('football livescore')
    def parsePlayerBirthdayFromLivescore(self, response):
        print ("Enter player birthday")
        playerName = response.meta['playerName']
        matchId = response.meta['matchId']
        try:
            birthday = response.xpath('//span[@class="mx-break-small"]/text()').re_first("\((.+)\)")
            dataList = response.xpath('//span[@class="mx-break-micro"]/text()').extract()
            country = re.sub(r"\W", "", dataList[2])
            if birthday is not None:
                delimit1 = birthday.find('/') + 1
                delimit2 = birthday.find('-') + 1
                birthMonth = birthday[delimit1:delimit1 + 2]
                birthDay = birthday[:2]
                birthYear = birthday[delimit2:len(birthday)]
            else:
                birthMonth = 0
                birthDay = 0
                birthYear = 0

            if self.parseLastNameOnly:
                nameSpace = playerName.find(' ')
                if nameSpace > -1:
                    playerLastName = playerName.rsplit(None, 1)[-1]
                    playerNameEncoded = urllib.quote(playerLastName, safe='')
            else:
                playerNameEncoded = urllib.quote(playerName, safe='')

            # Search for the player via a search engine or directly via sofifa.com
            if self.searchEngine is not None:
                if self.searchEngine == 'Google':
                    results = self.googleSearch(playerName + ' site:sofifa.com/player', self.myGoogleApiKey,
                                                self.myGoogleCseId, num=1)
                    firstResult = results[0]
                    googleSearchUrl = firstResult['formattedUrl']
                    fifaIdList = re.findall('sofifa.com/player/([0-9]+)', googleSearchUrl)
                    fifaId = fifaIdList[0]
                    playerUrl = 'http://sofifa.com/player/' + str(fifaId)
                    yield scrapy.Request(playerUrl, callback=self.parsePlayerFromSoFifa, dont_filter=True,
                                         meta={'fifaVersion': self.fifaEarliestRelease, 'playerIndex': 0,
                                               'playerUrl': playerUrl, 'playerName': playerName, 'matchId': matchId,
                                               'fifaId': fifaId, 'birthDay': birthDay, 'birthMonth': birthMonth,
                                               'birthYear': birthYear, 'country': country})
                else:
                    playerUrl = self.searchEngine + playerNameEncoded + ' sofifa.com/player'
                    playerUrlWithFifaVersion = playerUrl
                    yield scrapy.Request(playerUrlWithFifaVersion,
                                         callback=self.parsePlayerFromSearchEngine,
                                         dont_filter=True,
                                         meta={'fifaVersion': self.fifaLatestRelease, 'playerUrl': playerUrl,
                                               'playerName': playerName, 'matchId': matchId, 'birthDay': birthDay,
                                               'birthMonth': birthMonth, 'birthYear': birthYear, 'country': country})
            else:
                playerUrl = self.baseUrlSoFifa + playerNameEncoded
                playerUrlWithFifaVersion = playerUrl + '&v=' + str(self.fifaLatestRelease)
                yield scrapy.Request(playerUrlWithFifaVersion, callback=self.parsePlayer,
                                     dont_filter=True,
                                     meta={'fifaVersion': self.fifaLatestRelease, 'playerUrl': playerUrl,
                                           'playerName': playerName, 'matchId': matchId, 'birthDay': birthDay,
                                           'birthMonth': birthMonth, 'birthYear': birthYear, 'country': country})
        except:
            print ('Failed retrieving: ' + playerName)
            filename = self.playerErrorFile
            file = open(filename, 'a')
            file.write(matchId + ',' + playerName + '\n')

    def parsePlayerFromSearchEngine(self, response):
        matchId = response.meta['matchId']
        fifaVersion = response.meta['fifaVersion']
        playerUrl = response.meta['playerUrl']
        playerName = response.meta['playerName']
        birthDay = response.meta['birthDay']
        birthMonth = response.meta['birthMonth']
        birthYear = response.meta['birthYear']
        country = response.meta['country']
        playerIndex = 0

        fifaIdList = response.xpath('//a/@href').re('sofifa.com/player/([0-9]+)')
        fullHrefLink = response.xpath('//a/@href').re('sofifa.com/player/(.+)')

        idx = 0
        for fifaId in fifaIdList[:self.searchEngineResultLimit]:
            url = 'http://sofifa.com/player/' + fullHrefLink[idx] + '?hl=en-US'
            yield scrapy.Request(url,
                                 callback=self.parsePlayerFromSoFifa,
                                 dont_filter=True,
                                 meta={'fifaVersion': fifaVersion, 'playerIndex': playerIndex,
                                       'playerUrl': playerUrl, 'playerName': playerName, 'matchId': matchId,
                                       'fifaId': fifaId, 'birthDay': birthDay, 'birthMonth': birthMonth,
                                       'birthYear': birthYear, 'country': country})
            idx += 1

    # Go to Sofifa website and search the player
    def parsePlayer(self, response):
        matchId = response.meta['matchId']
        fifaVersion = response.meta['fifaVersion']
        playerUrl = response.meta['playerUrl']
        playerName = response.meta['playerName']
        birthDay = response.meta['birthDay']
        birthMonth = response.meta['birthMonth']
        birthYear = response.meta['birthYear']
        country = response.meta['country']

        hrefList = response.xpath('//a[contains(@href,"/player/")]/@href').extract()
        playerList = response.xpath('//a[contains(@href,"/player/")]/@title').extract()

        # Get the next player in the list or start from zero if we are doing a new search
        try:
            playerIndex = response.meta["playerIndex"] + 1
        except:
            playerIndex = 0

        # If there is no relevant player in the search result, decrement the version of fifa used for the search
        if ((playerIndex + 1 > len(hrefList)) or (not playerList)) and fifaVersion > self.fifaEarliestRelease:
            fifaVersion -= 1
            if len(str(fifaVersion)) == 1:
                fifaVersionStr = '0' + str(fifaVersion)
            else:
                fifaVersionStr = str(fifaVersion)

            # Fire a new search for an older version of fifa
            playerUrlWithFifaVersion = playerUrl + '&v=' + fifaVersionStr + '&hl=en-US'
            yield scrapy.Request(playerUrlWithFifaVersion,
                                 callback=self.parsePlayer,
                                 dont_filter=True,
                                 meta={'fifaVersion': fifaVersion, 'playerUrl': playerUrl,
                                       'playerName': playerName, 'matchId': matchId, 'birthDay': birthDay,
                                       'birthMonth': birthMonth, 'birthYear': birthYear, 'country': country,
                                       'splash': {
                                           'args': {'wait': 2.5}
                                       }})
        # Browse relevant players
        elif (playerIndex + 1 <= len(hrefList)):
            try:
                href = hrefList[playerIndex]
                allFifaId = re.findall("player/([0-9]+)", href)
                fifaId = allFifaId[0]
                url = 'http://sofifa.com' + str(href)
                # Look at the player's page
                yield scrapy.Request(url,
                                     callback=self.parsePlayerFromSoFifa,
                                     dont_filter=True,
                                     meta={'fifaVersion': fifaVersion, 'playerIndex': playerIndex,
                                           'playerUrl': playerUrl, 'playerName': playerName, 'matchId': matchId,
                                           'fifaId': fifaId, 'birthDay': birthDay, 'birthMonth': birthMonth,
                                           'birthYear': birthYear, 'country': country,
                                           'splash': {
                                               'args': {'wait': 2.5}
                                           }})

            except:
                e = sys.exc_info()[0]
                print ('Error with player: ' + playerName + ' Error type: ' + str(e))
        # If we haven't found the player after browsing all versions of fifa, write out the player's in a file
        else:
            print ('No player found in Sofifa for: ' + playerName)
            filename = self.playerErrorFile
            file = open(filename, 'a')
            file.write(matchId + ',' + playerName + '\n')

    # Read the player page on sofifa and reach the page of the latest stats update
    def parsePlayerFromSoFifa(self, response):
        fifaVersion = response.meta["fifaVersion"]
        playerIndex = response.meta["playerIndex"]
        playerUrl = response.meta["playerUrl"]
        playerName = response.meta['playerName']
        matchId = response.meta['matchId']
        fifaId = response.meta['fifaId']
        country = response.meta['country']

        # Livescore birhtday
        birthDay = int(response.meta['birthDay'])
        birthMonth = int(response.meta['birthMonth'])
        birthYear = int(response.meta['birthYear'])

        countrySoFifa = response.xpath('//div[@class="info"]//div[@class="meta"]//a//span/@title').extract_first()

        # Sofifa birthday
        birthdaySoFifa = response.xpath('//div[@class="info"]//div[@class="meta"]//span').re_first(
            '\((.+)\)')  # Sep 9, 1991
        if birthdaySoFifa is None:
            print ('Cannot find birthday for sofifa id ' + str(fifaId))
            soFifaBirthMonth = birthMonth
            soFifaBirthDay = birthDay
            soFifaBirthYear = birthYear
        else:
            if birthdaySoFifa.find('/') > -1:
                slash = birthdaySoFifa.find('/')
                soFifaBirthDay = int(birthdaySoFifa[:slash])
                birthDayCut = birthdaySoFifa[slash + 1:]
                slash = birthDayCut.find('/')
                soFifaBirthMonth = int(birthDayCut[:slash])
                soFifaBirthYear = int(birthDayCut[slash + 1:len(birthDayCut)])
            else:
                comma = birthdaySoFifa.find(',') + 1
                try:
                    soFifaBirthYear = int(birthdaySoFifa[-4:])
                except:
                    soFifaBirthYear = birthYear
                try:
                    soFifaBirthDay = int(birthdaySoFifa[4:comma - 1])
                except:
                    soFifaBirthDay = birthDay
                try:
                    soFifaBirthMonthTxt = birthdaySoFifa[:3]
                    soFifaBirthMonth = strptime(soFifaBirthMonthTxt, '%b').tm_mon
                except:
                    soFifaBirthMonth = birthMonth

        # Compare birthdays

        if self.birthDayCheck and birthDay != 0:
            birthdaybool = (soFifaBirthDay == birthDay)
        else:
            birthdaybool = True

        if self.birthMonthCheck and birthMonth != 0:
            birthmonthbool = (soFifaBirthMonth == birthMonth)
        else:
            birthmonthbool = True

        if self.birthYearCheck and birthYear != 0:
            birthyearbool = (soFifaBirthYear == birthYear)
        else:
            birthyearbool = True

        if self.countryCheck:
            if countrySoFifa.find(country) > -1:
                countrybool = True
            else:
                countrybool = False
                # countrybool = (country == countrySoFifa)
        else:
            countrybool = True

        if (birthmonthbool and birthdaybool and birthyearbool and countrybool):

            # path to ajax.php that loads player history versions
            ajax_str = response.xpath('//script[contains(.,"playerHistoryUrl")]/text()').re_first('playerHistoryUrl\s*=\s*"(.*)";')
            s = requests.session()
            ajax_url = 'http://sofifa.com' + ajax_str
            ajax_response =  s.get(ajax_url)
            player_json = ajax_response.json()
            #id used in 'jump to version' url
            player_id_so_fifa = response.xpath('//div[@class="info"]//h1/text()').re_first(
                '(\d+)')
            #construct url to last version from json
            href = '/player/' + player_id_so_fifa + '?v=' + player_json['versions'][-1]['version'] + '&e=' + player_json['versions'][-1]['exportdate'] # Get the latest update page
            url = 'http://sofifa.com' + str(href)
            yield scrapy.Request(url, callback=self.recordPlayer,
                                 dont_filter=True,
                                 meta={'playerIndex': playerIndex, 'playerUrl': playerUrl,
                                       'playerName': playerName, 'matchId': matchId,
                                       'fifaId': fifaId, 'birthdaySoFifa': birthdaySoFifa, 'country': country})
            # Go to latest player update page
        elif self.searchEngine is not None:
            pass
        else:
            if len(str(fifaVersion)) == 1:
                fifaVersionStr = '0' + str(fifaVersion)
            else:
                fifaVersionStr = str(fifaVersion)
            playerUrlWithVersion = playerUrl + '&v=' + fifaVersionStr + '&hl=en-US'
            yield scrapy.Request(playerUrlWithVersion, callback=self.parsePlayer, dont_filter=True,
                                 meta={'fifaVersion': fifaVersion, 'playerIndex': playerIndex,
                                       'playerUrl': playerUrl, 'playerName': playerName, 'matchId': matchId,
                                       'birthDay': birthDay, 'birthMonth': birthMonth, 'birthYear': birthYear,
                                       'country': country})

    # Read and dump the player stats includings previous updates
    def recordPlayer(self, response):
        try:
            playerIndex = response.meta["playerIndex"]
            playerUrl = response.meta["playerUrl"]
            playerName = response.meta['playerName']
            matchId = response.meta['matchId']
            fifaId = response.meta['fifaId']
            birthdaySoFifa = response.meta['birthdaySoFifa']
            timestamp = response.xpath('//dt/a/@href').re('e=([0-9]+)')
            name = response.xpath('//div[@class="header"]/text()').re_first('(.+) \(ID:')
            generalStats = response.xpath(
                '//div[@class="cards"]//div[@class="card"]//div[@class="content"]//ul/li/span/text()').extract()
            statsValues = response.xpath(
                '//div[@class="description"]/ul/li/span[contains(@class,"p ")]/text()').extract()
            statsLabels = response.xpath('//div[@class="description"]/ul/li/text()').re('\t+([^\t]+)\t+')
            updates = response.xpath('//dd')
            feet = response.xpath('//div[@class="tab-content"]//div[@class="description"]/p/text()').re_first(
                '([0-9]+)\'')
            inch = response.xpath('//div[@class="tab-content"]//div[@class="description"]/p/text()').re_first(
                '\'([0-9]+)')
            weight = response.xpath('//div[@class="tab-content"]//div[@class="description"]/p/text()').re('([0-9]+)lbs')
            weight = weight[0]
            height = (float(feet) * 12 + float(inch)) * 2.54
            overallRating = generalStats[0]
            potential = generalStats[1]
            workRate = generalStats[2]
            if not potential.isdigit():
                potential = generalStats[2]

            idx = 2
            while workRate.find('/') == -1 and idx <= 4 and idx < len(workRate):
                workRate = generalStats[idx]
                idx += 1

            delimitor = workRate.find('/')
            attackingWorkRate = workRate[:delimitor - 1]
            defensiveWorkRate = workRate[delimitor + 2:]
            preferredFoot = response.xpath(
                '//div[@class="cards"]//div[@class="card"]//div[@class="content"]//ul/li/text()').re('\t+([^\t]+)\t+')
            # Work out the latest stats
            currentStats = collections.OrderedDict()
            currentStats['Timestamp'] = timestamp[0]
            currentStats['Overall rating'] = overallRating
            currentStats['Potential'] = potential
            currentStats['Preferred Foot'] = preferredFoot[0]
            currentStats['Attacking Work Rate'] = attackingWorkRate
            currentStats['Defensive Work Rate'] = defensiveWorkRate
            for i, label in enumerate(statsLabels):
                currentStats[label] = statsValues[i]

            # stats = collections.OrderedDict()
            # stats[timestamp[0]] = currentStats

            stats = list()
            stats.append(currentStats)

            player = Player()
            player['name'] = playerName
            player['matchId'] = matchId
            player['fifaId'] = fifaId
            player['birthday'] = birthdaySoFifa
            player['height'] = height
            player['weight'] = weight

            # Work out the previous stats from the update timeline
            for i, update in enumerate(updates):
                currentStats = collections.OrderedDict(currentStats)
                preferredFoot = update.xpath('span[@class="nowrap"]').re(
                    '<abbr>Preferred Foot:</abbr> ([A-Z]+[a-z]+) <i')
                attackingWorkRate = update.xpath('span[@class="nowrap"]').re(
                    '<abbr>Attacking Work Rate:</abbr> ([A-Z]+[a-z]+) <i')
                defensiveWorkRate = update.xpath('span[@class="nowrap"]').re(
                    '<abbr>Defensive Work Rate:</abbr> ([A-Z]+[a-z]+) <i')
                if len(preferredFoot) == 1:
                    currentStats['Preferred Foot'] = preferredFoot[0]
                if len(attackingWorkRate) == 1:
                    currentStats['Attacking Work Rate'] = attackingWorkRate[0]
                if len(defensiveWorkRate) == 1:
                    currentStats['Defensive Work Rate'] = defensiveWorkRate[0]

                labels = update.xpath('span[@class="nowrap"]').re('<abbr>(.+):</abbr> <span class="p ')
                values = update.xpath('span[@class="nowrap"]/span[contains(@class,"p ")]/text()').extract()
                if i < (len(updates) - 1):  # all updates
                    currentStats['Timestamp'] = timestamp[i + 1]
                else:
                    currentStats['Timestamp'] = self.fifaFirstStatsTimestamp
                for j, label in enumerate(labels):
                    currentStats[label] = values[2 * j]

                stats.append(currentStats)
                # stats[timestamp[i+1]] = currentStats

            # Dump stats
            player['stats'] = stats
            yield player

            print ('Exported ' + name + ',' + matchId + ',' + fifaId)
            filename = os.getcwd() + '..\\..\\DATA\\players_list\\2_export_list.txt'
            file = open(filename, 'a')
            file.write(name + ',' + matchId + ',' + fifaId + '\n')
        except:
            print ('No player found in Sofifa for: ' + playerName)
            filename = self.playerErrorFile
            file = open(filename, 'a')
            file.write(matchId + ',' + playerName + '\n')
