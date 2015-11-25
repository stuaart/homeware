import json, urllib2, datetime, threading, time, logging

import db, screen, externaldata

class WeatherManager(threading.Thread):
	
	killEvent = None
	
	tId = -1
	wait = 1
	screen = None

	wData = None
	datapointURL = None

	def __init__(self, killEvent, tId, dbManager=None, screen=None, wait=1800):
		
		super(WeatherManager, self).__init__()

		self.killEvent = killEvent
		self.tId = tId
		self.wait = wait

		self.dbManager = dbManager
		self.screen = screen

		self.wData = externaldata.WeatherData()

		datapointURL = "http://datapoint.metoffice.gov.uk/public/data/val/wxobs/all/json/3354?res=hourly&key="

		f = open('datapoint.key')
		key = f.read()

		self.datapointURL = datapointURL + key


	def run(self):
		logging.info("WeatherManager running [tid=" + str(self.tId) + "]")

		while not self.killEvent.is_set():
	

			res = urllib2.urlopen(self.datapointURL)
			obj = json.loads(res.read())
			d = datetime.datetime.strptime(obj['SiteRep']['DV']['dataDate'], "%Y-%m-%dT%H:%M:%SZ")
			newWData = True
			if self.wData.getWData()['time'] != None and d == self.wData.getWData()['time']:
				newWData = False

			latest_ = obj['SiteRep']['DV']['Location']['Period']
			latest = latest_[len(latest_)-1]['Rep']

			if latest != None:
				try: 
					readings = None
					if isinstance(latest, dict):
						readings = latest
					elif len(latest) > 0:
						readings = latest[len(latest)-1]

					self.wData.setObs(float(readings['T']), float(readings['H']), d)
			
					if self.screen is not None:
						self.screen.updateEntry(wData=self.wData)
	
					if self.dbManager is not None and newWData:
						self.dbManager.insertWData(self.wData)

				except KeyError:
					logging.error("Problem with weather data: " + str(latest))

			self.killEvent.wait(self.wait)


