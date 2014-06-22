"""
Spooler

TODO
- dedicated config?
"""

## Get Config File
try:
    CONFIG = sys.argv[1]
except Exception as err:
    CONFIG = 'settings.json'

## Main Class for the Spooler Robot
import sys
import json
import time
class Spooler:
    
    # Initialize
    def __init__(self, config):
    
        ### Load Config
        print('[Loading Config File]')
        with open(config) as config_file:
            settings = json.loads(config_file.read())
            print(json.dumps(settings, sort_keys=True, indent=4))
            for key in settings:
                try:
                    getattr(self, key)
                except AttributeError as error:
                    setattr(self, key, settings[key])
        
        ### Initializing ZMQ Module           
        try:
            self.client = Client(self)
        except Exception as error:
            print('\tERROR: %s' % str(error))  
            
        ### Initialize Vision Module
        try:
            self.vision = Vision(self)
        except Exception as error:
            print('\tERROR: %s' % str(error))
            
        ### Initialize Controller Module
        try:
            self.controller = Controller(self)
        except Exception as error:
            print('\tERROR: %s' % str(error))
           
    ##  The run loop for the robot
    def run(self):
        while True:
            try:
                snapshot = self.vision.find_trees(self)
                result = self.client.send_request(self, snapshot)
                response = self.client.receive_response(self)
                error = self.controller.execute(self, response)
            except KeyboardInterrupt:
                self.client.close()
                self.vision.close()
                self.controller.close()
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
            print('\tOKAY')
        except Exception as error:
            print('\tERROR: %s' % str(error))
            
    ## Send sample to aggregator
    def send_request(self, object, snapshot):
        print('[Sending Request]')
        try:
            request = {
		'time': time.time(),
                'type':'request',
                'id':'spooler',
                'snapshot':snapshot,
            }
            print(json.dumps(request, sort_keys=True, indent=4))
            dump = json.dumps(request)
            result = self.socket.send(dump)
            return result
        except Exception as error:
            print('\tERROR: %s' % str(error))
            
    ## Receive response from aggregator
    def receive_response(self, object):
        print('[Receiving Response]')
        try:
            socks = dict(self.poller.poll(object.ZMQ_TIMEOUT))
            if socks:
                if socks.get(self.socket) == zmq.POLLIN:
                    dump = self.socket.recv(zmq.NOBLOCK)
                    response = json.loads(dump)
                    print(json.dumps(response, sort_keys=True, indent=4))
                    return response
                else:
                    print('\tERROR: No poll available')
            else:
                print('\tERROR: No socket available')
        except Exception as error:
            print('\tERROR: %s' % str(error))
    
    ## Close
    def close(self):
        print('[Closing ZMQ Connection]')
        try:
            self.socket.close()
        except Exception as error:
            print('\tERROR: %s' % str(error))

# Vision
import cv2
import cv
import numpy
class Vision(object):

    ## Initialize Capture Interface 
    def __init__(self, object):
        print('[Initializing Camera]')
        try:
            self.camera = cv2.VideoCapture(object.CV2_CAM_INDEX)
            self.camera.set(cv.CV_CAP_PROP_FRAME_WIDTH, object.CAM_WIDTH)
            self.camera.set(cv.CV_CAP_PROP_FRAME_HEIGHT, object.CAM_HEIGHT)
            print('\tOKAY')
        except Exception as error:
            print('\tERROR: %s' % str(error))
            
    #!TODO Find Trees
    def find_trees(self, object):
        (s, bgr) = self.camera.read()
        if s:
            hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
            hue_min = object.HUE_MIN
            hue_max = object.HUE_MAX
            sat_min = object.SAT_MIN
            sat_max = object.SAT_MAX
            val_min = object.VAL_MIN
            val_max = object.VAL_MAX
            threshold_min = numpy.array([hue_min, sat_min, val_min], numpy.uint8)
            threshold_max = numpy.array([hue_max, sat_max, val_max], numpy.uint8)
            mask = cv2.inRange(hsv, threshold_min, threshold_max)
            column_sum = mask.sum(axis=0) # vertical summation
            threshold = numpy.percentile(column_sum, object.THRESHOLD_PERCENTILE)
            probable = numpy.nonzero(column_sum >= threshold) # returns 1 length tuble
            for i in probable[0]:
                mask[:,i] = 255
            snapshot = [((object.CAM_FOV / object.CAM_WIDTH) * (index - (object.CAM_WIDTH / 2.0))) for index in probable[0].tolist()] #!TODO
            return snapshot
    
    ## Close
    def close(self):
        print('[Releasing Camera Connection]')
        try:
            self.camera.release()
        except Exception as error:
            print('\tERROR: %s' % str(error))

# Controller
import serial
class Controller(object):
    
    ## Initialize Serial Port
    def __init__(self, object):
    
        print('[Initializing Controller]')
        try:
            self.arduino = serial.Serial(object.ARDUINO_DEV, object.ARDUINO_BAUD)
            print('\tOKAY')
        except Exception as error:
            print('\tERROR: %s' % str(error))
    
    #!TODO Execute Command on Arduino
    def execute(self, object, response):
        print('[Sending Command to Arduino]')
        try:
            command = response['command']
            self.arduino.write(command)
        except Exception as error:
            print('\tERROR: %s' % str(error))
    
    ## Close
    def close(self):
        print('[Closing Serial Connection]')
        try:
            self.arduino.close()
        except Exception as error:
            print('\tERROR: %s' % str(error))
            
if __name__ == '__main__':
    robot = Spooler(CONFIG)
    robot.run()
