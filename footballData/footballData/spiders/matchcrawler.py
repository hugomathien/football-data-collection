import scrapy
import json
import sys
from footballData.items import Match

class MatchSpider(scrapy.Spider):
    name = "match"
    detailedStats = True
    allowed_domains = ["football-data.mx-api.enetscores.com",'json.mx-api.enetscores.com']
    start_urls = [
        "http://football-data.mx-api.enetscores.com/page/xhr/standings/"
    ]
    countries = ['Spain']
    #countries = ['Germany']
    #seasons = ['2009/2010','2008/2009','2012/2013','2011/2012','2010/2011']
    seasons = ['2016/2017']
    stages = []
    matches = []
    
    #COUNTRY
    def parse(self,response):
        for country in self.countries:
            href = response.xpath('//li[text()[contains(.,"'+country+'")]]/@data-snippetparams').re_first('"params":"(.+)"')
            url = 'http://football-data.mx-api.enetscores.com/page/xhr/standings/' + href
            yield scrapy.Request(url, callback=self.parseLeague,meta={'country':country})

    #LEAGUE
    def parseLeague(self,response):
        country = response.meta['country']
        selection = response.xpath('//div[@class="mx-dropdown mx-country-template-stage-selector"]/ul/li/text()').extract()
        
        league = selection[322]
        #indexes = []
        #for i, j in enumerate(selection):
        #    if country in j:
        #        indexes.append(i)
        #        
        #league = selection[indexes[0]]
        league = "Spain Primera Division"
        
        href = response.xpath('//li[text()[contains(.,"'+league+'")]]/@data-snippetparams').re_first('"params":"(.+)"')
        url = 'http://football-data.mx-api.enetscores.com/page/xhr/standings/' + href
        yield scrapy.Request(url, callback=self.parseSeason,meta={'country':country,'league':league})
      
    #SEASON  
    def parseSeason(self,response):
        country = response.meta['country']
        league = response.meta['league']
        
        for season in self.seasons:
            href = response.xpath('//li[text()[contains(.,"'+season+'")]]/@data-snippetparams').re_first('"params":"(.+)"')
            url = 'http://football-data.mx-api.enetscores.com/page/xhr/standings/' + href
            yield scrapy.Request(url, callback=self.parseMatches,meta={'country':country,'league':league,'season':season})
    
    #OPEN SEASON
    def parseMatches(self,response):
        country = response.meta['country']
        league = response.meta['league']
        season = response.meta['season']
        href = response.xpath('//div[contains(@class,"mx-matches-finished-betting_extended")]/@data-params').re_first('params":"(.+)/')
        url = 'http://football-data.mx-api.enetscores.com/page/xhr/stage_results/' + href
        first_stage_url = url + '/1'
        yield scrapy.Request(first_stage_url, callback=self.parseStage, meta={'href':href,'country':country,'league':league,'season':season})
    
    #LOOP STAGES
    def parseStage(self,response):
        country = response.meta['country']
        league = response.meta['league']
        season = response.meta['season']
        href = response.meta['href']
        
        url = 'http://football-data.mx-api.enetscores.com/page/xhr/stage_results/' + href
        totalPages = response.xpath('//span[contains(@class,"mx-pager-next")]/@data-params').re_first('total_pages": "([0-9]+)"')
        
        if not self.stages:
            iterateStages = range(1,int(totalPages)+1)
        else:
            iterateStages = self.stages
            
        for stage in iterateStages:
            full_stage_url = url + '/' + str(stage)
            yield scrapy.Request(full_stage_url, callback=self.parseAllMatchesInStage,dont_filter = True, meta={'stage':stage,'country':country,'league':league,'season':season})
            
    #MATCHES IN STAGE  
    def parseAllMatchesInStage(self, response):
        country = response.meta['country']
        league = response.meta['league']
        season = response.meta['season']
        stage = response.meta['stage']
        matchesDataEventList = response.xpath('//a[contains(@class, "mx-link")]/@data-event').extract()
        dateList = response.xpath('//span[@class="mx-time-startdatetime"]/text()').extract()
     
        matchList = list()
        if len(self.matches) >= 1:
            for match in self.matches:
                matchList.append(matchesDataEventList[match-1])
        else:
            matchList = list(matchesDataEventList)
            
        counter = 0
   
        for matchId in matchList:
            match = Match()
            match["matchId"] = matchId
            match["country"] = country
            match["league"] = league
            match["season"] = season
            #date = dateList[counter]
            match["date"] = dateList[0]
            
            url = 'http://football-data.mx-api.enetscores.com/page/xhr/match_center/' + matchId + '/'
            counter += 1
            yield scrapy.Request(url, callback=self.parseMatchGeneralStats,meta={'match':match})
            
    #MATCH GENERAL STATS
    def parseMatchGeneralStats(self, response):
        match = response.meta['match']
        
        stage = response.xpath('//span[@class="mx-stage-name"]/text()').re_first('\s([0-9]+)')
        match["stage"] = stage
        
        fullTeamNameHome = response.xpath('//div[contains(@class, "mx-team-home-name mx-break-small")]/a/text()').re('\t+([^\n]+[^\t]+)\n+\t+')
        fullTeamNameAway = response.xpath('//div[@class="mx-team-away-name mx-break-small"]/a/text()').re('\t+([^\n]+[^\t]+)\n+\t+')
        teamIdHome = response.xpath('//div[@class="mx-team-home-name mx-break-small"]/a/@data-team').extract()
        teamIdAway = response.xpath('//div[@class="mx-team-away-name mx-break-small"]/a/@data-team').extract()
        homeAcronym = response.xpath('//div[@class="mx-team-away-name mx-show-small"]/a/text()').re('\t+([^\n]+[^\t]+)\n+\t+')
        awayAcronym = response.xpath('//div[@class="mx-team-home-name mx-show-small"]/a/text()').re('\t+([^\n]+[^\t]+)\n+\t+')
        homeTeamGoal = response.xpath('//div[@class="mx-res-home mx-js-res-home"]/@data-res').extract_first()
        awayTeamGoal = response.xpath('//div[@class="mx-res-away mx-js-res-away"]/@data-res').extract_first()
        
        match['homeTeamFullName'] = fullTeamNameHome
        match['awayTeamFullName'] = fullTeamNameAway
        match['homeTeamAcronym'] = homeAcronym
        match['awayTeamAcronym'] = awayAcronym
        match['homeTeamId'] = teamIdHome
        match['awayTeamId'] = teamIdAway
        match['homeTeamGoal'] = homeTeamGoal
        match['awayTeamGoal'] = awayTeamGoal
        matchId = match['matchId']
        
        url = 'http://football-data.mx-api.enetscores.com/page/xhr/event_gamecenter/' + matchId + '%2Fv2_lineup/'
        yield scrapy.Request(url, callback=self.parseSquad,meta={'match':match})

    #MATCH SQUADS
    def parseSquad(self, response):
        match = response.meta['match']
        players = response.xpath('//div[@class="mx-lineup-incident-name"]/text()').extract()
        playersId = response.xpath('//a/@data-player').extract()
        subsId = response.xpath('//div[@class="mx-lineup-container mx-float-left"]//div[@class="mx-collapsable-content"]//a/@data-player').extract()
        titularPlayerId = [x for x in playersId if x not in subsId]
        
        # player x y pitch position
        playersX = response.xpath('//div[contains(@class,"mx-lineup-pos")]/@class').re('mx-pos-row-([0-9]+)\s')
        playersY = response.xpath('//div[contains(@class,"mx-lineup-pos")]/@class').re('mx-pos-col-([0-9]+)\s')
        playersPos = response.xpath('//div[contains(@class,"mx-lineup-pos")]/@class').re('mx-pos-([0-9]+)\s')
        
        match['homePlayers'] = players[:11]
        match['homePlayersId'] = titularPlayerId[:11]
        match['homePlayersX'] = playersX[:11]
        match['homePlayersY'] = playersY[:11]       
       
        match['awayPlayers'] = players[11:]
        match['awayPlayersId'] = titularPlayerId[11:22]
        match['awayPlayersX'] = playersX[11:]
        match['awayPlayersY'] = playersY[11:]
        
        matchId = match['matchId']
        if self.detailedStats:
            url = 'http://json.mx-api.enetscores.com/live_data/actionzones/' + matchId + '/0?_=1'
            yield scrapy.Request(url, callback=self.parseMatchEvents,meta={'match':match})
        else:
            yield match
    
    #MATCH EVENTS
    def parseMatchEvents(self, response):
        #match = response.meta['match']
        #matchId = match['matchId']
        #url = 'http://json.mx-api.enetscores.com/live_data/actionzones/' + matchId + '/0?_=1'
        match = response.meta['match']
        jsonresponse = json.loads(response.body_as_unicode())
        
        try:
            goal = [s for s in jsonresponse["i"] if s['type']=='goal']
            shoton = [s for s in jsonresponse["i"] if s['type']=='shoton']
            shotoff = [s for s in jsonresponse["i"] if s['type']=='shotoff']
            foulcommit = [s for s in jsonresponse["i"] if s['type']=='foulcommit']
            card = [s for s in jsonresponse["i"] if s['type']=='card']
            corner = [s for s in jsonresponse["i"] if s['type']=='corner']
            subtypes = [s for s in jsonresponse["i"] if 'subtype' in s]
            cross = [s for s in subtypes if s['subtype']=='cross']
            possession = [s for s in subtypes if s['subtype']=='possession']
            
            match['goal'] = goal
            match['shoton'] = shoton
            match['shotoff'] = shotoff
            match['foulcommit'] = foulcommit
            match['card'] = card
            match['cross'] = cross
            match['corner'] = corner
            match['possession'] = possession
        
        except:
            e = sys.exc_info()[0]
            print ('No Match Events: ' + str(e))
            
        yield match
