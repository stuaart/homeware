import sqlite3
import datetime
import threading
import Queue

import sensordata
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

		while not self.killEvent.is_set():
			if self.qq.qsize() > 0:
				msg = "Dequeuing and exec-ing " + str(self.qq.qsize()) + " commands"
				if self.screen is not None:
					self.screen.updateStatus(msg)
				else:
					print msg

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
					if self.screen is not None:
						self.screen.updateStatus(err)
					else:
						print(err)

			self.killEvent.wait(self.wait)

		self.con.close()

	def setup(self):
		self.qq.put(("create table pir_data(state bool, time timestamp)",))
		self.qq.put(("create table env_data_temp1w(temp real, time timestamp)",))
		self.qq.put(("create table env_data_bmp085(temp real, pres real, time timestamp)",))

	def insertEnvData(self, envData):
		self.qq.put(("insert into env_data_temp1w(temp, time) values (?, ?)", (envData.getTemp1W()['temp'], envData.getTemp1W()['time'])))
		self.qq.put(("insert into env_data_bmp085(temp, pres, time) values (?, ?, ?)", (envData.getBMP085()['temp'], envData.getBMP085()['pres'], envData.getBMP085()['time'])))



	def insertPIRData(self, pirData):
		self.qq.put(("insert into pir_data(state, time) values (?, ?)", (pirData.getCurrState()['state'], pirData.getCurrState()['time'])))


	def purge(self): 
		d = datetime.datetime.now() - datetime.timedelta(days=DAYS)
		self.qq.put(("delete from pir_data where time < ?", (d,)))
		self.qq.put(("delete from env_data_temp1w where time < ?", (d,)))
		self.qq.put(("delete from env_data_bmp085 where time < ?", (d,)))

