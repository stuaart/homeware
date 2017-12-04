import os, glob, time, datetime, threading, serial, logging
import RPi.GPIO as GPIO
import Adafruit_BMP.BMP085 as BMP085

import sensordata, envrfpoller

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

	envRFPoller = None

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

		# Frequency at which this polls *must* be < the frequency of data being sent 
		self.envRFPoller = envrfpoller.EnvRFPoller(killEvent, self.envData, dbManager, screen)
		self.envRFPoller.start()


	def getEnvData(self):
		return self.envData


	def getPIRData(self):
		return self.pirData


	def run(self):

		logging.info("SensorsManager running [tid=" + str(self.tId) + "]")


		while not self.killEvent.is_set():

			if self.pirPoll:
				self.pirCallback(self.pins['pir'])
		
			temp1w = None	
			if self.read1w() != None:	
				temp1w = self.read1w()[0]

			if self.cmaTherms[0] == 0:
				self.cmaTherms[1] = temp1w
				self.cmaTherms[0] = 1
			else:
				cmaTherms_ = (temp1w + self.cmaTherms[0] * self.cmaTherms[1]) / (self.cmaTherms[0] + 1)
				self.cmaTherms[0] += 1
				self.cmaTherms[1] = cmaTherms_

			if temp1w != None:
				self.envData.setTemp1W(temp1w, datetime.datetime.now())
			else:
				logging.error("temp1w is None")
			self.envData.setBMP085(self.bmpDev.read_temperature(), 
							       self.bmpDev.read_pressure(),
							       datetime.datetime.now())

			self.dbManager.writeStateNow(envData=self.envData)
			logging.debug("writeStateNow(envData) called from SensorsManager")


			if self.screen is not None:
				self.screen.updateEntry(envData=self.envData)

			if self.dbManager is not None:
				self.dbManager.insertEnvData(self.envData)

			self.killEvent.wait(self.wait)



	def read1wRaw(self):
		try:
			f = open(self.therm1wDev, 'r')
			lines = f.readlines()
			f.close()
			return lines
		except TypeError:
			logging.error("read1wRaw() is not finding 1w temp sensor; try putting dtoverlay=w1-gpio in /boot/config.txt")
			return None


	def read1w(self):
		lines = self.read1wRaw()
		if lines == None:
			return None
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

		if self.dbManager is not None:
			self.pirData.setState(self.dbManager, GPIO.input(self.pins['pir']), 
								  datetime.datetime.now())

		if self.screen:
			self.screen.updateEntry(pirData=self.pirData)

		if GPIO.input(self.pins['pir']) == GPIO.HIGH:
			self.ledManager.on('pir_led')
		else:
			self.ledManager.off('pir_led')


