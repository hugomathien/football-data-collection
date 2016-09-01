# Collecting football data
## Welcome !
This is an open source project aiming to provide tools for people to collect and format large set of data about football matches and players. The project is essentially a crawler written in Python and relies on two sources:

- Football matches, end of game statistics and in-game events. You can crawl these with the **MatchSpider** [http://football-data.mx-api.enetscores.com/](http://football-data.mx-api.enetscores.com/) 
- Player attributes from EA Sports FIFA video game [http://sofifa.com](http://sofifa.com). You can crawl these with the **PlayerSpider**

## Using Scrapy

To facilitate the crawling, I use an open source python library called [Scrapy](http://scrapy.org). 
Have a look at the tutorials on their webpage if you're not already familiar with the lib.

## Collection process

- 1: collect the matches stats and team lineups using the Match Crawler
- 2: build a list of unique player names
- 3: loop this list with the Player Crawler. Create a list of the players you haven't successfully crawled and again follow the third step, adjusting the crawling paramaters. Repeat until you've got all the players you need.

## Using Search Engines
Sometimes, a player name is rather complicated or not consistent accross different sources. To help identify a player, the algorithm can be parameterized to make use of search engines. Google is a prime choice thanks to its large database and tolerance to mispelling player names. Unfortunately, the Google API has a limited usage rate per day. Hence I suggest you use Yahoo or Bing first and only use Google for those players you stuggle to find.
