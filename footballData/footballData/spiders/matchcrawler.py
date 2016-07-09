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
    countries = ['Scotland']
    #seasons = ['2009/2010','2008/2009']
    #seasons = ['2012/2013','2011/2012','2010/2011']
    seasons = ['2015/2016','2014/2015','2013/2014']
    #seasons = ['2015/2016']
    stages = []
    matches = []
    
    #COUNTRY
    def parse(self,response):
        for country in self.countries:
            href = response.xpath('//li[text()[contains(.,"'+country+'")]]/@data-snippetparams').re_first('"params":"(.+)"')
            url = 'http://football-data.mx-api.enetscores.com/page/xhr/standings/' + href
            yield scrapy.Request(url, callback=self.parse_league,meta={'country':country})
    
    #LEAGUE
    def parse_league(self,response):
        country = response.meta['country']
        selection = response.xpath('//div[@class="mx-dropdown mx-country-template-stage-selector"]/ul/li/text()').extract()
        league = selection[322]
        
        href = response.xpath('//li[text()[contains(.,"'+league+'")]]/@data-snippetparams').re_first('"params":"(.+)"')
        url = 'http://football-data.mx-api.enetscores.com/page/xhr/standings/' + href
        yield scrapy.Request(url, callback=self.parse_season,meta={'country':country,'league':league})
      
    #SEASON  
    def parse_season(self,response):
        country = response.meta['country']
        league = response.meta['league']
        
        for season in self.seasons:
            href = response.xpath('//li[text()[contains(.,"'+season+'")]]/@data-snippetparams').re_first('"params":"(.+)"')
            url = 'http://football-data.mx-api.enetscores.com/page/xhr/standings/' + href
            yield scrapy.Request(url, callback=self.parse_matches,meta={'country':country,'league':league,'season':season})
    
    #OPEN SEASON
    def parse_matches(self,response):
        country = response.meta['country']
        league = response.meta['league']
        season = response.meta['season']
        href = response.xpath('//div[contains(@class,"mx-matches-finished-betting_extended")]/@data-params').re_first('params":"(.+)/')
        url = 'http://football-data.mx-api.enetscores.com/page/xhr/stage_results/' + href
        first_stage_url = url + '/1'
        yield scrapy.Request(first_stage_url, callback=self.parse_stage, meta={'href':href,'country':country,'league':league,'season':season})
    
    #LOOP STAGES
    def parse_stage(self,response):
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
            yield scrapy.Request(full_stage_url, callback=self.parse_all_matches_in_stage,dont_filter = True, meta={'stage':stage,'country':country,'league':league,'season':season})
            
    #MATCHES IN STAGE  
    def parse_all_matches_in_stage(self, response):
        country = response.meta['country']
        league = response.meta['league']
        season = response.meta['season']
        stage = response.meta['stage']
        matchesDataEventList = response.xpath('//a[@class="mx-link mx-hide"]/@data-event').extract()
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
            date = dateList[counter]
            match["date"] = date
            
            url = 'http://football-data.mx-api.enetscores.com/page/xhr/match_center/' + matchId + '/'
            #full_url = 'http://football-data.mx-api.enetscores.com/page/xhr/event_gamecenter/' + game + '%2Fv2_lineup/'
            counter += 1
            yield scrapy.Request(url, callback=self.parse_match_general_stats,meta={'match':match})
            
    #MATCH GENERAL STATS
    def parse_match_general_stats(self, response):
        match = response.meta['match']
        
        stage = response.xpath('//span[@class="mx-stage-name"]/text()').re_first('\s([0-9]+)')
        match["stage"] = stage
        
        fullTeamName = response.xpath('//div[@class="mx-team-away-name mx-break-small"]/a/text()').re('\t+([^\n]+[^\t]+)\n+\t+')
        teamId = response.xpath('//div[@class="mx-team-away-name mx-break-small"]/a/@data-team').extract()
        teamAcronym = response.xpath('//div[@class="mx-team-away-name mx-show-small"]/a/text()').re('\t+([^\n]+[^\t]+)\n+\t+')
        homeTeamGoal = response.xpath('//div[@class="mx-res-home mx-js-res-home"]/@data-res').extract_first()
        awayTeamGoal = response.xpath('//div[@class="mx-res-away mx-js-res-away"]/@data-res').extract_first()
        
        match['homeTeamFullName'] = fullTeamName[0]
        match['awayTeamFullName'] = fullTeamName[1]
        match['homeTeamAcronym'] = teamAcronym[0]
        match['awayTeamAcronym'] = teamAcronym[1]
        match['homeTeamId'] = teamId[0]
        match['awayTeamId'] = teamId[1]
        match['homeTeamGoal'] = homeTeamGoal
        match['awayTeamGoal'] = awayTeamGoal
        matchId = match['matchId']
        
        url = 'http://football-data.mx-api.enetscores.com/page/xhr/event_gamecenter/' + matchId + '%2Fv2_lineup/'
        yield scrapy.Request(url, callback=self.parse_squad,meta={'match':match})

    #MATCH SQUADS
    def parse_squad(self, response):
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
            yield scrapy.Request(url, callback=self.parse_match_events,meta={'match':match})
        else:
            yield match
            
    
    #MATCH EVENTS
    def parse_match_events(self, response):
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
            print 'No Match Events: ' + str(e)
            
        yield match
        
        
        #post match stats: http://json.mx-api.enetscores.com/live_data/actionzones/1710068/0?_=1465892810155
        #post match stats: http://football-data.mx-api.enetscores.com/page/xhr/match_center/1710068%2Fv2/
        # player home/away
        # playersHA = response.xpath('//div[contains(@class,"mx-lineup-pos")]/@class').re('mx-pos-team-([a-z]{4})\s')
        # print response.body