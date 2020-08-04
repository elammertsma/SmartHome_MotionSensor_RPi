#! /usr/bin/python

# Imports
import RPi.GPIO as GPIO
import time
import requests
import logging

# ADD YOUR IFTTT WEBHOOK KEY HERE
ifttt_key='***REMOVED***'

# Set the log level
logging.basicConfig(level=logging.DEBUG)

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
            logging.error(f'Request {action} failed on try {i} at {time.ctime()}')
            logging.error(f'HTTP error occurred: {http_err}')
        except Timeout as time_err:
            logging.error(f'Request {action} timed out on try {i} at {time.ctime()}')
            logging.error(f'Time out occurred: {time_err}')
        except Exception as err:
            logging.error(f'Request {action} failed on try {i} at {time.ctime()}')
            logging.error(f'Other error occurred: {err}')
        if r:
            logging.info(f'Request {action} success on try {i}! {time.ctime()}')
            logging.info(f'Response: {r.text}')
            break
        time.sleep(1)

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

    # Loop until users quits with CTRL-C
    while True:

        # Read PIR state
        current_state = GPIO.input(pin_pir)

        if current_state == 1:
            time_trigger = time.time()

        time_elapsed = time.time() - time_trigger

        # If the PIR is triggered
        if current_state == 1 and previous_state == 0:

            logging.info(f'New motion detected at {time.ctime()}')

            # Fire the motion event when the motion started (e.g. turn on the lights)
            # Your IFTTT URL with event name, key and json parameters (values)
            reqaction('motion_detected', 3)

            # Record new previous state
            previous_state = 1

        # If the PIR has returned to ready state and the timer ran out
        elif current_state == 0 and previous_state == 1 and time_elapsed > timer:

            # Fire an event when the motion stopped and the timer ran out (e.g. turn off the lights)
            reqaction('motion_stopped', 3)

            logging.info('Timer of {timer} seconds expired at {time.ctime()} with no motion detected.\n    Ready!')

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
