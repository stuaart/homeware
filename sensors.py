import threading
import RPi.GPIO as GPIO
import os 
import glob 
import time 
import Adafruit_BMP.BMP085 as BMP085
import datetime

import sensordata

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

class SensorsManager(threading.Thread):

	killEvent = None

	tId = -1
	wait = 1
	pirPoll = False

	ledManager = None
	dbManager = None
	screen = None
	exitFlag = False
	
	pins = None
	
	therm1wDev = None
	bmpDev = None

	cmaTherms = [0, 0] # n, cma

	envData = None
	pirData = None


	def __init__(self, killEvent, tId, pins, ledManager, dbManager=None, 
				 screen=None, wait=60, pirPoll=False):

		super(SensorsManager, self).__init__()

		self.killEvent = killEvent

		self.tId = tId
		self.wait = wait
		self.pirPoll = pirPoll

		self.ledManager = ledManager
		self.dbManager = dbManager
		self.screen = screen

		self.pins = pins

		self.envData = sensordata.EnvData()
		self.pirData = sensordata.PIRData()
		
		GPIO.setmode(self.pins['mode'])
		GPIO.setup(self.pins['pir'], GPIO.IN)

		if not self.pirPoll:
			GPIO.add_event_detect(self.pins['pir'], GPIO.BOTH, 
								  callback=self.pirCallback)

		try:
			self.therm1wDev = (glob.glob('/sys/bus/w1/devices/' + '28*')[0]) + '/w1_slave'
		except IndexError:
			if self.screen is not None:
				self.screen.updateStatus("Error accessing 1w thermometer", 1)
			else:
				print "Error accessing 1w thermometer"

		self.bmpDev = BMP085.BMP085()


	def getEnvData(self):
		return self.envData

	def getPIRData(self):
		return self.pirData


	def run(s):

		if s.screen is not None:
			s.screen.updateStatus("SensorsManager running [tid=" + 
									 str(s.tId) + "]")
		else: 
			print "SensorsManager running [tid=" + str(s.tId) + "]"


		while not s.killEvent.is_set():

			if s.pirPoll:
				s.pirCallback(self.pins['pir'])

			temp1w = s.read1w()[0]

			if s.cmaTherms[0] == 0:
				s.cmaTherms[1] = temp1w
				s.cmaTherms[0] = 1
			else:
				cmaTherms_ = (temp1w + s.cmaTherms[0] * s.cmaTherms[1]) / (s.cmaTherms[0] + 1)
				s.cmaTherms[0] += 1
				s.cmaTherms[1] = cmaTherms_

			s.envData.setTemp1W(temp1w, datetime.datetime.now())
			s.envData.setBMP085(s.bmpDev.read_temperature(), 
							    s.bmpDev.read_pressure(),
							    datetime.datetime.now())

			if s.screen is not None:
				s.screen.updateEntry(envData=s.envData)

			if s.dbManager is not None:
				s.dbManager.insertEnvData(s.envData)

			s.killEvent.wait(s.wait)


	def read1wRaw(self):
		f = open(self.therm1wDev, 'r')
		lines = f.readlines()
		f.close()
		return lines


	def read1w(self):
		lines = self.read1wRaw()
		while lines[0].strip()[-3:] != 'YES':
			time.sleep(0.2)
			lines = self.read1wRaw()
		equals_pos = lines[1].find('t=')
		if equals_pos != -1:
			temp_string = lines[1][equals_pos+2:]
			temp_c = float(temp_string) / 1000.0
			temp_f = temp_c * 9.0 / 5.0 + 32.0
			return temp_c, temp_f


	def pirCallback(self, channel):
		if channel != self.pins['pir']:
			if self.screen:
				self.screen.updateStatus("Error on PIR callback, channel = " + 
										 str(channel))
			else:
				print "Error on PIR callback, channel = " + str(channel)
			return

		self.pirData.setState(GPIO.input(self.pins['pir']), 
							  datetime.datetime.now())

		if self.dbManager is not None:
			self.dbManager.insertPIRData(self.pirData)
	
		if self.screen:
			self.screen.updateEntry(pirData=self.pirData)

		if GPIO.input(self.pins['pir']) == GPIO.HIGH:
			self.ledManager.on('pir_led')
		else:
			self.ledManager.off('pir_led')

