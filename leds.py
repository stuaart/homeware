
import RPi.GPIO as GPIO
import threading
import time

class LEDManager:

	bt = {}
	pins = None

	def __init__(self, pins):
		self.pins = pins
		GPIO.setmode(self.pins['mode'])
		for p in self.pins.keys(): 
			GPIO.setup(self.pins[p], GPIO.OUT)
			self.off(p)
			self.bt[p] = None

	def on(self, ledID):
		GPIO.output(self.pins[ledID], GPIO.HIGH)

	def off(self, ledID):
		GPIO.output(self.pins[ledID], GPIO.LOW)

	def blink_(self, ledID, gap, n):
		for i in range (0, n):
			self.on(ledID); time.sleep(gap)
			self.off(ledID); time.sleep(gap)


	def blink(self, ledID, gap, n):
		if self.bt[ledID] == None or not self.bt[ledID].isAlive():
			self.bt[ledID] = threading.Thread(target=self.blink_, 
											  args=[ledID, gap, n])
			self.bt[ledID].start()

