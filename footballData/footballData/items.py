# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class Match(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    country = scrapy.Field()
    league = scrapy.Field()
    season = scrapy.Field()
    stage = scrapy.Field()
    matchId = scrapy.Field()
    date = scrapy.Field()
    homeTeamFullName = scrapy.Field()
    awayTeamFullName = scrapy.Field()
    homeTeamAcronym = scrapy.Field()
    awayTeamAcronym = scrapy.Field()
    homeTeamId = scrapy.Field()
    awayTeamId = scrapy.Field()
    homeTeamGoal = scrapy.Field()
    awayTeamGoal = scrapy.Field()
    
    homePlayers = scrapy.Field()
    awayPlayers = scrapy.Field()
    homePlayersId = scrapy.Field()
    awayPlayersId = scrapy.Field()
    homePlayersX = scrapy.Field()
    awayPlayersX = scrapy.Field()
    homePlayersY = scrapy.Field()
    awayPlayersY = scrapy.Field()
    
    goal = scrapy.Field()
    shoton = scrapy.Field()
    shotoff = scrapy.Field()
    foulcommit = scrapy.Field()
    card = scrapy.Field()
    cross = scrapy.Field()
    corner = scrapy.Field()
    possession = scrapy.Field()
        
class Player(scrapy.Item):
    matchId = scrapy.Field()
    fifaId = scrapy.Field()
    name = scrapy.Field()
    birthday = scrapy.Field()
    height = scrapy.Field()
    weight = scrapy.Field()
    stats = scrapy.Field()
    
    def keys(self):
        return self._values.keys()