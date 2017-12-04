#!/usr/bin/python

import sqlite3, json, datetime
import json

DAYS = 7 # How many days to pull from db

datadir = "./data"
dbfile = datadir + "/homeware-data.db"

d = datetime.datetime.now() - datetime.timedelta(days=DAYS)

def get(table, posTime, yAxis, _id=None):
		
	with sqlite3.connect(dbfile, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES) as con:
		o = []
		n = 1

		res = None
		if _id != None:
			res = con.execute("select * from " + table + " where time > ? and id = ?", (d, _id))
		else:
			res = con.execute("select * from " + table + " where time > ?", (d,))
	
		for row in res:
			o.append([n, str(row[yAxis]), str(row[posTime])])
			n += 1
		return o


env_data = {'env_data' : 
				{'env_data_temp1w' : get("env_data_temp1w", 0, 1),
				 'env_data_bmp085_temp' : get("env_data_bmp085", 0, 1), 
				 'env_data_bmp085_pres' : get("env_data_bmp085", 0, 2), 
				 'env_data_dht22_temp' : get("env_data_dht22", 0, 1), 
				 'env_data_dht22_hum' : get("env_data_dht22", 0, 2)}
		   }

#env_data_wt(time timestamp, id text, temp real, hum real)

with sqlite3.connect(dbfile, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES) as con:
	res = con.execute("select distinct id from env_data_wt")
	env_data_wt = {}
	for row in res:
		print row[0]
		env_data_wt[str(row[0])] = {
				 'env_data_wt_temp' : get("env_data_wt", 0, 2, row[0]),
			     'env_data_wt_hum' : get("env_data_wt", 0, 3, row[0])}

w_data_obs = {'w_data_obs' :
				{'w_data_obs_temp' : get("w_data_obs", 0, 1),
				 'w_data_obs_hum' : get("w_data_obs", 0, 2)}
			 }

pir_data = {'pir_data' : get("pir_data", 0, 1)}


with open(datadir + '/env_data.json', 'w') as outfile:
	json.dump(env_data, outfile, sort_keys = True, indent = 4, ensure_ascii=False)

with open(datadir + '/pir_data.json', 'w') as outfile:
	json.dump(pir_data, outfile, sort_keys = True, indent = 4, ensure_ascii=False)

with open(datadir + "/w_data_obs.json", 'w') as outfile:
	json.dump(w_data_obs, outfile, sort_keys = True, indent = 4, ensure_ascii = False)

with open(datadir + "/env_data_wt.json", 'w') as outfile:
	json.dump(env_data_wt, outfile, sort_keys = True, indent = 4, ensure_ascii = False)
