#!/usr/bin/python

import sqlite3, json, datetime
import json

DAYS = 7 # How many days to pull from db

datadir = "/home/pi/homeware/data"
dbfile = datadir + "/homeware-data-7-days.db"

d = datetime.datetime.now() - datetime.timedelta(days=DAYS)

with sqlite3.connect(dbfile, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES) as con:

	def get(table, posTime, yAxis):
		
		o = []
		n = 1

		for row in con.execute("select * from " + table + " where time > ?", (d,)):
			o.append([n, str(row[yAxis]), str(row[posTime])])
			n += 1
		return o

	t1 = get("env_data_temp1w", 0, 1)
	t2 = get("env_data_bmp085", 0, 1)
	t3 = get("env_data_bmp085", 0, 2)
	t4 = get("env_data_dht22", 0, 1)
	t5 = get("env_data_dht22", 0, 2)
	t6 = get("pir_data", 0, 1)

	env_data = {'env_data' : {'env_data_temp1w' : t1, 'env_data_bmp085_temp' : t2, 'env_data_bmp085_pres' : t3, 'env_data_dht22_temp' : t4, 'env_data_dht22_hum' : t5}}

	pir_data = {'pir_data' : t6}


with open(datadir + '/env_data.json', 'w') as outfile:
  json.dump(env_data, outfile, sort_keys = True, indent = 4, ensure_ascii=False)

with open(datadir + '/pir_data.json', 'w') as outfile:
  json.dump(pir_data, outfile, sort_keys = True, indent = 4, ensure_ascii=False)

