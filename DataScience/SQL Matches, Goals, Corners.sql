/****** Script for SelectTopNRows command from SSMS  ******/
SELECT DISTINCT TOP (1000) Matches.ExternalId, Matches.HomeTeam_Id, AwayTeam_Id, Date, Count(Goals.ExternalId)
  FROM [FootballData].[dbo].[Matches]
  LEFT JOIN [FootballData].[dbo].[Goals]
  ON Matches.ExternalId = Goals.MatchId
  LEFT JOIN [FootballData].[dbo].Corners
  ON Matches.ExternalId = Corners.MatchId
  WHERE Country like '%England%' 
	AND Season like '%2017/2018%'
	AND League like '%Premier League%'
GROUP BY Matches.ExternalId,HomeTeam_Id, AwayTeam_Id, Date
ORDER BY Date DESC
