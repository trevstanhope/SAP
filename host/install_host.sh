#!/bin/sh

# Update Dependencies
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install build-essential python-dev -y
sudo apt-get install python-pip python-opencv python-numpy python-serial python-zmq -y
sudo apt-get install git-core -y
sudo apt-get install arduino arduino-mk -y
sudo apt-get install mongodb -y
sudo apt-get install python-matplotlib
sudo apt-get install python-tkinter
sudo pip install pymongo
