import os, glob, time, datetime, threading, serial
import RPi.GPIO as GPIO
import Adafruit_BMP.BMP085 as BMP085

import sensordata

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

SERIAL_DEVICE  = "/dev/ttyAMA0"
SERIAL_BAUD	   = 9600
SERIAL_TIMEOUT = 10

# LLAP standard
LLAP_PKT_LEN = 12
START_B 	 = 0
ID_B1 		 = 1
ID_B2 		 = 2
PADDING_B 	 = "-"
DATA_B_START = 3
TOKEN_LEN	 = 3
HUM_TOKEN	 = "HUM"
TEMP_TOKEN	 = "TMP"



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

	serDevice = None

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
		
		self.serDevice = serial.Serial(SERIAL_DEVICE, SERIAL_BAUD, timeout=SERIAL_TIMEOUT)

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

	def readPkt(self, line):
		_start = line[START_B]
		_id = line[ID_B1] + "" + line[ID_B2]
		line = line[DATA_B_START:]
		_data = ""
		for c in line:
			if c != PADDING_B:
				_data += c

		if _data[:TOKEN_LEN] == HUM_TOKEN:
			return (HUM_TOKEN, datetime.datetime.now(), _data[TOKEN_LEN:])
		elif _data[:TOKEN_LEN] == TEMP_TOKEN:
			return (TEMP_TOKEN, datetime.datetime.now(), _data[TOKEN_LEN:])


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

			# Read two packets from the serial/radio
			lines = None
			for c in s.serDevice.read(LLAP_PKT_LEN * 2):
				if lines == None:
					lines = []
				lines.append(c)
	
			if lines != None:
				readings = []
				readings.append(s.readPkt(lines[:LLAP_PKT_LEN]))
				readings.append(s.readPkt(lines[LLAP_PKT_LEN:]))
				for reading in readings:
					if reading[0] == HUM_TOKEN:
						s.envData.setDHT22Hum(float(reading[2]), reading[1])
					elif reading[0] == TEMP_TOKEN:
						s.envData.setDHT22Temp(float(reading[2]), reading[1])
			else:
				if s.screen is not None:
					s.screen.updateStatus("Error accessing DHT22 via serial interface")
				else:
					print "Error accessing DHT22 via serial interface"



			if s.screen is not None:
				s.screen.updateEntry(envData=s.envData)

			if s.dbManager is not None:
				s.dbManager.insertEnvData(s.envData)

			s.killEvent.wait(s.wait)

		s.serDevice.close()


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

		if self.dbManager is not None:
			self.pirData.setState(self.dbManager, GPIO.input(self.pins['pir']), 
								  datetime.datetime.now())

		if self.screen:
			self.screen.updateEntry(pirData=self.pirData)

		if GPIO.input(self.pins['pir']) == GPIO.HIGH:
			self.ledManager.on('pir_led')
		else:
			self.ledManager.off('pir_led')


