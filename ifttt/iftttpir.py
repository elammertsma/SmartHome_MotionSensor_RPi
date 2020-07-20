#! /usr/bin/python

# Imports
import RPi.GPIO as GPIO
import time
import requests
import logging

# Set the log level
logging.basicConfig(level=logging.DEBUG)

# Set the GPIO naming convention
GPIO.setmode(GPIO.BCM)

# Turn off GPIO warnings
GPIO.setwarnings(False)

# Set a variable to hold the GPIO Pin identity
pinpir = 17

# Set GPIO pin as input
GPIO.setup(pinpir, GPIO.IN)

# Variables to hold the current and last states
currentstate = 0
previousstate = 0

try:
	print('Waiting for PIR to settle ...')
	
	# Loop until PIR output is 0
	while GPIO.input(pinpir) == 1:
	
		currentstate = 0

	print('    Ready!')
	# set timer for 5 minutes (300 seconds) until shutoff event fires
	timer = 300
	
	# set the last time motion was detected to epoch
	time_trigger = 0
	
	# Loop until users quits with CTRL-C
	while True:
	
		# Read PIR state
		currentstate = GPIO.input(pinpir)
		
		if currentstate = 1:
			time_trigger = time.time()
			
		time_elapsed = time.time() - time_trigger

		# If the PIR is triggered
		if currentstate == 1 and previousstate == 0:
		
			print('New motion detected!')
			
			# Fire the motion event when the motion started (e.g. turn on the lights)
			# Your IFTTT URL with event name, key and json parameters (values)
			r = requests.post('https://maker.ifttt.com/trigger/motion_detected/with/key/REPLACE_WITH_YOUR_IFTTT', params={'value1':'none','value2':'none','value3':'none'})
			
			# Record new previous state
			previousstate = 1
			
		# If the PIR has returned to ready state and the timer ran out
		elif currentstate == 0 and previousstate == 1 and time_elapsed > timer:
		
			# Fire an event when the motion stopped and the timer ran out (e.g. turn off the lights)
			r = requests.post('https://maker.ifttt.com/trigger/motion_stopped/with/key/REPLACE_WITH_YOUR_IFTTT', params={'value1':'none','value2':'none','value3':'none'})

			print('Timer expired with no motion detected.\n    Ready!')

			# Record new previous state
			previousstate = 0
			
		elif currentstate = 1:
			logging.debug('More motion detected. Timer is set to ' + str(timer) + ' and there are ' + str(time_trigger - time_elapsed) + ' seconds left.')
			
		elif currentstate = 0:
			logging.debug('No motion detected.')
			

		# Wait for 100 milliseconds
		time.sleep(0.1)

except KeyboardInterrupt:
	print("    Quit")

	# Reset GPIO settings
	GPIO.cleanup()
