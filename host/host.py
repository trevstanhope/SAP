"""
Host

TODO:
- break into classes
"""

import json
import cv2
import sys
import os
import time
from datetime import datetime

# Constants
try:
    CONFIG = sys.argv[1]
except Exception as err:
    CONFIG = 'settings.json'

## Super Class for Host
import json
class Host:

    def __init__(self, config):
    
        ### Configs
        print('[Loading Config File]')
        with open(config) as config_file:
            settings = json.loads(config_file.read())
            print(json.dumps(settings, sort_keys=True, indent=4))
            for key in settings:
                try:
                    getattr(self, key)
                except AttributeError as error:
                    setattr(self, key, settings[key])         
        ### ZMQ
        try:
            self.server = Server(self)
        except Exception as error:
            print('\tERROR: %s' % str(error))
            
        ### Mongo 
        try:
            self.database = Database(self)
        except Exception as error:
            print('\tERROR: %s' % str(error))
            
        ### State Machine
        try:
            self.state_machine = StateMachine(self)
        except Exception as error:
            print('\tERROR: %s' % str(error))
        
        ### Display
        try:
            self.display = Display(self)
        except Exception as error:
            print('\tERROR: %s' % str(error))
    
    ## Run
    def run(self, object):
        print('[Running] %s' % datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
        self.running = True
        while self.running: 
            request = self.server.receive_request()
            response = self.state_machine.handle_request(request)
            self.server.send_response(response) #!TODO
            self.display.update_gui()
            trees = self.state_machine.predict_trees()
            robots = self.state_machine.predict_robots()
            path = self.state_machine.path
            self.display.show_board(trees, robots, path)
    
    ## Stop 
    def stop(self, object):
        print('[Stopping] %s' % datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
        self.running = False
        
# ZMQ Server Object
import zmq
import json
class Server(object):

    def __init__(self, object):
        try:
            print('[Initializing Server] %s' % datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
            self.context = zmq.Context()
            self.socket = self.context.socket(zmq.REP)
            self.socket.bind(object.ZMQ_SERVER)
            print('\tOKAY')
        except Exception as error:
            print('\tERROR: %s' % str(error))
            
    ## Get Request() --> DICT
    def receive_request(self):
        print('[Receiving Request] %s' % datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
        try:
            request = json.loads(self.socket.recv())
            #print json.dumps(request, sort_keys=True, indent=4)
            return request
        except Exception as error:
            print('\tERROR: %s' % str(error))
            return None
    
    ## Send Response(DICT) --> DICT
    def send_response(self, response):
        print('[Sending Response] %s' % datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
        try:
            dump = json.dumps(response, sort_keys=True, indent=4)
            result = self.socket.send(dump)
            return result
        except Exception as error:
            print('\tERROR: %s' % str(error))
            return None
    
    ## Close ZMQ
    def close(self):
        print('[Closing ZMQ]  %s' % datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
        try:
            self.socket.close()
        except Exception as error:
            print('\tERROR: %s' % str(error))

# Mongo Database
from pymongo import MongoClient
class Database(object):

    ## Initialize Databasse
    def __init__(self, object):
        print('[Initializing Database] %s' % datetime.strftime(datetime.now(), object.TIME_FORMAT))
        try:
            client = MongoClient()
            database = client[object.MONGO_DB]
            trial_name = datetime.strftime(datetime.now(), object.TIME_FORMAT)
            self.collection = database[trial_name]
            print('\tOKAY')
        except Exception as error:
            print('\tERROR: %s' % str(error))
            
    ## Store to Mongo(DICT) --> _ID
    def store(self, request, response):
        print('[Storing to Database]  %s' % datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
        try:
            doc = {
                'request': request,
                'response':response
            }
            doc_id = self.collection.insert(doc)
            print doc_id
            return doc_id
        except Exception as error:
            print('\tERROR: %s' % str(error))
        
# Display
import pygtk
pygtk.require('2.0')
import gtk
import matplotlib.pyplot as mpl
class Display(object):

    ## Initialize Display
    def __init__(self, object):
        print('[Initializing Display] %s' % datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
        try:
            self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
            self.window.set_size_request(480, 120)
            self.window.connect("delete_event", self.close)
            self.window.set_border_width(10)
            self.window.show()
            self.hbox = gtk.HBox(False, 0)
            self.hbox.show()
            self.window.add(self.hbox)
            ### Run Button
            self.button_run = gtk.Button("Run")
            self.button_run.connect("clicked", object.run)
            self.hbox.pack_start(self.button_run, True, True, 0)
            self.button_run.show()
            ### Stop Button
            self.button_stop = gtk.Button("Stop")
            self.button_stop.connect("clicked", object.stop)
            self.hbox.pack_start(self.button_stop, True, True, 0)
            self.button_stop.show()
            print('\tOKAY')
        except Exception as error:
            print('\tERROR: %s' % str(error))
    
    ## Update GUI
    def update_gui(self):
        while gtk.events_pending():
            gtk.main_iteration_do(False)
               
    ## Close GUI
    def close(self, widget, window):
        print('[Closing Application] %s' % datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
        try:
            gtk.main_quit()
        except Exception as error:
            print('\tERROR: %s' % str(error))
    
    ## Show Board State
    def show_board(self, tree_locations, robot_locations, path):
        print('[Displaying Board] %s' % datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
        try:
            board = cv2.imread('board.jpg')
            ### Draw Tree locations
            (w,h,d) = board.shape
            for (x,y) in tree_locations:
                cv2.circle(board,(x * w / 96, y * h / 96),5,(0,0,255),5)
            ### Draw Spooler location
            (x,y,t) = robot_locations['spooler']
            cv2.circle(board,(x * w / 96, y * h / 96),10,(0,255,0),10)
            ### Draw Left Scout location
            (x,y,t) = robot_locations['scout_left']
            cv2.circle(board,(x * w / 96, y * h / 96),10,(255,0,0),10)
            ### Draw Right Scout location
            (x,y,t) = robot_locations['scout_right']
            cv2.circle(board,(x * w / 96, y * h / 96),10,(255,0,0),10)
            ### Draw Path
            for i in range(len(path) - 1):
                (x1, y1) = path[i]
                pt1 = (x1 * w / 96, y1 * h / 96)
                (x2, y2) = path[i+1]
                pt2 = (x2 * w / 96, y2 * h / 96)
                cv2.line(board, pt1, pt2, (128,128,128), thickness=4, lineType=8, shift=0)
            cv2.imshow('BOARD', board)
            if cv2.waitKey(5) == 27:
                pass
        except Exception as error:
            print('\tERROR: %s' % str(error))
            
# StateMachine
import numpy
import itertools as it
import math
class StateMachine(object):

    def __init__(self, object):
        print('[Initializing State Machine] %s' % datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
        try:
            self.map = numpy.zeros([object.X_SIZE, object.Y_SIZE])
            self.NUM_TREES = object.NUM_TREES
            self.detected_trees = []
            self.path = []
            self.snapshots = {}
            self.tree_positions = [
                (16, 32),
                (16, 48),
                (16, 64),
                (16, 80),
                (32, 32),
                (32, 48),
                (32, 64),
                (32, 80),
                (48, 32),
                (48, 48),
                (48, 64),
                (48, 80),
                (64, 32),
                (64, 48),
                (64, 64),
                (64, 80),
                (80, 32),
                (80, 48),
                (80, 64),
                (80, 80),
            ]
            self.robots = {
                'spooler' : (48, 0, numpy.pi/2.0),
                'scout_left' : (8, 0, numpy.pi/2.0),
                'scout_right' : (88, 0, numpy.pi/2.0)
            }
            print('\tOKAY')
        except Exception as error:
            print('\tERROR: %s' % str(error))
    
    ## Handle new request    
    def handle_request(self, request):
        print('[Handling Request] %s' % datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
        robot_id = request['id']
        if robot_id == 'scout_left':
            response = self.command_scout_left(request)
        elif robot_id == 'scout_right':
            response = self.command_scout_right(request)
        elif robot_id == 'spooler':
            response = self.command_spooler(request)
        return response
    
    ##!TODO Handle Spooler
    def command_spooler(self, request):
        print('[Handling Spooler Request] %s' % datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
        try:
            snapshot = request['snapshot']
            position = self.robots[request['id']]
            self.detected_trees = self.predict_trees()
            if len(self.detected_trees) < self.NUM_TREES:
                print('\tWARNING: Not enough trees detected')
                self.update_map(snapshot, position) 
            elif len(self.path) < self.NUM_TREES:
                print('\tWARNING: Ready to calculate path')
                self.path = self.find_path(self.detected_trees)
            else:
                print('\tWARNING: Running Path')
                #!TODO decide movement actions for spooler 
        except Exception as error:
            print('\tERROR: %s' % str(error))
        response = request
        return response
    
    ##!TODO Handle Scout (Left)
    def command_scout_left(self, request):
        print('[Handling Scout Request] %s' % datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
        try:
            print('\tOKAY')
            return request #!TODO decide movement actions for scout left 
        except Exception as error:
            print('\tERROR: %s' % str(error))
        
    ##!TODO Handle Scout (Right)
    def command_scout_right(self, request):
        print('[Handling Scout Request] %s' % datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
        try:
            print('\tOKAY') 
            return request #!TODO decide movement actions for scout right 
        except Exception as error:
            print('\tERROR: %s' % str(error))
            
    ## Update Map   
    def update_map(self, snapshot, position):
        print('[Updating Map] %s' % datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
#        try:
#            position_as_string = str(list(position))
#            previous = self.snapshots[position_as_string]
#            print('\tWARNING: Snapshot already taken at this position!')
#            return None # do not add redundant snapshots to tree map
#        except Exception as error:
#            print('\tERROR: %s' % str(error))
#            self.snapshots[position_as_string] = snapshot
        (x, y, t) = position
        error = 0.1
        DIST_MIN = 10
        DIST_MAX = 106
        X_MAX = 96
        Y_MAX = 96
        for offset in snapshot:
            for orientation in [-error, 0, error]: # more then 3
                x1 = x + numpy.cos(t + offset + error) * DIST_MIN
                y1 = y + numpy.sin(t + offset + error) * DIST_MIN
                for dist in range(DIST_MIN, DIST_MAX):
                    x2 = x1 + numpy.cos(t + offset + error) * dist
                    y2 = y1 + numpy.sin(t + offset + error) * dist
                    if (x2 >= X_MAX - 2) or (y2 >= Y_MAX - 2):
                        break
                    elif (x2 <= 0) or (y2 <= 0):
                        break
                    else:
                        continue
            x_vals = numpy.linspace(x1, x2, dist).astype(int)
            y_vals = numpy.linspace(y1, y2, dist).astype(int)
            self.map[x_vals, y_vals] += 1 ## add to field
    
    ## Predict Tree Locations        
    def predict_trees(self):
        print('[Predicting Tree Locations] %s' % datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
        mask = self.map[numpy.nonzero(self.map)]
        (x,y) = numpy.nonzero((self.map > numpy.mean(mask)))
        tree_locations = []
        for i in range(len(x)):
            for (a,b) in self.tree_positions:
                if x[i] == a and y[i] == b:
                    tree_locations.append( (x[i], y[i]) )
        print('\tTrees: %s' % str(tree_locations))
        return tree_locations
    
    ## Predict Robot Locations
    def predict_robots(self):
        print('[Predicting Robot Locations] %s' % datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
        return self.robots
    
    ## Calculate Minimum Hamiltonian Path
    def find_path(self, trees):
        print('[Finding Shortest Path] %s' % datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
        points = trees.append((48,1)) # add start
        paths = [ p for p in it.permutations(trees) ]
        path_distances = [ sum(map(lambda x: self.dist(x[0],x[1]),zip(p[:-1],p[1:]))) for p in paths ]
        min_index = numpy.argmin(path_distances)
        shortest_path = paths[min_index]
        print('\tPath: %s' % str(shortest_path[::-1]))
        return shortest_path[::-1]
    
    ## Distance Function
    def dist(self, x, y):
        return math.hypot(y[0]-x[0],y[1]-x[1])
    
    ## Close State Machine
    def close(self):
        print('[Closing State Machine] %s' % datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
        
def main():
    gtk.main()
    
if __name__ == '__main__':
    host = Host(CONFIG)
    main()
