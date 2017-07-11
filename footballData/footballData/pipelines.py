# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import os
import collections
from scrapy import signals
from scrapy.exporters import XmlItemExporter

class JsonWriterPipeline(object):
    def __init__(self):
        self.file = open('items.json', 'wb')
    
    def process_item(self, item, spider): 
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item
    
class JsonWriterPipeline2(object):
    def open_spider(self, spider):
        self.file = open('items.jl', 'w')
    def close_spider(self, spider):
        self.file.close()
    def process_item(self, item, spider):
        line = json.dumps(item) + "\n"
        self.file.write(line)
        return item

class XmlExportPipeline(object):

    def __init__(self):
        self.files = {}

    @classmethod
    def from_crawler(cls, crawler):
         pipeline = cls()
         crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
         crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
         return pipeline

    def spider_opened(self, spider):
        file = open('%s.xml' % spider.name, 'w+b')
        self.files[spider] = file
        self.exporter = XmlItemExporter(file)
        self.exporter.start_exporting()
        pass
    
    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        file = self.files.pop(spider)
        file.close()

    def process_item(self, item, spider):
        if spider.name is 'match':
            league = item['league'].strip(' \t\n\r')
            if league == "":
                league = "Unknown"
            filename = 'matches/'  + item['country']   + '/' + league + '/' + item['season'] + '/' + str(item['stage']) +'/%s.xml' % item['matchId']
            if not os.path.exists(os.path.dirname(filename)):
                try:
                    os.makedirs(os.path.dirname(filename))
                except OSError as exc: # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise
            file = open(filename, 'w+b')
            self.files[item['matchId']] = file
            self.exporter = XmlItemExporter(file)
            self.exporter.fields_to_export = [
                'country',
                'league',
                'season',
                'stage',
                'matchId', 
                'date',
                'homeTeamId',
                'awayTeamId',
                'homeTeamFullName', 
                'awayTeamFullName',
                'homeTeamAcronym',
                'awayTeamAcronym',
                'homeTeamGoal',
                'awayTeamGoal',
                'homePlayers',
                'awayPlayers',
                'homePlayersId',
                'awayPlayersId',
                'homePlayersX',
                'awayPlayersX',
                'homePlayersY',
                'awayPlayersY',
                'goal',
                'shoton',
                'shotoff',
                'foulcommit',
                'card',
                'cross',
                'corner',
                'possession']
            
            self.exporter.export_item(item)
            return item
        elif spider.name is 'player':
            filename = 'players/' + item['name']+'_'+item['matchId']+'_'+item['fifaId']+'.xml'
            if not os.path.exists(os.path.dirname(filename)):
                try:
                    os.makedirs(os.path.dirname(filename))
                except OSError as exc: # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise
            file = open(filename, 'w+b')
            self.files[item['name']] = file
            self.exporter = XmlItemExporter(file)
            self.exporter.fields_to_export = [
                'name',
                'matchId',
                'fifaId',
                'birthday',
                'height',
                'weight',
                'stats']
            self.exporter.export_item(item)
            return item