import requests
import sqlite3 as lite
import datetime

api_key = "71a93e1e6160a194d3ef9c3a2cf00e19/"
url = 'https://api.forecast.io/forecast/' + api_key

cities = {"Phoenix": '33.572154,-112.090132',
	"SaltLakeCity": '40.778996,-111.932630',
	"SanFrancisco": '37.727239,-123.032229',
	"Seattle": '47.620499,-122.350876',
	"Washington": '38.904103,-77.017229'
	}

end_date = datetime.datetime.now() 

con = lite.connect('weather.db')
cur = con.cursor()

cur.execute('drop table daily_temp')
con.commit()

cities.keys()
with con:
	cur.execute('CREATE TABLE IF NOT EXISTS daily_temp ( day_of_reading INT, Phoenix REAL, SaltLakeCity REAL, SanFrancisco REAL, Seattle REAL, Washington REAL);')

query_date = end_date - datetime.timedelta(days=30) #

with con:
    while query_date < end_date:
        cur.execute("INSERT INTO daily_temp(day_of_reading) VALUES (?)", (query_date.strftime('%Y-%m-%dT12:00:00'),))
        query_date += datetime.timedelta(days=1)

for k,v in cities.iteritems():
    query_date = end_date - datetime.timedelta(days=30) 
    while query_date < end_date:
        #query for the value
        print (url + v + ',' +  query_date.strftime('%Y-%m-%dT12:00:00'))
        r = requests.get(url + v + ',' +  query_date.strftime('%Y-%m-%dT12:00:00'))

        with con:
            cur.execute('UPDATE daily_temp SET ' + k + ' = ' + str(r.json()['daily']['data'][0]['temperatureMax']) + ' WHERE day_of_reading = ' + query_date.strftime("'%Y-%m-%dT12:00:00'"))

        query_date += datetime.timedelta(days=1) 

con.close()

import pandas as pd
import collections
import requests
import sqlite3 as lite
import datetime

con = lite.connect('weather.db')
cur = con.cursor()

df = pd.read_sql_query("SELECT * FROM daily_temp ORDER BY day_of_reading",con,index_col='day_of_reading')

print df

month_change = collections.defaultdict(int)
for col in df.columns:
    city_vals = df[col].tolist()
    city_change = 0
    for k,v in enumerate(city_vals):
        if k < len(city_vals) - 1:
            city_change = max(city_change, abs(city_vals[k] - city_vals[k+1]))
    month_change[col] = city_change 

def keywithmaxval(d):
	return max(d, key=lambda k: d[k])


max_city = keywithmaxval(month_change)

print "The city with the largest range is city %s" % max_city
print "With " + str(month_change[max_city]) + " temperature difference between " + df.index[0] + " and " + df.index[-1]

import matplotlib.pyplot as plt

plt.bar(range(len(month_change)), month_change.values())
plt.show()


