#!/usr/bin/python

import sqlite3, csv, datetime

DAYS = 90 # How many days to pull from db

datadir = "./data/"
dbfile = datadir + "homeware-data.db"

d = datetime.datetime.now() - datetime.timedelta(days=DAYS)

with sqlite3.connect(dbfile, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES) as con:

	with open(datadir + 'env_data_temp1w.csv', 'wb') as csvfile:
		writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
		writer.writerow(['timestamp', 'env_data_temp1w'])
		for row in con.execute("select * from env_data_temp1w where time > ?", (d,)):
			writer.writerow([str(row[0]), str(row[1])])

	with open(datadir + 'env_data_bmp085.csv', 'wb') as csvfile:
		writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
		writer.writerow(['timestamp', 'env_data_bmp085_temp', 'env_data_bmp085_pres'])
		for row in con.execute("select * from env_data_bmp085 where time > ?", (d,)):
			writer.writerow([str(row[0]), str(row[1]), str(row[2])])

	with open(datadir + 'env_data_pir.csv', 'wb') as csvfile:
		writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
		writer.writerow(['timestamp', 'env_data_pir_score', 'env_data_pir_period'])
		for row in con.execute("select * from pir_data where time > ?", (d,)):
			writer.writerow([str(row[0]), str(row[1]), str(row[2])])

	with open(datadir + 'env_data_dht22.csv', 'wb') as csvfile:
		writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
		writer.writerow(['timestamp', 'env_data_dht22_temp', 'env_data_dht22_hum'])
		for row in con.execute("select * from env_data_dht22 where time > ?", (d,)):
			writer.writerow([str(row[0]), str(row[1]), str(row[2])])


#	con.close()

