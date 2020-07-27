# SmartHome_MotionSensor_RPi
This project combines a Raspberry Pi with a motion sensor to control a smart home device with IFTTT

Materials:
- Raspberry Pi Zero W with headers (or without headers by soldering) - https://amzn.to/2NncxP4
  - or Raspberry Pi 3B, 3B+ (3A, or 4) - https://amzn.to/2O9SxiO
- MicroSD card - https://amzn.to/2Nq5AN9
- Motion Sensor - https://www.adafruit.com/product/189
- A smart device like a TP-Link Smart Plug (https://amzn.to/30dpAty) or I used a Philips Wiz Light 
- Peripherals: Mouse, Keyboard, & Monitor

Assumptions:
- Working knowledge of how to setup a fresh Raspberry Pi with Raspberry Pi OS (or optionally the Lite version on a Pi Zero W).
- A rough understanding of how the Raspberry Pi GPIO works
- How to boot up a Raspberry Pi.
- A grasp of some basic Linux commands
- Previously setup a smart plug that is currently active and connected to your home or office Wifi network.

# Step 1: Setup Raspbian OS
I assume this isn't your first experience with a Raspberry Pi, so won't go into detail here. There are many videos and tutorials for setting it up though!
- Download and flash Raspberry Pi OS on a micro SD card
- Enable SSH and add your WiFi by adding files to the SD card, as described at https://learn.adafruit.com/raspberry-pi-zero-creation/install-os-on-to-sd-card
- Place the SD card in the Raspberry Pi
- Either attach a mouse, keyboard, and monitor to your Raspberry Pi, or use another computer to log in to it through SSH with nothing attached
- Boot up your Raspberry Pi

To let Python interact with the GPIO pins, we need to install a library:
- Open a terminal on the Pi (either directly or through SSH) and enter:
```pip3 --version```
- If it shows you a version number, great! You can skip the next step - but it probably won't since Raspberry Pi OS doesn't usually include it.
- Otherwise, enter:
```
sudo apt-get install python3-pip
pip3 --version
```
- Now you can install the required python package with pip, by entering:
```pip3 install RPi.GPIO```


# Step 2: Hardware Assembly
- Unplug your Raspberry Pi
- Connect your motion sensor to your Raspberry Pi. If you are using a Raspberry Pi Zero, you may need to solder the wires or header pins.
  - Connect the Ground pin of your motion sensor to GPIO pin 6 of your Raspberry Pi
  - Connect the OUT pin of your motion sensor to GPIO pin 11 of your Raspberry Pi
  - Connect the VCC pin of your motion sensor to GPIO pin 2 of your Raspberry Pi
- Power on your Pi.

![WiringDiagram](https://github.com/carolinedunn/SmartHome_MotionSensor_RPi/blob/master/Wiring%20Diagram-MotionSensor%20to%20RPi.jpg)

# Step 3: Setup IFTTT

In this step, you'll setup your IFTTT Webhook
- Go to: https://ifttt.com/ (If you don't already have an account with IFTTT, create one. It is free and does not require a credit card.)
- Login to IFTTT
- Click the "Create" button in the top right
- Click "This"
- Search for "webhook" and select "Webhooks"
- Click "Receive a web request"
- Enter "motion_detected" and click the "Create trigger" button
- Click "That"
- Search for your smart plug vendor or smart plug app and click the appropriate icon.
- Connect your smart plug with IFTTT. Enter your login and password for your smart home plug and authorize the connection with IFTTT.
- Click on your desired action to turn the light on (or do what you'd like).
- Configure (if necessary) and click "Create Action"
- Click the IFTTT logo in the top left and search for "webhook" in sthe "Search Filters" field.
- Click Webhook
- Click "Documentation" (and leave that page open for the next test steps and the Software Installation step.)

Now test to make sure the IFTTT action works:
- Open a Terminal on your Pi or another computer
- Enter (replacing your access code from the documentation page):
```curl -X POST https://maker.ifttt.com/trigger/motion_detected/with/key/{youraccesscode}```
- Does your light turn on?
- Great!

Now go back a to the beginning of the IFTTT home page and create another action for motion_stopped, for example chosing to turn off the light.
- Test it with:
```curl -X POST https://maker.ifttt.com/trigger/motion_stopped/with/key/{youraccesscode}```

# Step 4: Software Installation

Open a Terminal and run the following commands

```
sudo apt-get update
sudo apt-get upgrade
mkdir ifttt
cd ifttt
wget https://raw.githubusercontent.com/elammertsma/SmartHome_MotionSensor_RPi/master/ifttt/iftttpir.py
sudo nano iftttpir.py
```
- Go back to your IFTTT webpage and copy the key
- Paste IFTTT key into lines 62 and 71. For example:
```
r = requests.post('https://maker.ifttt.com/trigger/motion_detected/with/key/KXXXXXXXXXXXXXXA6pE', params={"value1":"none","value2":"none","value3":"none"})
r = requests.post('https://maker.ifttt.com/trigger/motion_stopped/with/key/KXXXXXXXXXXXXXXA6pE', params={'value1':'none','value2':'none','value3':'none'})
```
- While you're in the file, note the timer variable on line 29. It is set in seconds (for example 300 seconds for five minutes), meaning that the motion_stopped IFTTT funtion will run if no motion is detected for that many seconds after the last motion was detected. Feel free to make this shorter or longer.
```timer = 300```
- Ctrl-X
- Y to save
- press Enter to confirm keeping the filename unchanged

Now let's try running the code!
```sudo python3 iftttpir.py```

Now move your hand in front of your motion sensor and see if it works. If it doesn't work, retrace your steps.


# Step 5: Run on Boot

This step is optional if you'd like for this python script to run at boot. If you're going to use this as a motion sensor (semi-)permenantly, you should definitely do this!

- Open a Terminal
- We're going to set the boot script to include our python script. We do this in /etc/rc.local, which runs at every boot. If we did this in /home/pi/.bashrc, it would run every time you log in to a terminal as 'pi' instead, which isn't what we want. Since we want this script to run unattended as a motion sensor, we want it to run every time the pi boots up, even if no one logs in.
- Enter:
```sudo nano /etc/rc.local```
- Arrow down to the bottom of the file.
- On a new line before 'Exit 0' add following in rc.local
```sudo python3 /home/pi/ifttt/iftttpir.py &```
- The end of the file should now look like this:
```
sudo python3 /home/pi/iftttpir.py &
exit 0
```
- Don't forget the & at the end of the line! This lets the script complete without waiting for the Python script to complete. If you left it out, rc.local would never complete because our Python script runs forever!
- Ctrl-X to exit
- 'y' to Save
- Press enter to confirm.
- Reboot your Raspberry Pi.

Voila! You now have a motion sensor that turns on your lights and turns them off again when no one is around (unless they stand very still).



  
