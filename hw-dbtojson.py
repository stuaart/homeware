#!/usr/bin/python

import sqlite3
import json

datadir = "/home/pi/homeware/data"
dbfile = datadir + "/homeware-data-7-days.db"

con = sqlite3.connect(dbfile, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)

def get(table, posTime, yAxis):
	o = []
	n = 1
	for row in con.execute("select * from " + table):
		o.append([n, str(row[yAxis]), str(row[posTime])])
		n += 1
	return o

t1 = get("env_data_temp1w", 0, 1)
t2 = get("env_data_bmp085", 0, 1)
t3 = get("env_data_bmp085", 0, 2)
t4 = get("pir_data", 0, 1)

env_data = {'env_data' : {'env_data_temp1w' : t1, 'env_data_bmp085_temp' : t2, 'env_data_bmp085_pres' : t3}}

pir_data = {'pir_data' : t4}

con.close()


with open(datadir + '/env_data.json', 'w') as outfile:
  json.dump(env_data, outfile, sort_keys = True, indent = 4, ensure_ascii=False)

with open(datadir + '/pir_data.json', 'w') as outfile:
  json.dump(pir_data, outfile, sort_keys = True, indent = 4, ensure_ascii=False)

