#import pyodbc 
#import pandas as pd
#cnxn = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
#                      "Server=Martin-PC\SQLEXPRESS;"
#                      "Database=FootballData;"
#                      "Trusted_Connection=yes;")


#cursor = cnxn.cursor()
#cursor.execute('SELECT * FROM Matches')



#df.head(5)

#for row in cursor:
#   print('row = %r' % (row,))


import pymssql
import _mssql
import pandas as pd

## instance a python db connection object- same form as psycopg2/python-mysql drivers also
print('f')
conn = pymssql.connect(server="localhost",  database="FootballData")# You can lookup the port number inside SQL server. 
#conn = _mssql.connect("(local)",  "martin", "Waveform*88" )# You can lookup the port number inside SQL server. 
conn.close()
## Hey Look, college data
#
#stmt = "SELECT * FROM Matches WHERE Id = 5"
#df = pd.read_sql(stmt,conn)
# Excute Query here
print('g')
#df = pd.read_sql(stmt,conn)

#df.head(5)