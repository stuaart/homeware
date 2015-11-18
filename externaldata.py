
class WeatherData:

	wData = None

	def __init__(self):
		self.wData = {'temp' : None, 'hum' : None, 'time' : None}

	def setObs(self, temp, hum, time):
		self.wData['temp'] = temp
		self.wData['hum'] = hum
		self.wData['time'] = time

	def getWData(self):
		return self.wData
