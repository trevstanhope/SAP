"""
    ZMQ Controlled RPi-Arduino Robot
"""
import sys
import json
import time

## Get Config File
try:
    CONFIG = sys.argv[1]
except Exception as err:
    print('No Config File Specified! Exiting.')
    sys.exit()

## Main Class for the Spooler Robot
class Robot:
    
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
                hsv = self.vision.capture_image()
                trees_snapshot = self.vision.find_trees(hsv)
                spooler_snapshot = self.vision.find_spooler(hsv)
                result = self.client.send_request(trees_snapshot, spooler_snapshot)
                response = self.client.receive_response()
                error = self.controller.execute(response)
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
            self.ID = object.ID
            print('\tOKAY')
        except Exception as error:
            print('\tERROR: %s' % str(error))
            
    ## Send sample to aggregator
    def send_request(self, trees_snapshot, spooler_snapshot):
        print('[Sending Request]')
        try:
            request = {
		        'time' : time.time(),
                'type' : 'request',
                'id' : self.ID,
                'trees_snapshot' : trees_snapshot,
                'spooler_snapshot' : spooler_snapshot,
            }
            dump = json.dumps(request)
            result = self.socket.send(dump)
            print('\tOKAY')
            return result
        except Exception as error:
            print('\tERROR: %s' % str(error))
            
    ## Receive response from aggregator
    def receive_response(self):
        print('[Receiving Response]')
        try:
            socks = dict(self.poller.poll(self.ZMQ_TIMEOUT))
            if socks:
                if socks.get(self.socket) == zmq.POLLIN:
                    dump = self.socket.recv(zmq.NOBLOCK)
                    response = json.loads(dump)
                    print(json.dumps(response, sort_keys=True, indent=4))
                    print('\tOKAY')
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
            print('\tOKAY')
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
            self.CAM_WIDTH = object.CAM_WIDTH
            self.CAM_FOV = object.CAM_FOV
            self.THRESHOLD_PERCENTILE = object.THRESHOLD_PERCENTILE
            self.TREE_THRESHOLD_MIN = numpy.array([object.TREE_HUE_MIN, object.TREE_SAT_MIN, object.TREE_VAL_MIN], numpy.uint8)
            self.TREE_THRESHOLD_MAX = numpy.array([object.TREE_HUE_MAX, object.TREE_SAT_MAX, object.TREE_VAL_MAX], numpy.uint8)
            self.SPOOLER_THRESHOLD_MIN = numpy.array([object.SPOOLER_HUE_MIN, object.SPOOLER_SAT_MIN, object.SPOOLER_VAL_MIN], numpy.uint8)
            self.SPOOLER_THRESHOLD_MAX = numpy.array([object.SPOOLER_HUE_MAX, object.SPOOLER_SAT_MAX, object.SPOOLER_VAL_MAX], numpy.uint8)
            print('\tOKAY')
        except Exception as error:
            print('\tERROR: %s' % str(error))
    
    def capture_image(self):
        for i in range(30):
            (s, bgr) = self.camera.read()
        if s:
            hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
            cv2.imwrite('bgr.jpg', bgr)
            cv2.imwrite('hsv.jpg', hsv)
        return hsv
        
    #!TODO Find Trees
    def find_trees(self, hsv):
        print('[Finding Trees]')
        try:
            mask = cv2.inRange(hsv, self.TREE_THRESHOLD_MIN, self.TREE_THRESHOLD_MAX)
            column_sum = mask.sum(axis=0) # vertical summation
            threshold = numpy.percentile(column_sum, self.THRESHOLD_PERCENTILE)
            probable = numpy.nonzero(column_sum >= threshold) # returns 1 length tuble
            for i in probable[0]:
                mask[:,i] = 255
            snapshot = [((self.CAM_FOV / self.CAM_WIDTH) * (index - (self.CAM_WIDTH / 2.0))) for index in probable[0].tolist()]
            cv2.imwrite('mask_tree.jpg', mask)
            print('\tOKAY')
            print('\tOffsets Detected: %s' % str(len(snapshot)))
            return snapshot
        except Exception as error:
            print('\tERROR: %s' % str(error))
            
    #!TODO Find Spooler
    def find_spooler(self, hsv):
        print('[Finding Spooler]')
        try:
            mask = cv2.inRange(hsv, self.SPOOLER_THRESHOLD_MIN, self.SPOOLER_THRESHOLD_MAX)
            column_sum = mask.sum(axis=0) # vertical summation
            threshold = numpy.percentile(column_sum, self.THRESHOLD_PERCENTILE)
            probable = numpy.nonzero(column_sum >= threshold) # returns 1 length tuble
            for i in probable[0]:
                mask[:,i] = 255
            snapshot = [((self.CAM_FOV / self.CAM_WIDTH) * (index - (self.CAM_WIDTH / 2.0))) for index in probable[0].tolist()]
            cv2.imwrite('mask_spooler.jpg', mask)
            print('\tOKAY')
            print('\tOffsets Detected: %s' % str(len(snapshot)))
            return snapshot
        except Exception as error:
            print('\tERROR: %s' % str(error))
    
    ## Close
    def close(self):
        print('[Releasing Camera Connection]')
        try:
            self.camera.release()
            print('\tOKAY')
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
    def execute(self, response):
        print('[Sending Command to Arduino]')
        try:
            command = response['command']
            self.arduino.write(command)
            print('\tOKAY')
        except Exception as error:
            print('\tERROR: %s' % str(error))
    
    ## Close
    def close(self):
        print('[Closing Serial Connection]')
        try:
            self.arduino.close()
            print('\tOKAY')
        except Exception as error:
            print('\tERROR: %s' % str(error))
            
if __name__ == '__main__':
    robot = Robot(CONFIG)
    robot.run()
