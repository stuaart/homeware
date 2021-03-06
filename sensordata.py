import datetime, logging

import envrfpoller

class PIRData:

	prevState = None
	currState = None
	
	currScore = None
	accumPeriod = 5 # Accumulate score in 5 minute buckets

	def __init__(self, accumPeriod=5, startTime=datetime.datetime.now()):
		self.prevState = {'state' : False, 'time' : None}
		self.currState = {'state' : False, 'time' : None}
		self.currScore = {'score' : 0, 'start' : startTime, 
					       'end' : startTime + datetime.timedelta(minutes=accumPeriod)}
		self.accumPeriod = accumPeriod

	def setState(self, dbManager, s, t):
		self.prevState = self.currState
		self.currState['state'] = s
		self.currState['time'] = t
		if self.currScore['end'] > t:
			if s: 
				self.currScore['score'] += 1
		else:
			dbManager.insertPIRData(self)
			dbManager.writeStateNow(pirData=self)
			logging.debug("writeStateNow(pirData) called from PIRData")
			self.currScore['start'] = t
			self.currScore['end'] = t + datetime.timedelta(minutes=self.accumPeriod)
			self.currScore['score'] = 0

	def getCurrState(self):
		return self.currState

	def getPrevState(self):
		return self.prevState

	def getCurrScore(self):
		return self.currScore

	def getAccumPeriod(self):
		return self.accumPeriod


class EnergyData:

	# Gas and electricity readings / counts
	gas = None
	elec = None

	def __init__(self):
		elec = None



class EnvData: # For capturing environmental data e.g., temp, humidity, etc.

	temp1W = None
	bmp085 = None
	dht22 = None # My own custom built temp / rhum sensor
	wt = None 	 # WirelessThings temp / rhum sensors
	
	def __init__(self):
		self.temp1W = {'temp' : None, 'time' : None}
		self.bmp085 = {'temp' : None, 'pres' : None, 'time' : None}
		self.dht22 = {'temp' : None, 'hum' : None, 'time' : None}
		self.wt = {}
		for t in envrfpoller.WT_IDS:
			self.wt[t] = {'temp' : None, 'hum' : None, 'time' : None}

	def setTemp1W(self, temp, time):
		self.temp1W['temp'] = temp
		self.temp1W['time'] = time

	def setBMP085(self, temp, pres, time):
		self.bmp085['temp'] = temp
		self.bmp085['pres'] = pres
		self.bmp085['time'] = time
	
	def setDHT22(self, temp, hum, time):
		self.dht22['temp'] = temp
		self.dht22['hum'] = hum
		self.dht22['time'] = time

	def setDHT22Temp(self, temp, time):
		self.dht22['temp'] = temp
		self.dht22['time'] = time

	def setDHT22Hum(self, hum, time):
		self.dht22['hum'] = hum
		self.dht22['time'] = time

	def setWTTemp(self, _id, temp, time):
		self.wt[_id]['temp'] = temp
		self.wt[_id]['time'] = time

	def setWTHum(self, _id, hum, time):
		self.wt[_id]['hum'] = hum
		self.wt[_id]['time'] = time

	def getTemp1W(self):
		return self.temp1W
#		return (self.temp1W['temp'], self.temp1W['time'])

	def getBMP085(self):
		return self.bmp085
#		return (self.bmp085['temp'], self.bmp085['pres'], self.bmp085['time'])

	def getDHT22(self):
		return self.dht22

	def getWT(self):
		return self.wt
