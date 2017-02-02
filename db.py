import sqlite3, datetime, threading, logging
import Queue

import sensordata, externaldata
import screen


class DBManager(threading.Thread):

	tId = -1
	wait = 1
	screen = None
	datadir = "/home/pi/homeware/data/"
	dbfile = datadir + "homeware-data.db"

	killEvent = None

	# SQLite query queue for execute() only
	# Tuples only
	qq = Queue.Queue()


	def __init__(self, killEvent, tId, screen=None, wait=60):
		super(DBManager, self).__init__()

		self.killEvent = killEvent

		self.tId = tId
		self.wait = wait
		self.screen = screen


	def run(self):
	
		self.setup()

		while not self.killEvent.is_set():
			if self.qq.qsize() > 0:
				msg = "Dequeuing and exec-ing " + str(self.qq.qsize()) + " commands"
				if self.screen is not None:
					self.screen.updateStatus(msg)
				else:
					print msg

				logging.debug(msg)

			con = sqlite3.connect(self.dbfile, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)


			while not self.killEvent.is_set() and not self.qq.empty():
				qt = (0)
				try:
					qt = self.qq.get()
					rowc = 0
					with con:
						if len(qt) == 1:
							rowc += con.execute(qt[0]).rowcount
						else:
							rowc += con.execute(qt[0], qt[1]).rowcount
	
					if rowc > 0:
						msg = "Rows affected: " + str(rowc)
						if self.screen is not None:
							self.screen.updateStatus(msg)
						else: 
							print(msg)

						logging.debug(msg)

				except:
					err = "Error: query = %s" % (qt,)
					logging.error(err)

			con.commit()
			con.close()
			
			self.killEvent.wait(self.wait)
			

	def setup(self):
		self.qq.put(("create table pir_data(time timestamp, score real, period real)",))
		self.qq.put(("create table env_data_temp1w(time timestamp, temp real)",))
		self.qq.put(("create table env_data_bmp085(time timestamp, temp real, pres real)",))
		self.qq.put(("create table env_data_dht22(time timestamp, temp real, hum real)",))
		self.qq.put(("create table env_data_wt(time timestamp, id text, temp real, hum real)",))
		self.qq.put(("create table w_data_obs(time timestamp, temp real, hum real)",))

		self.qq.put(("create table pir_data_latest(time timestamp, score real, period real)",))
		self.qq.put(("create table env_data_temp1w_latest(time timestamp, temp real)",))
		self.qq.put(("create table env_data_bmp085_latest(time timestamp, temp real, pres real)",))
		self.qq.put(("create table env_data_dht22_latest(time timestamp, temp real, hum real)",))
#		self.qq.put(("create table env_data_wt_latest(time timestamp, id text, temp real, hum real)",))
		self.qq.put(("create table w_data_obs_latest(time timestamp, temp real, hum real)",))

	# Make sure we don't insert duplicate values
	t1wLastTime = 0
	bmp085LastTime = 0
	dht22LastTime = 0
	wtLastTime = {}

	def insertEnvData(self, envData):
		t1w = envData.getTemp1W()
		if t1w['time'] != None and t1w['time'] != self.t1wLastTime:
			self.qq.put(("insert into env_data_temp1w(time, temp) values (?, ?)", (t1w['time'], t1w['temp'])))
		self.t1wLastTime = t1w['time']

		bmp085 = envData.getBMP085()
		if bmp085['time'] != None and bmp085['time'] != self.bmp085LastTime:
			self.qq.put(("insert into env_data_bmp085(time, temp, pres) values (?, ?, ?)", (bmp085['time'], bmp085['temp'], bmp085['pres'])))
		self.bmp085LastTime = bmp085['time']

		dht22 = envData.getDHT22()
		if dht22['time'] != None and dht22['time'] != self.dht22LastTime and dht22['temp'] != None and dht22['hum'] != None:
			self.qq.put(("insert into env_data_dht22(time, temp, hum) values (?, ?, ?)", (dht22['time'], dht22['temp'], dht22['hum'])))
		self.dht22LastTime = dht22['time']

		wt = envData.getWT()
		if len(wt) > 0:
			for k, v in wt.iteritems():
				if self.wtLastTime and k in self.wtLastTime and self.wtLastTime[k] != v['time'] and v['temp'] != None and v['hum'] != None:
					self.qq.put(("insert into env_data_wt(time, id, temp, hum) values (?, ?, ?, ?)",
							    (v['time'], k, v['temp'], v['hum'])))
				self.wtLastTime[k] = v['time']


	def insertWData(self, wData):
		if wData.getWData()['time'] != None:
			self.qq.put(("insert into w_data_obs(time, temp, hum) values (?, ?, ?)", (wData.getWData()['time'], wData.getWData()['temp'], wData.getWData()['hum'])))

	def insertPIRData(self, pirData):
		self.qq.put(("insert into pir_data(time, score, period) values (?, ?, ?)", (pirData.getCurrScore()['start'], pirData.getCurrScore()['score'], pirData.getAccumPeriod())))

	
	def writeStateNow(self, pirData=None, envData=None, wData=None):
		
		con = sqlite3.connect(self.dbfile, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)

		with con:
			if envData != None:
				if envData.getTemp1W()['time'] != None:
					con.execute("delete from env_data_temp1w_latest")
					con.execute("insert into env_data_temp1w_latest(time, temp) values (?, ?)", (envData.getTemp1W()['time'], envData.getTemp1W()['temp']))
		
				if envData.getBMP085()['time'] != None:
					con.execute("delete from env_data_bmp085_latest")
					con.execute("insert into env_data_bmp085_latest(time, temp, pres) values (?, ?, ?)", (envData.getBMP085()['time'], envData.getBMP085()['temp'], envData.getBMP085()['pres']))

				if envData.getDHT22()['time'] != None and envData.getDHT22()['temp'] != None and envData.getDHT22()['hum'] != None:
					con.execute("delete from env_data_dht22_latest")
					con.execute("insert into env_data_dht22_latest(time, temp, hum) values (?, ?, ?)", (envData.getDHT22()['time'], envData.getDHT22()['temp'], envData.getDHT22()['hum']))

			if pirData != None and pirData.getCurrScore()['start'] != None:
					con.execute("delete from pir_data_latest")
					con.execute("insert into pir_data_latest(time, score, period) values (?, ?, ?)", (pirData.getCurrScore()['start'], pirData.getCurrScore()['score'], pirData.getAccumPeriod()))

			if wData != None and wData.getWData()['time'] != None:
				con.execute("delete from w_data_obs_latest")
				con.execute("insert into w_data_obs_latest(time, temp, hum) values (?, ?, ?)", (wData.getWData()['time'], wData.getWData()['temp'], wData.getWData()['hum']))

		con.commit()
		con.close()


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
		self.qq.put(("delete from env_data_wt where time < ?", (d,)))
		self.qq.put(("delete from w_data_obs where time < ?", (d, )))

