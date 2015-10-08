#!/usr/bin/python

import sqlite3
import csv

datadir = "/home/pi/homeware/data/"
dbfile = datadir + "homeware-data-7-days.db"

with sqlite3.connect(dbfile, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES) as con:

	with open(datadir + 'env_data_temp1w.csv', 'wb') as csvfile:
		writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
		writer.writerow(['timestamp', 'env_data_temp1w'])
		for row in con.execute("select * from env_data_temp1w"):
			writer.writerow([str(row[0]), str(row[1])])

	with open(datadir + 'env_data_bmp085.csv', 'wb') as csvfile:
		writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
		writer.writerow(['timestamp', 'env_data_bmp085_temp', 'env_data_bmp085_pres'])
		for row in con.execute("select * from env_data_bmp085"):
			writer.writerow([str(row[0]), str(row[1]), str(row[2])])

	with open(datadir + 'env_data_pir.csv', 'wb') as csvfile:
		writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
		writer.writerow(['timestamp', 'env_data_pir_score', 'env_data_pir_period'])
		for row in con.execute("select * from pir_data"):
			writer.writerow([str(row[0]), str(row[1]), str(row[2])])

#	con.close()

