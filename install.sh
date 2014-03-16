#!/bin/sh
# Scout

# Update Dependencies
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install build-essential -y
sudo apt-get install python python-imaging python-opencv python-numpy python-serial -y
sudo apt-get install git-core -y
sudo apt-get install arduino arduino-mk -y

# Configure Network
sudo cp config/interfaces /etc/network/interfaces
sudo cp config/hosts /etc/hosts
