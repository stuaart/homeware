#!/usr/bin/python

import RPi.GPIO as GPIO
import threading

import leds
import sensors
import db
import screen
import weather

pins = {'mode' : GPIO.BCM, 'pir' : 7, 'pir_led' : 25}

screen = screen.Screen()

killEvent = threading.Event()
killEvent.clear()


lm = leds.LEDManager(pins)

threads = {}
threads['dbm'] = db.DBManager(killEvent, len(threads), screen, wait=600) # DB commit every 10 minutes
threads['ssm'] = sensors.SensorsManager(killEvent, len(threads), pins, lm, threads['dbm'], screen, wait=1800) # Updated readings every 30 minutes for sensors not on callback
threads['wm'] = weather.WeatherManager(killEvent, len(threads), threads['dbm'], screen, wait=1800) # Update every half hour

threads['dbm'].start()
threads['ssm'].start()
threads['wm'].start()

try:
	while True:
		if screen.scr.getch() == ord('q'):
			raise KeyboardInterrupt
except KeyboardInterrupt:
	killEvent.set()
	for t in threads.keys(): 
		threads[t].join()

	screen.updateStatus("Exiting...", 2)
	
	screen.close()
	GPIO.cleanup()
	exit()

