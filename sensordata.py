class PIRData:

	prevState = None
	currState = None

	def __init__(self):
		self.prevState = {'state' : False, 'time' : None}
		self.currState = {'state' : False, 'time' : None}

	def setState(self, s, t):
		self.prevState = self.currState
		self.currState['state'] = s
		self.currState['time'] = t

	def getCurrState(self):
		return self.currState

	def getPrevState(self):
		return self.prevState


class EnvData:

	temp1W = None
	bmp085 = None
	
	def __init__(self):
		self.temp1W = {'temp' : None, 'time' : None}
		self.bmp085 = {'temp' : None, 'pres' : None, 'time' : None}

	def setTemp1W(self, temp, time):
		self.temp1W['temp'] = temp
		self.temp1W['time'] = time

	def setBMP085(self, temp, pres, time):
		self.bmp085['temp'] = temp
		self.bmp085['pres'] = pres
		self.bmp085['time'] = time

	def getTemp1W(self):
		return self.temp1W
#		return (self.temp1W['temp'], self.temp1W['time'])

	def getBMP085(self):
		return self.bmp085
#		return (self.bmp085['temp'], self.bmp085['pres'], self.bmp085['time'])


