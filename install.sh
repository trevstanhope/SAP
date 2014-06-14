#!/bin/sh

# Update Dependencies
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install build-essential -y
sudo apt-get install python python-imaging python-opencv python-numpy python-serial python-zmq -y
sudo apt-get install git-core -y
sudo apt-get install arduino arduino-mk -y

# Configure Arduino
sudo cp configs/avrdude /usr/bin/avrdude
sudo cp configs/avrdude /usr/share/arduino/hardware/tools
sudo chown root /usr/bin/avrdude /usr/share/arduino/hardware/tools/avrdude
sudo chgrp root /usr/bin/avrdude /usr/share/arduino/hardware/tools/avrdude
sudo chmod a+s /usr/bin/avrdude /usr/share/arduino/hardware/tools/avrdude
sudo cp configs/avrdude.conf  /usr/share/arduino/hardware/tools
sudo cp configs/boards.txt  /usr/share/arduino/hardware/arduino
sudo cp configs/cmdline.txt /boot
sudo cp configs/inittab /etc
sudo cp configs/80-alamode.rules /etc/udev/rules.d
sudo cp -r libs/* /usr/share/arduino/libraries

