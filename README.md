# SmartHome_MotionSensor_RPi
This project combines a Raspberry Pi with a motion sensor to control a smart home device with IFTTT.

Many thanks to Caroline Dunn for starting this project! Her original tutorial can be found at carolinedunn/SmartHome_MotionSensor_RPi. I've made many modifications to the code and tutorial to make this run more reliably and so that you can update your motion sensor with future versions of my code without any issues.

Materials:
- Raspberry Pi Zero W with headers (or without headers by soldering) - https://amzn.to/2NncxP4
  - or Raspberry Pi 3B, 3B+ (3A, or 4) - https://amzn.to/2O9SxiO
- MicroSD card - https://amzn.to/2Nq5AN9
- Motion Sensor - https://www.adafruit.com/product/189
- A smart device like a TP-Link Smart Plug (https://amzn.to/30dpAty). I used Philips WiZ Lights from Home Depot because I love the built-in automatic circadian rhythm and brightness for my bathroom. This made a perfect use-case for motion sensing since those lights only need to be on if someone enters the bathroom.
- Optional peripherals: Mouse, Keyboard, & Monitor

Assumptions:
- Working knowledge of how to setup a fresh Raspberry Pi with Raspberry Pi OS (or preferably the Lite version on a Pi Zero W).
- A rough understanding of how the Raspberry Pi GPIO works
- How to boot up a Raspberry Pi.
- A grasp of some basic Linux commands
- Previously setup a smart plug that is currently active and connected to your home or office Wifi network.

# Step 1: Setup Raspbian OS
I assume this isn't your first experience with a Raspberry Pi, so won't go into detail here. There are many videos and tutorials for setting it up though!
- Download and flash Raspberry Pi OS on a micro SD card
- Enable SSH and add your WiFi by adding files to the SD card, as described at https://learn.adafruit.com/raspberry-pi-zero-creation/install-os-on-to-sd-card
- Place the SD card in the Raspberry Pi
- Use another computer to log in to it through SSH (preferred method) or, optionally, attach a mouse, keyboard, and monitor to your Raspberry Pi
- Boot up your Raspberry Pi

To let Python interact with the GPIO pins, we need to install a library:
- Open a terminal on the Pi (either directly or through SSH) and enter:
```pip3 --version```
- If it shows you a version number, great! You can skip the next step - but it probably won't since Raspberry Pi OS doesn't usually include it for Python 3.
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

![WiringDiagram](https://github.com/elammertsma/SmartHome_MotionSensor_RPi/blob/master/Wiring%20Diagram-MotionSensor%20to%20RPi.jpg)

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

- First, we'll make sure our Pi is up to date:
```
sudo apt-get update
sudo apt-get upgrade
```
- Next we'll download this motion detector project from Github:
```
git clone https://github.com/elammertsma/SmartHome_MotionSensor_RPi.git
```
- Then we need to add the IFTTT key we recieved above to a new file we'll create, called keys.txt. We need to create this in the folder where the script is:
```
cd SmartHome_MotionSensor_RPi/ifttt/
touch keys.txt
```
- Then we open the keys.txt file to add our key:
```
nano keys.txt
```
- Now add the following text to the file:
```
ifttt_key=
```
- Go back to your IFTTT webpage and copy the key
- Paste the IFTTT webhook key at the end of the line. Note that in Nano, you need to press Ctrl+U to paste! When you're done it should look like this:
```
ifttt_key=nTxxxxxxxxxxxxxxJSA
```
- Press Ctrl-X
- Press Y to save
- Press Enter to confirm keeping the filename unchanged
- Optionally, you can change some settings in the code in iftttpir.py:
```
nano iftttpir.py
```
- Take a look around and see what you can understand. While you're in the file, note the timer variable on line 48. It is set in seconds (for example 240 seconds for five minutes), meaning that the motion_stopped IFTTT funtion will run if no motion is detected 5 minutes after the last motion was detected. Feel free to make this shorter or longer.
```timer = 240```

Now let's try running the code!
```python3 iftttpir.py```
Or, if you navigated to a different folder:
```python3 ~/SmartHome_MotionSensor_RPi/ifttt/iftttpir.py```

Now move your hand in front of your motion sensor and see if it works. If it doesn't work, retrace your steps.


# Step 5: Run on Boot

If you're going to use this as a motion sensor (semi-)permenantly, this is necessary! In that case, we want our script to run anytime the Pi reboots (for example if it gets unplugged or the power goes out).

- Open a Terminal
- We're going to set the boot script to include our python script. We do this in /etc/rc.local, which runs at every boot. Another option is to do this in /home/pi/.bashrc, but then it would only run when you log in to a terminal as 'pi' instead, which isn't what we want. Since we want this script to run unattended as a motion sensor, we want it to run in the background every time the pi boots up, even if no one logs in.
- Enter:
```sudo nano /etc/rc.local```
- Arrow down to the bottom of the file.
- On a new line before 'Exit 0' add following in rc.local
```sudo python3 /home/pi/SmartHome_MotionSensor_RPi/ifttt/iftttpir.py &```
- The end of the file should now look like this:
```
sudo python3 /home/pi/SmartHome_MotionSensor_RPi/ifttt/iftttpir.py &
exit 0
```
- Don't forget the "&" at the end of the line! This lets the script complete without waiting for the Python script to complete. If you left it out, rc.local would never complete and the boot sequence would never finish because our Python script runs forever!
- Press Ctrl-X to exit
- Press Y to Save
- Press Enter to confirm
- Reboot your Raspberry Pi
```
sudo reboot
```

Voila! You now have a motion sensor that automatically turns on your lights and turns them off again when no one is around!


# Step 6: Occassionally get the latest updates

Sometimes, I update this project so it runs even better. I use this project in my own home, so whenever I encounter a problem I fix it and make sure to update the code. If you ever run into an issue, it's always a good idea to see if the code has been updated.

To update your code:
- Log in to your Pi
- Always make sure your Pi is up to date:
```
sudo apt-get update
sudo apt-get upgrade
```
- Navigate to the project folder:
```
cd ~/SmartHome_MotionSensor_RPi/ifttt/
```
- Tell git to retrieve the latest updates and reboot:
```
git pull
sudo reboot
```

If you still have issues, just open an issue in this project or send me a message and I'll take a look!

