#!/usr/bin/python

import sqlite3, json, datetime
import json

datadir = "/home/pi/homeware/data"
dbfile = datadir + "/homeware-data.db"

with sqlite3.connect(dbfile, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES) as con:

	def get(table, posTime, yAxis):
		c = con.execute("select * from " + table + "_latest")
		row = c.fetchone()
		return [str(row[yAxis]), str(row[posTime])]

	latest = {
		'env_data' : 
			{'env_data_temp1w' : get("env_data_temp1w", 0, 1),
			 'env_data_bmp085_temp' : get("env_data_bmp085", 0, 1), 
			 'env_data_bmp085_pres' : get("env_data_bmp085", 0, 2), 
			 'env_data_dht22_temp' : get("env_data_dht22", 0, 1), 
			 'env_data_dht22_hum' : get("env_data_dht22", 0, 2)
			},
		'w_data_obs' :
			{'w_data_obs_temp' : get("w_data_obs", 0, 1),
			 'w_data_obs_hum' : get("w_data_obs", 0, 2)
			},
		'pir_data' : get("pir_data", 0, 1)
	}


with open(datadir + '/latest-state.json', 'w') as outfile:
	json.dump(latest, outfile, sort_keys = True, indent = 4, ensure_ascii=False)
