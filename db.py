import sqlite3
import datetime
import threading
import Queue

import sensordata, externaldata
import screen


class DBManager(threading.Thread):

	DAYS = 7

	tId = -1
	wait = 1
	con = None
	screen = None
	dbfile = "data/homeware-data.db"

	killEvent = None

	# SQLite query queue for execute() only
	# Tuples only
	qq = Queue.Queue()

	def __init__(self, killEvent, tId, screen=None, wait=60):
		super(DBManager, self).__init__()

		self.killEvent = killEvent

		self.tId = tId
		self.wait = wait
		self.dbfile = "data/homeware-data-" + str(self.DAYS) + "-days.db"
		self.screen = screen

	def run(self):
	
		if self.con is None:
			self.con = sqlite3.connect(self.dbfile, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)

		self.setup()

		self.con.commit()
		self.con.close()
		self.con = None

		while not self.killEvent.is_set():
			if self.qq.qsize() > 0:
				msg = "Dequeuing and exec-ing " + str(self.qq.qsize()) + " commands"
				if self.screen is not None:
					self.screen.updateStatus(msg)
				else:
					print msg

			if self.con is None:
				self.con = sqlite3.connect(self.dbfile, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)


			while not self.killEvent.is_set() and not self.qq.empty():
				qt = (0)
				try:
					qt = self.qq.get()
					rowc = 0
					with self.con:
						if len(qt) == 1:
							rowc += self.con.execute(qt[0]).rowcount
						else:
							rowc += self.con.execute(qt[0], qt[1]).rowcount
	
					if rowc > 0:
						msg = "Rows affected: " + str(rowc)
						if self.screen is not None:
							self.screen.updateStatus(msg)
						else: 
							print(msg)
				except:
					err = "Error: query = %s" % (qt,)
					#if self.screen is not None:
					#	self.screen.updateStatus(err)
					#else:
					#	print(err)

			self.killEvent.wait(self.wait)
			
			self.con.commit()
			self.con.close()
			self.con = None

	def setup(self):
		self.qq.put(("create table pir_data(time timestamp, score real, period real)",))
		self.qq.put(("create table env_data_temp1w(time timestamp, temp real)",))
		self.qq.put(("create table env_data_bmp085(time timestamp, temp real, pres real)",))
		self.qq.put(("create table env_data_dht22(time timestamp, temp real, hum real)",))
		self.qq.put(("create table w_data_obs(time timestamp, temp real, hum real)",))

	def insertEnvData(self, envData):
		if envData.getTemp1W()['time'] != None:
			self.qq.put(("insert into env_data_temp1w(time, temp) values (?, ?)", (envData.getTemp1W()['time'], envData.getTemp1W()['temp'])))
		if envData.getBMP085()['time'] != None:
			self.qq.put(("insert into env_data_bmp085(time, temp, pres) values (?, ?, ?)", (envData.getBMP085()['time'], envData.getBMP085()['temp'], envData.getBMP085()['pres'])))
		if envData.getDHT22()['time'] != None and envData.getDHT22()['temp'] != None and envData.getDHT22()['hum'] != None:
			self.qq.put(("insert into env_data_dht22(time, temp, hum) values (?, ?, ?)", (envData.getDHT22()['time'], envData.getDHT22()['temp'], envData.getDHT22()['hum'])))

	def insertWData(self, wData):
		if wData.getWData()['time'] != None:
			self.qq.put(("insert into w_data_obs(time, temp, hum) values (?, ?, ?)", (wData.getWData()['time'], wData.getWData()['temp'], wData.getWData()['hum'])))

	def insertPIRData(self, pirData):
		self.qq.put(("insert into pir_data(time, score, period) values (?, ?, ?)", (pirData.getCurrScore()['start'], pirData.getCurrScore()['score'], pirData.getAccumPeriod())))


	def purge(self): 
		d = datetime.datetime.now() - datetime.timedelta(days=DAYS)
		self.qq.put(("delete from pir_data where time < ?", (d,)))
		self.qq.put(("delete from env_data_temp1w where time < ?", (d,)))
		self.qq.put(("delete from env_data_bmp085 where time < ?", (d,)))
		self.qq.put(("delete from env_data_dht22 where time < ?", (d,)))
		self.qq.put(("delete from w_data_obs where time < ?", (d, )))

