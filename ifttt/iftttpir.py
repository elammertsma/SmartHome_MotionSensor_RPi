#! /usr/bin/python

# ADD YOUR IFTTT WEBHOOK KEY FIRST
#
# To do this, create a file named keys.txt
# Then add a line with the content:
#
# ifttt_key=XXXXXXXXXXXXXXXXXXX
#
# Replace XXXX... with your IFTTT webhook key.

# Imports
import RPi.GPIO as GPIO
import time
import requests
from requests.exceptions import HTTPError
from requests.exceptions import Timeout
import logging
import os

# Create a log file that has write access from all users.
# The default umask is 0o22 which turns off write permission of group and others
os.umask(0)
path_to_script = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(path_to_script, 'iftttpir.log')
# Create log file with write permissions for all users
with open(os.open(log_file, os.O_CREAT | os.O_WRONLY, 0o777), 'w') as lf:
  lf.write('Log file created')

# Load the IFTTT webhook key from our keys.txt file
keys_file = os.path.join(path_to_script, 'keys.txt')
with open(keys_file, mode='r') as keys:
    keys_list = keys.readlines()
    keys_dict = {key.split('=')[0].strip():key.split('=')[1].strip() for key in keys_list}
ifttt_key = keys_dict['ifttt_key']

# Set the log level and start logging so we can see what's happening
# 
# Filemode "w" (write) overwrites the log file every time the script runs.
# Change the mode to "a" (append) if you want to keep one long log file for all runs.
logging.basicConfig(filename=log_file, filemode='w', format='%(asctime)s: %(levelname)s: %(message)s', level=logging.INFO)
# Comment the above line and uncomment the below line if you want to see live logs while
# trying to solve a problem with your code.
#logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', level=logging.DEBUG)

# Set the GPIO naming convention
GPIO.setmode(GPIO.BCM)

# Turn off GPIO warnings
GPIO.setwarnings(False)

# Set a variable to hold the GPIO Pin identity
pin_pir = 17

# Set GPIO pin as input
GPIO.setup(pin_pir, GPIO.IN)

# Set the amount of seconds to wait for IFTTT to trigger the action
ifttt_timeout = 2.0

# set timer in seconds until shutoff event fires
timer = 240

def reqaction(action, rep):
    for i in range(rep):
        try:
            r = requests.post(f'https://maker.ifttt.com/trigger/{action}/with/key/{ifttt_key}', params = {'value1' : 'none', 'value2' : 'none', 'value3' : 'none'}, timeout = ifttt_timeout)
            r.raise_for_status()
        except HTTPError as http_err:
            logging.error(f'Request {action} failed on try {i+1}')
            logging.error(f'HTTP error occurred: {http_err}')
        except Timeout as time_err:
            logging.error(f'Request {action} timed out on try {i+1}')
            logging.error(f'Time out occurred: {time_err}')
        except Exception as err:
            logging.error(f'Request {action} failed on try {i+1}')
            logging.error(f'Other error occurred: {err}')
        else:
            logging.info(f'Request {action} success on try {i+1}!')
            logging.debug(f'Response: {r.text}')
            break
        pass

def main():
    logging.info('Waiting for PIR to settle ...')

    # Loop until PIR output is 0
    while GPIO.input(pin_pir) == 1:

        current_state = 0

    logging.info('    Ready!')

    # Variables to hold the current and last states
    current_state = 0
    previous_state = 0

    # set the last time motion was detected to epoch
    time_trigger = 0

    global timer

    # Loop until users quits with CTRL-C
    while True:

        # Read PIR state
        current_state = GPIO.input(pin_pir)

        if current_state == 1:
            time_trigger = time.time()

        time_elapsed = time.time() - time_trigger

        # If the PIR is triggered
        if current_state == 1 and previous_state == 0:

            logging.info(f'New motion detected')

            # Fire the motion event when the motion started (e.g. turn on the lights)
            # Your IFTTT URL with event name, key and json parameters (values)
            reqaction('motion_detected', 3)

            # Record new previous state
            previous_state = 1

        # If the PIR has returned to ready state and the timer ran out
        elif current_state == 0 and previous_state == 1 and time_elapsed > timer:

            # Fire an event when the motion stopped and the timer ran out (e.g. turn off the lights)
            reqaction('motion_stopped', 3)

            logging.info(f'Timer of {timer} seconds expired with no motion detected.\n    Ready!')

            # Record new previous state
            previous_state = 0

        elif current_state == 1:
            logging.debug(f'More motion detected. timer={str(timer)}, trigger={time.ctime(time_trigger)[-13:-5]}, elapsed={str(int(time_elapsed))}, remaining={str(int(timer - time_elapsed))}')

        elif current_state == 0:
            logging.debug(f'No motion detected.   timer={str(timer)}, trigger={time.ctime(time_trigger)[-13:-5]}, elapsed={str(int(time_elapsed))}, remaining={str(int(timer - time_elapsed))}')

        # Wait for 100 milliseconds
        time.sleep(0.5)

try:
    main()
except KeyboardInterrupt:
    print("    Quit")

    # Reset GPIO settings
    GPIO.cleanup()
