#!/usr/bin/python

import RPi.GPIO as GPIO
import threading
import time

import leds
import sensors
import db

pins = {'mode' : GPIO.BCM, 'pir' : 7, 'pir_led' : 25}

killEvent = threading.Event()
killEvent.clear()


lm = leds.LEDManager(pins)

threads = {}
threads['dbm'] = db.DBManager(killEvent, len(threads), wait=600)
threads['ssm'] = sensors.SensorsManager(killEvent, len(threads), pins, lm, threads['dbm'], wait=300)

threads['dbm'].start()
threads['ssm'].start()

try:
	while True:
		time.sleep(0.1)
except KeyboardInterrupt:
	killEvent.set()
	for t in threads.keys(): 
		threads[t].join()

	GPIO.cleanup()
	exit()

