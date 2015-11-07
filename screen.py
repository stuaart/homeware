import curses
import time

class Screen:

	PIR_DATA 		= 1
	ENV_DATA_TEMP1W = 2
	ENV_DATA_BMP085 = 3
	ENV_DATA_DHT22	= 4

	LABEL_COL = 2

	stypeCol 				  = {}
	stypeCol[PIR_DATA] 		  = 20
	stypeCol[ENV_DATA_TEMP1W] = 20
	stypeCol[ENV_DATA_BMP085] = 20
	stypeCol[ENV_DATA_DHT22]  = 20

	scr = None

	def __init__(self):
		self.scr = curses.initscr()
		curses.noecho()
		curses.cbreak()
		self.scr.keypad(1)
		self.scr.addstr(self.scr.getmaxyx()[0]-3, 0, "---")
		self.scr.addstr(self.scr.getmaxyx()[0]-1, 0, "---")
		self.scr.addstr(self.PIR_DATA, self.LABEL_COL, " Motion", curses.A_BOLD)
		self.scr.addstr(self.ENV_DATA_TEMP1W, self.LABEL_COL, "1w temp", 
						curses.A_BOLD)
		self.scr.addstr(self.ENV_DATA_BMP085, self.LABEL_COL, " BMP085", 
						curses.A_BOLD)
		self.scr.addstr(self.ENV_DATA_DHT22, self.LABEL_COL, " DHT22", 
						curses.A_BOLD)



	def getScreen(self):
		return self.scr

	def close(self):
		curses.nocbreak()
		self.scr.keypad(0)
		curses.echo()
		curses.endwin()

	def updateEntryText(self, stype, text):
		self.scr.move(stype, self.stypeCol[stype])
		self.scr.clrtoeol()
		self.scr.addstr(stype, self.stypeCol[stype], text)
		self.scr.refresh()
	
	def updateEntry(self, pirData=None, envData=None):
		if pirData is not None:
			entry = "CurrState=" + str(pirData.getCurrState()['state']) + " [" 
			entry += str(pirData.getCurrState()['time'])
			entry += "]" #; PrevState=" + str(pirData.getPrevState()['state']) + " ["
#			entry += str(pirData.getPrevState()['time']) + "]"

			self.updateEntryText(self.PIR_DATA, entry)

		elif envData is not None:
			try:
				t1wStr = "{0:0.2f}*C".format(envData.getTemp1W()['temp'])
		#		therm1wStr += " [CMA {0:0.2f}*C]".format(self.cmaTherms[1])			
				t1wStr += " [" + str(envData.getTemp1W()['time']) + "]"				
				self.updateEntryText(self.ENV_DATA_TEMP1W, t1wStr)

			except ValueError:
				self.updateStatus("Error formatting 1W temp data")
	
			try:
				bmpStr =  "{0:0.2f}*C".format(envData.getBMP085()['temp'])
				bmpStr += " {0:0.2f}kPa".format(envData.getBMP085()['pres'] / 1000)
				bmpStr += " [" + str(envData.getBMP085()['time']) + "]"
				self.updateEntryText(self.ENV_DATA_BMP085, bmpStr)

			except ValueError:
				self.updateStatus("Error formatting BMP085 data")

			try:
				dht22Str = "{0:0.2f}*C".format(envData.getDHT22()['temp'])
				dht22Str += " {0:0.2f}%".format(envData.getDHT22()['hum'])
				dht22Str += " [" + str(envData.getDHT22()['time']) + "]"

				self.updateEntryText(self.ENV_DATA_DHT22, dht22Str)
			except ValueError:
				self.updateStatus("Error formatting DHT22 data")


	# NOTE: blocks
	def updateStatus(self, text, sleep=0):
		srow = self.scr.getmaxyx()[0] - 2
		self.scr.move(srow, 0)
		self.scr.clrtoeol()
		self.scr.addstr(srow, 2, text)
		self.scr.refresh()
		if sleep > 0:
			time.sleep(sleep)





