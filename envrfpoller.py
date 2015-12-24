import threading, serial, logging, datetime, time

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


class EnvRFPoller(threading.Thread):

	killEvent = None
	
	wait = 1
	screen = None

	serDevice = None

	envData = None

	def __init__(self, killEvent, envData, screen=None, wait=5):
		super(EnvRFPoller, self).__init__()

		self.killEvent = killEvent
		self.wait = wait
		self.envData = envData

		self.screen = screen

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


	def run(self):
		logging.info("EnvRFPoller running in SensorsManager")

		while not self.killEvent.is_set():
			logging.debug("EnvRFPoller cycle")

			# Read two packets from the serial/radio
			self.serDevice = serial.Serial(SERIAL_DEVICE, SERIAL_BAUD, timeout=SERIAL_TIMEOUT)
			lines = None
			for c in self.serDevice.read(LLAP_PKT_LEN * 2):
				if lines == None:
					lines = []
				lines.append(c)
			logging.debug("lines = " +  str(lines))
			if lines != None and len(lines) == LLAP_PKT_LEN * 2:
				readings = []
				readings.append(self.readPkt(lines[:LLAP_PKT_LEN]))
				readings.append(self.readPkt(lines[LLAP_PKT_LEN:]))
				for reading in readings:
					if reading != None:
						if reading[0] != None and reading[0] == HUM_TOKEN:
							self.envData.setDHT22Hum(float(reading[2]), reading[1])
						elif reading[0] != None and reading[0] == TEMP_TOKEN:
							self.envData.setDHT22Temp(float(reading[2]), reading[1])
			else:
				if self.screen is not None:
					self.screen.updateStatus("No reading yet from DHT22")
				else:
					print "No reading yet from DHT22"

			logging.debug("End EnvRFPoller cycle")

			self.serDevice.close()

			self.killEvent.wait(self.wait)


	
