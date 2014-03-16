"""
Spooler
"""

import serial
import zmq
import sys
import json
import cv2

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
        
        print('[Initializing ZMQ]')
        try:
            self.context = zmq.Context()
            self.socket = self.context.socket(zmq.REQ)
            self.socket.connect(self.ZMQ_SERVER)
            self.poller = zmq.Poller()
            self.poller.register(self.socket, zmq.POLLIN)
        except Exception as error:
            print('--> ERROR: ' + str(error))

        print('[Initializing Camera]')
        try:
            self.camera = VideoCapture(self.CV2_CAM_INDEX)
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
            return None
            
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
                else:
                    return None
            else:
                return None
        except Exception as error:
            print('--> ERROR: ' + str(error))
            return None
           
    ##  The run loop for the robot
    def run(self):
        while True:
            try:
                req = {'type':'test'}
                res = self.send(req)
                data = self.receive()
            except KeyboardInterrupt:
                self.socket.close()
                break
            
if __name__ == '__main__':
    root = Spooler(CONFIG)
    root.run()
