"""
Spooler
"""

import sys

try:
    CONFIG = sys.argv[1]
except Exception as err:
    CONFIG = 'settings.json'

class Spooler:
    def __init__(self, config):
        print('[Loading Config File]')
        with open(config) as config_file:
            settings = json.loads(config_file.read())
            print('--> settings : ' + json.dumps(settings, sort_keys=True, indent=4))
            for key in settings:
                try:
                    getattr(self, key)
                except AttributeError as error:
                    setattr(self, key, settings[key])
                    
        print('[Initializing Asynch Client]')
        try:
            self.client = Client(self)
        except Exception as error:
            print('--> ERROR: ' + str(error))  
            
        print('[Initializing Vision]')
        try:
            self.vision = Vision(self)
        except Exception as error:
            print('--> ERROR: ' + str(error))
            
        print('[Initializing Controller]')
        try:
            self.controller = Controller(self)
        except Exception as error:
            print('--> ERROR: ' + str(error))
           
    ##  The run loop for the robot
    def run(self):
        while True:
            try:
                req = {'type':'test'}
                res = self.client.send(req)
                data = self.client.receive()
            except KeyboardInterrupt:
                self.client.close()
                break
    
# Asynch Client
import zmq
import json
class Client(object):
    def __init__(self, object):
        print('[Initializing ZMQ]')
        try:
            self.context = zmq.Context()
            self.socket = self.context.socket(zmq.REQ)
            self.socket.connect(object.ZMQ_SERVER)
            self.poller = zmq.Poller()
            self.poller.register(self.socket, zmq.POLLIN)
            self.ZMQ_TIMEOUT = object.ZMQ_TIMEOUT
        except Exception as error:
            print('--> ERROR: ' + str(error))
            
    ## Send sample to aggregator
    def send(self, request):
        print('[Sending Request]')
        try:
            dump = json.dumps(request)
            result = self.socket.send(dump)
            return result
        except Exception as error:
            print('--> ERROR: ' + str(error))
            
    ## Receive response from aggregator
    def receive(self):
        print('[Receiving Response]')
        try:
            socks = dict(self.poller.poll(self.ZMQ_TIMEOUT))
            if socks:
                if socks.get(self.socket) == zmq.POLLIN:
                    dump = self.socket.recv(zmq.NOBLOCK)
                    response = json.loads(dump)
                    return response
        except Exception as error:
            print('--> ERROR: ' + str(error))
    
    ## Close
    def close(self):
        try:
            self.socket.close()
        except Exception as error:
            print('--> ERROR: ' + str(error))

# Vision
import cv2
class Vision(object):
    def __init__(self, object):
        print('[Initializing Camera]')
        try:
            self.camera = VideoCapture(self.CV2_CAM_INDEX)
        except Exception as error:
            print('--> ERROR: ' + str(error))

# Controller
import serial
class Controller(object):
    def __init__(self, object):
        print('[Initializing Controller]')
        try:
            self.connection = serial.Serial(object.ARDUINO_DEV, object.ARDUINO_BAUD)
        except Exception as error:
            print('--> ERROR: ' + str(error))
            
if __name__ == '__main__':
    robot = Spooler(CONFIG)
    robot.run()
