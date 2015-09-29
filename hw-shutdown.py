#!/usr/bin/python

import RPi.GPIO as GPIO
from subprocess import call
import threading
import time
import leds

P_NAME 		= "hw-shutdown"
WAIT 		= 10

pins = {'mode' : GPIO.BCM, 'shutdown' : 10, 'shutdown_led' : 9}
killEvent = threading.Event()
killEvent.set()


def issueShutdown(channel):
	global lm
	global killEvent
	lm.blink('shutdown_led', 0.1, 20)
	print "[" + P_NAME + "] Issuing /sbin/shutdown -h now"
	call(["/sbin/shutdown", "-h", "now"])
	killEvent.clear()

lm = leds.LEDManager(pins)

GPIO.setmode(pins['mode'])
GPIO.setup(pins['shutdown'], GPIO.IN)
GPIO.add_event_detect(pins['shutdown'], GPIO.RISING, callback=issueShutdown, bouncetime=300)

try:
	print "[" + P_NAME + "] Starting..."
	while killEvent.is_set():
		time.sleep(0.1)
except KeyboardInterrupt:
	print "[" + P_NAME + "] Exiting..."
	killEvent.clear()
	GPIO.cleanup()
	exit()
