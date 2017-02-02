import threading, serial, logging, datetime, time

SERIAL_DEVICE  = "/dev/ttyACM0"
SERIAL_BAUD	   = 9600
SERIAL_TIMEOUT = 20

# LLAP standard: [a,<id_b1>,<id_b2>,<token>x4,<data>x4,<padding>]
# E.g., aABRHUM18.50-
LLAP_PKT_LEN = 12
START_B 	 = 0
ID_B1 		 = 1
ID_B2 		 = 2
PADDING_B 	 = "-"
DATA_B_START = 3
TOKEN_LEN	 = 4

WT_IDS = { "GARAGE" : "AA", "LOFT" : "AR" } #, "ELEC" : "AB" } need to deal with optical pulse 
O_IDS = { "PIANO" : "SR" }

TOKENS = { "HUM_TOKEN" : "RHUM", "TEMP_TOKEN" : "TEMP", "VCC_TOKEN" : "PVCC" }

class EnvRFPoller(threading.Thread):

	dbManager = None
	killEvent = None
	
	screen = None

	ser = None

	envData = None

	def __init__(self, killEvent, envData, dbManager=None, screen=None):
		super(EnvRFPoller, self).__init__()

		self.dbManager = dbManager
		self.killEvent = killEvent
		self.envData = envData

		self.screen = screen

	def readPkt(self, line):
		try:
			_start = line[START_B]
			_id = line[ID_B1] + "" + line[ID_B2]
			line = line[DATA_B_START:]
			_data = ""
			for c in line:
				if c != PADDING_B:
					_data += c
			for token in TOKENS.values():
				if token == _data[:TOKEN_LEN]:
					return (_id, token, datetime.datetime.now(), _data[TOKEN_LEN:])

			return None

		except IndexError:
			return None

	def run(self):
		logging.info("EnvRFPoller running in SensorsManager")
		self.ser = serial.Serial(SERIAL_DEVICE, SERIAL_BAUD, timeout=SERIAL_TIMEOUT)

		line = []
		c = None
		c_ = False

		while not self.killEvent.is_set() and self.ser.isOpen():
			try:

				for c in self.ser.read(1):
					if c == 'a':
						if c_:
							pkt = self.readPkt(line)
							if pkt == None:
								logging.error("Bad packet parse from DHT22, serial data = " + str(line))
								if self.screen is not None:
									self.screen.updateStatus("Bad packet parse from DHT22, serial data = " + str(line))
							else:
								logging.info("Serial packet parsed at " + str(datetime.datetime.now()) + "; packet = " + str(pkt))
								try:
									if pkt[0] == O_IDS["PIANO"]:
										if pkt[1] == TOKENS["HUM_TOKEN"]:
											self.envData.setDHT22Hum(float(pkt[3]), pkt[2])
										elif pkt[1] == TOKENS["TEMP_TOKEN"]:
											self.envData.setDHT22Temp(float(pkt[3]), pkt[2])
										elif pkt[1] == TOKENS["VCC_TOKEN"]:
											logging.info("VCC at " + str(pkt[2]) + " = " + str(pkt[3]))
									else:
										err = True
										for key in WT_IDS.keys():
											if pkt[0] == WT_IDS[key]:
												if pkt[1] == TOKENS["HUM_TOKEN"]:
													self.envData.setWTHum(key, float(pkt[3]), pkt[2])
												elif pkt[1] == TOKENS["TEMP_TOKEN"]:
													self.envData.setWTTemp(key, float(pkt[3]), pkt[2])
												err = False
										if err:
											logging.error("Got unrecognised packet: " + str(pkt))
								except ValueError:
									logging.error("Problem formatting DHT22 packet value; packet value = " + str(pkt))

						line = []
						line.append(c)
					else:
						line.append(c)

					c_ = True
				if self.dbManager != None:
					self.dbManager.writeStateNow(envData=self.envData)
					logging.debug("writeStateNow(envData) called from EnvRFPoller")

			except serial.SerialException:
				logging.error("SerialException raised")


		self.ser.close()
	
