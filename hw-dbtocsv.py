#!/usr/bin/python

import sqlite3
import csv

datadir = "/home/pi/homeware/data"
dbfile = datadir + "/homeware-data-7-days.db"

con = sqlite3.connect(dbfile, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)

with open(datadir + 'env_data_temp1w.csv', 'wb') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quotechar='|', 
					    quoting=csv.QUOTE_MINIMAL)
	writer.writerow(['timestamp', 'env_data_temp1w'])
	for row in con.execute("select env_data_temp1w from " + table):
		writer.writerow([str(row[0]), str(row[1])])

with open(datadir + 'env_data_bmp085.csv', 'wb') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quotechar='|', 
					    quoting=csv.QUOTE_MINIMAL)
	writer.writerow(['timestamp', 'env_data_bmp085_temp', 'env_data_bmp085_pres'])
	for row in con.execute("select env_data_bmp085 from " + table):
		writer.writerow([str(row[0]), str(row[1]), str(row[2]])

with open(datadir + 'env_data_pir.csv', 'wb') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quotechar='|', 
					    quoting=csv.QUOTE_MINIMAL)
	writer.writerow(['timestamp', 'env_data_pir'])
	for row in con.execute("select env_data_pir from " + table):
		writer.writerow([str(row[0]), str(row[1])])

con.close()

