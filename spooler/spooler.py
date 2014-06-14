"""
Spooler

TODO
- dedicated config?
"""

import sys
import random

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
            
    def determine_request(self, snapshot):
        index = random.randint(0,1) 
        classes = ['action', 'status']
        request = {
            'type':'request',
            'class':classes[index],
            'id':'spooler'
        }
        return request
           
    ##  The run loop for the robot
    def run(self):
        while True:
            try:
                snapshot = self.vision.find_trees()
                request = self.determine_request(snapshot)
                result = self.client.send_request(request)
                response = self.client.receive_response()
                #error = self.controller.execute(response)
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
    def send_request(self, request):
        print('[Sending Request]')
        try:
            dump = json.dumps(request)
            result = self.socket.send(dump)
            return result
        except Exception as error:
            print('--> ERROR: ' + str(error))
            
    ## Receive response from aggregator
    def receive_response(self):
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
            self.camera = cv2.VideoCapture(self.CV2_CAM_INDEX)
        except Exception as error:
            print('--> ERROR: ' + str(error))
    def find_trees(self):
        return None

# Controller
import serial
class Controller(object):
    def __init__(self, object):
        print('[Initializing Controller]')
        try:
            self.connection = serial.Serial(object.ARDUINO_DEV, object.ARDUINO_BAUD)
        except Exception as error:
            print('--> ERROR: ' + str(error))
    def execute(self):
        return None
            
if __name__ == '__main__':
    robot = Spooler(CONFIG)
    robot.run()
