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
from matplotlib import pyplot as mpl

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
        print('[Starting Run] %s' % datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
        self.running = True
        while self.running: 
            request = self.server.receive_request()
            self.display.update_gui()
            response = self.state_machine.handle_request(request)
            self.display.update_gui()
            self.server.send_response(response) #!TODO
            self.display.update_gui()
            tree_map = self.state_machine.update_tree_map()
            self.display.update_gui()
            trees = self.state_machine.detected_trees
            self.display.update_gui()
            robots = self.state_machine.predict_robots()
            self.display.update_gui()
            path = self.state_machine.path
            true_path = self.state_machine.true_path
            self.display.show_board(trees, robots, path, true_path, tree_map)
            self.display.update_gui()
            self.database.store(request, response)
            self.display.update_gui()

    ## Stop 
    def stop(self, object):
        print('[Stopping Run] %s' % datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
        self.running = False
        
    ## Reset 
    def reset(self, object):
        print('[Resetting Run] %s' % datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
        self.state_machine = StateMachine(self)
    
    ## Reset 
    def shutdown(self, object):
        print('[Shutting Down] %s' % datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
        self.state_machine.close()
        self.server.close()
        
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
            
    ## Store to Mongo #!TODO
    def store(self, request, response):
        print('[Storing to Database]  %s' % datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
        try:
            doc = {
                'time' : datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"),
                'request' : request,
                'response': response
            }
            doc_id = self.collection.insert(doc)
            print('\tDoc ID: %s' % str(doc_id))
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
            ###
            self.X_SIZE = object.X_SIZE
            self.Y_SIZE = object.Y_SIZE
            ### Window
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
            ### Reset Button
            self.button_reset = gtk.Button("Reset")
            self.button_reset.connect("clicked", object.reset)
            self.hbox.pack_start(self.button_reset, True, True, 0)
            self.button_reset.show()
            ### Shutdown Button
            self.button_shutdown = gtk.Button("Shutdown")
            self.button_shutdown.connect("clicked", object.shutdown)
            self.hbox.pack_start(self.button_shutdown, True, True, 0)
            self.button_shutdown.show()
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
    def show_board(self, tree_locations, robot_locations, path, true_path, heat_map):
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
            ### Draw True Path
            for i in range(len(true_path) - 1):
                (x1, y1) = true_path[i]
                pt1 = (x1 * w / 96, y1 * h / 96)
                (x2, y2) = true_path[i+1]
                pt2 = (x2 * w / 96, y2 * h / 96)
                cv2.line(board, pt1, pt2, (0,128,255), thickness=4, lineType=8, shift=0)
            ### Draw Heat Map
            map_min = heat_map.min()
            map_max = heat_map.max()
            for i in range(self.X_SIZE):
                for j in range(self.Y_SIZE):
                    x = int(i * w / float(self.X_SIZE))
                    y = int(j * h / float(self.Y_SIZE))
                    if heat_map[j,i] > heat_map.mean():
                        board[x, y, :] = 0
            cv2.imshow('SAP', board)
            if cv2.waitKey(5) == 27:
                pass
        except Exception as error:
            print('\tERROR: %s' % str(error))
            
# StateMachine
import numpy
import cv2
import itertools as it
import math
#from sklearn.preprocessing import normalize
class StateMachine(object):
    
    ## Initialize StateMachine
    def __init__(self, object):
        print('[Initializing State Machine] %s' % datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
        try:
            ### Global Constants
            self.X_SIZE = object.X_SIZE
            self.Y_SIZE = object.Y_SIZE
            self.NUM_TREES = object.NUM_TREES
            self.PIVOT_DISTANCE = object.PIVOT_DISTANCE
            self.X_SIZE = object.X_SIZE
            self.Y_SIZE = object.Y_SIZE
            self.DIST_MIN = object.DIST_MIN
            self.DIST_MAX = object.DIST_MAX
            self.CAMERA_ERROR = object.CAMERA_ERROR
            self.ORIENTATION_PRECISION = object.ORIENTATION_PRECISION
            ### Tree Maps
            self.center_tree_map = numpy.zeros([self.X_SIZE, self.Y_SIZE])
            self.left_tree_map = numpy.zeros([self.X_SIZE, self.Y_SIZE])
            self.right_tree_map = numpy.zeros([self.X_SIZE, self.Y_SIZE])
            ### Spooler Maps
            self.left_spooler_map = numpy.zeros([self.X_SIZE, self.Y_SIZE])
            self.right_spooler_map = numpy.zeros([self.X_SIZE, self.Y_SIZE])
            ### Tree Positions
            self.blind_trees = [
                (16, 32),
                (16, 48),
                (16, 64),
                (32, 32),
                (48, 32),
                (64, 32),
                (80, 32),
                (80, 48),
                (80, 64),
            ]
            self.single_overlap_trees = [
                (32, 48),
                (48, 48),
                (64, 48),
            ]
            self.double_overlap_trees = [
                (16, 80),
                (32, 64),
                (32, 80),
                (48, 64),
                (48, 80),
                (64, 64),
                (64, 80),
                (80, 80),
            ]
            self.detected_trees = [
                (16, 32),
                (16, 48),
                (16, 64),
                (32, 32),
                (48, 32),
                (64, 32),
                (80, 32),
                (80, 48),
                (80, 64),
                (32, 48),
                (64, 48),
                (16, 80),
                #(32, 64),
                #(32, 80),
                #(48, 48),
                #(48, 64),
                #(48, 80),
                #(64, 64),
                #(64, 80),
                #(80, 80),
            ]
            ### Paths
            self.path = [
                (48, 1),
                (48, 32),
                (32, 32),
                (16, 32),
                (16, 48),
                (16, 64),
                (16, 80), 
                (32, 48),
                (64, 48),
                (64, 32),
                (80, 32),
                (80, 48), 
                (80, 64)
            ]
            self.true_path = [
            ]
            ### Spooler Position
            self.SPOOLER_DEFAULT_X = object.SPOOLER_DEFAULT_X
            self.SPOOLER_DEFAULT_Y = object.SPOOLER_DEFAULT_Y
            self.SPOOLER_DEFAULT_T = object.SPOOLER_DEFAULT_T
            self.spooler_position = (self.SPOOLER_DEFAULT_X, self.SPOOLER_DEFAULT_Y, self.SPOOLER_DEFAULT_T)
            ### Scout Positions
            self.SCOUT_LEFT_DEFAULT_X = object.SCOUT_LEFT_DEFAULT_X
            self.SCOUT_LEFT_DEFAULT_Y = object.SCOUT_LEFT_DEFAULT_Y
            self.SCOUT_LEFT_DEFAULT_T = object.SCOUT_LEFT_DEFAULT_T
            self.SCOUT_RIGHT_DEFAULT_X = object.SCOUT_RIGHT_DEFAULT_X
            self.SCOUT_RIGHT_DEFAULT_Y = object.SCOUT_RIGHT_DEFAULT_Y
            self.SCOUT_RIGHT_DEFAULT_T = object.SCOUT_RIGHT_DEFAULT_T
            self.scout_left_position = (self.SCOUT_LEFT_DEFAULT_X, self.SCOUT_LEFT_DEFAULT_Y, self.SCOUT_LEFT_DEFAULT_T)
            self.scout_right_position = (self.SCOUT_RIGHT_DEFAULT_X, self.SCOUT_RIGHT_DEFAULT_Y, self.SCOUT_RIGHT_DEFAULT_T)
            ### Movement Calibrations
            self.SPOOLER_MOVEMENT = object.SPOOLER_MOVEMENT
            self.SPOOLER_TURN = object.SPOOLER_TURN
            self.SCOUT_MOVEMENT = object.SCOUT_MOVEMENT
            self.SCOUT_TURN = object.SCOUT_TURN
            ### Commands
            self.FORWARD_COMMAND = object.FORWARD_COMMAND
            self.BACKWARD_COMMAND = object.BACKWARD_COMMAND
            self.RIGHT_COMMAND = object.RIGHT_COMMAND
            self.LEFT_COMMAND = object.LEFT_COMMAND
            self.WAIT_COMMAND = object.WAIT_COMMAND
            self.FORK_DOWN_COMMAND = object.FORK_DOWN_COMMAND
            self.FORK_UP_COMMAND = object.FORK_UP_COMMAND
            self.BOOM_RIGHT_COMMAND = object.BOOM_RIGHT_COMMAND
            self.BOOM_CENTER_COMMAND = object.BOOM_CENTER_COMMAND
            self.BOOM_LEFT_COMMAND = object.BOOM_LEFT_COMMAND
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
        print('\tSPOOLER')
        try:
            position = self.spooler_position
            ## 1. If not enough trees have been detected...
            if len(self.detected_trees) != self.NUM_TREES:
                trees_snapshot = request['trees_snapshot']
                self.draw_center_tree_map(trees_snapshot, position)
                self.detected_trees = self.predict_trees
                command = self.FORK_DOWN_COMMAND
            ## 2. If enough trees have been detected...
            elif len(self.path) < self.NUM_TREES:
                self.path = self.find_path(self.detected_trees)
                command = self.FORWARD_COMMAND
            ## 3. If a path has been found...
            elif len(self.true_path) < self.NUM_TREES:
                self.true_path = self.find_true_path(self.path)
                self.target_points = self.true_path[1:]
                command = self.FORK_UP_COMMAND
            ## 4. If points have been established...
            elif len(self.target_points) > 0:
                (target_x, target_y) = self.target_points[0]
                (x, y, t) = position
                ### Position
                (target_x, target_y) = self.target_points[0]
                if numpy.allclose(x, target_x, atol=self.SPOOLER_MOVEMENT) and numpy.allclose(y, target_y, atol=self.SPOOLER_MOVEMENT):
                    print('\t\tWARNING: Reached Target, proceeding to Next Point!')
                    self.target_points.pop(0)
                    (target_x, target_y) = self.target_points[0]
                distance_to_target = numpy.linalg.norm(numpy.array((target_x,target_y)) - numpy.array((x,y)))
                print('\t\tCurrent Point: %s' % str((x,y)))    
                print('\t\tTarget Point: %s' % str((target_x, target_y)))
                print('\t\tDistance to Target: %s' % str(distance_to_target))
                ### Orientation
                target_orientation = self.orientation((x,y), (target_x, target_y))
                if numpy.less(t, target_orientation) and ((target_orientation - t) < numpy.pi):
                    if (t - target_orientation) > 2 * numpy.pi:
                        orientation_to_target = abs(t - target_orientation - 2 * numpy.pi) #!TODO
                    else:
                        orientation_to_target = abs(t - target_orientation) #!TODO
                elif numpy.greater(t, target_orientation) or ((target_orientation - t) < 2 * numpy.pi):
                    if (t - target_orientation) < 0:
                        orientation_to_target = abs(2 * numpy.pi - t - target_orientation) #!TODO
                    else:
                        orientation_to_target = abs(t - target_orientation) #!TODO
                print('\t\tCurrent Orientation: %s' % str(t))
                print('\t\tTarget Orientation: %s' % str(target_orientation))
                print('\t\tOrientation to Target: %s' % str(orientation_to_target))
                ### Move Forward
                if numpy.allclose(t, target_orientation, atol=self.SPOOLER_TURN):
                    num_commands = int(math.ceil(distance_to_target / self.SPOOLER_MOVEMENT))
                    command = self.FORWARD_COMMAND + str(num_commands)
                    movement = num_commands * self.SPOOLER_MOVEMENT
                    new_x = x + movement * numpy.cos(t)
                    new_y = y + movement * numpy.sin(t)
                    self.spooler_position = (new_x, new_y, t)
                ### Turn Right
                elif (numpy.less(t, target_orientation) and numpy.less(target_orientation - t, numpy.pi)) or (numpy.less(t, target_orientation + 2 * numpy.pi) and numpy.less(2 * numpy.pi + target_orientation - t, numpy.pi)): #!TODO
                    num_commands = int(math.ceil(orientation_to_target / self.SPOOLER_TURN))
                    command = self.RIGHT_COMMAND + str(num_commands)
                    new_t = t + num_commands * self.SPOOLER_TURN
                    if new_t > 2 * numpy.pi:
                        new_t_round = numpy.around(new_t - 2 * numpy.pi, self.ORIENTATION_PRECISION)
                    else:
                        new_t_round = numpy.around(new_t, self.ORIENTATION_PRECISION)
                    self.spooler_position = (x, y, new_t_round)
                ### Turn Left
                elif numpy.greater(t, target_orientation) or ((target_orientation - t) < 2 * numpy.pi): #!TODO
                    num_commands = int(math.ceil(orientation_to_target / self.SPOOLER_TURN))
                    command = self.LEFT_COMMAND + str(num_commands)
                    new_t = t - num_commands * self.SPOOLER_TURN
                    if new_t < 0:
                        new_t = numpy.around(2 * numpy.pi + new_t, self.ORIENTATION_PRECISION)
                    else:
                        new_t = numpy.around(new_t, self.ORIENTATION_PRECISION)
                    self.spooler_position = (x, y, new_t)
                else:
                    command = self.WAIT_COMMAND
            else:
                command = self.WAIT_COMMAND
        except Exception as error:
            print('\t\tERROR in command_spooler(): %s' % str(error))
            command = self.WAIT_COMMAND
        response = {
            'type' : 'response', 
            'command' : command
        }
        print('\t\t--> Command: %s' % str(command))
        return response
    
    ##!TODO Handle Scout (Left)
    def command_scout_left(self, request):
        print('\tLEFT SCOUT')
        try:
            trees_snapshot = request['trees_snapshot']
            spooler_snapshot = request['spooler_snapshot']
            ### 1. If not enough trees detected ...
            if len(self.detected_trees) != self.NUM_TREES:
                self.draw_left_tree_map(trees_snapshot)
                command = self.WAIT_COMMAND
            ### 2. If enough trees detected ...
            else:
                self.draw_left_spooler_map(spooler_snapshot)
                command = self.WAIT_COMMAND
        except Exception as error:
            print('\t\tERROR in command_scout_left(): %s' % str(error))
            command = self.WAIT_COMMAND
        response = {
            'type' : 'response', 
            'command' : command
        }
        print('\t\t--> Command: %s' % command)
        return response #!TODO decide movement actions for scout left 
        
    ##!TODO Handle Scout (Right)
    def command_scout_right(self, request):
        print('\tRIGHT SCOUT')
        try:
            tree_snapshot = request['trees_snapshot']
            spooler_snapshot = request['spooler_snapshot']
            position = self.scout_right_position
            ### 1. If not enough trees detected ...
            if len(self.detected_trees) != self.NUM_TREES:
                self.draw_right_tree_map(tree_snapshot)
                command = self.WAIT_COMMAND
            ### 2. If enough trees detected ...
            else:
                self.draw_right_spooler_map(spooler_snapshot)
                command = self.WAIT_COMMAND
        except Exception as error:
            print('\t\tERROR in command_scout_right(): %s' % str(error))
            command = self.WAIT_COMMAND
        response = {
            'type' : 'response', 
            'command' : command
        }
        print('\t\t--> Command: %s' % command)
        return response #!TODO decide movement actions for scout right 

    ## Update Map   
    def update_tree_map(self):
        print('\t\t[Updating Tree Map] %s' % datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
        try:
            tree_map = 255 * (self.left_tree_map + self.center_tree_map + self.right_tree_map)
            return tree_map
        except Exception as error:
            print('\tERROR: %s' % str(error))
    
    ## Update Map   
    def draw_left_tree_map(self, snapshot):
        print('\t\t[Drawing Right Tree Map] %s' % datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
        self.left_tree_map = numpy.zeros([self.X_SIZE, self.Y_SIZE])
        (x, y, t) = self.scout_left_position
        x_all = []
        y_all = []
        for offset in snapshot:
            for error in numpy.linspace(-0.05, 0.05):
                x1 = x + numpy.cos(t + offset + error) * self.DIST_MIN
                y1 = y + numpy.sin(t + offset + error) * self.DIST_MIN
                if (x1 >= self.X_SIZE - 2) or (y1 >= self.Y_SIZE - 2):
                    pass
                elif (x1 <= 2) or (y1 <= 2):
                    pass
                else:
                    for dist in range(self.DIST_MIN, self.DIST_MAX):
                        x2 = x1 + numpy.cos(t + offset + error) * dist
                        y2 = y1 + numpy.sin(t + offset + error) * dist
                        if (x2 >= self.X_SIZE - 2) or (y2 >= self.Y_SIZE - 2):
                            break
                        elif (x2 <= 2) or (y2 <= 2):
                            break
                        else:
                             continue
                    x_vals = numpy.linspace(x1, x2, dist).astype(int)
                    y_vals = numpy.linspace(y1, y2, dist).astype(int)
                    self.left_tree_map[x_vals, y_vals] = 1
                    
    ## Draw Center Tree Map   
    def draw_center_tree_map(self, snapshot):
        print('\t\t[Drawing Spooler Tree Map]')
        self.center_tree_map = numpy.zeros([self.X_SIZE, self.Y_SIZE])
        (x, y, t) = self.spooler_position
        x_all = []
        y_all = []
        for offset in snapshot:
            for error in numpy.linspace(-0.05, 0.05):
                x1 = x + numpy.cos(t + offset + error) * self.DIST_MIN
                y1 = y + numpy.sin(t + offset + error) * self.DIST_MIN
                if (x1 >= self.X_SIZE - 2) or (y1 >= self.Y_SIZE - 2):
                    pass
                elif (x1 <= 2) or (y1 <= 2):
                    pass
                else:
                    for dist in range(self.DIST_MIN, self.DIST_MAX):
                        x2 = x1 + numpy.cos(t + offset + error) * dist
                        y2 = y1 + numpy.sin(t + offset + error) * dist
                        if (x2 >= self.X_SIZE - 2) or (y2 >= self.Y_SIZE - 2):
                            break
                        elif (x2 <= 2) or (y2 <= 2):
                            break
                        else:
                             continue
                    x_vals = numpy.linspace(x1, x2, dist).astype(int)
                    y_vals = numpy.linspace(y1, y2, dist).astype(int)
                    self.center_tree_map[x_vals, y_vals] = 1
    ## Update Map   
    def draw_right_tree_map(self, snapshot):
        print('\t\t[Drawing Right Tree Map]')
        self.right_tree_map = numpy.zeros([self.X_SIZE, self.Y_SIZE])
        (x, y, t) = self.scout_right_position
        x_all = []
        y_all = []
        for offset in snapshot:
            for error in numpy.linspace(-0.05, 0.05):
                x1 = x + numpy.cos(t + offset + error) * self.DIST_MIN
                y1 = y + numpy.sin(t + offset + error) * self.DIST_MIN
                if (x1 >= self.X_SIZE - 2) or (y1 >= self.Y_SIZE - 2):
                    pass
                elif (x1 <= 2) or (y1 <= 2):
                    pass
                else:
                    for dist in range(self.DIST_MIN, self.DIST_MAX):
                        x2 = x1 + numpy.cos(t + offset + error) * dist
                        y2 = y1 + numpy.sin(t + offset + error) * dist
                        if (x2 >= self.X_SIZE - 2) or (y2 >= self.Y_SIZE - 2):
                            break
                        elif (x2 <= 2) or (y2 <= 2):
                            break
                        else:
                             continue
                    x_vals = numpy.linspace(x1, x2, dist).astype(int)
                    y_vals = numpy.linspace(y1, y2, dist).astype(int)
                    self.right_tree_map[x_vals, y_vals] = 1
    ## Update Map   
    def update_spooler_map(self):
        print('\t\tUpdating Spooler Map] %s' % datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
        try:
            spooler_map = 255 * (self.left_spooler_map + self.right_spooler_map)
            return spooler_map
        except Exception as error:
            print('\tERROR: %s' % str(error))
            
    ## Draw Left Spooler Map   
    def draw_left_spooler_map(self, snapshot):
        print('\t\t[Drawing Right Tree Map] %s' % datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
        self.left_spooler_map = numpy.zeros([self.X_SIZE, self.Y_SIZE])
        (x, y, t) = self.scout_left_position
        x_all = []
        y_all = []
        for offset in snapshot:
            for error in numpy.linspace(-0.05, 0.05):
                x1 = x + numpy.cos(t + offset + error) * self.DIST_MIN
                y1 = y + numpy.sin(t + offset + error) * self.DIST_MIN
                if (x1 >= self.X_SIZE - 2) or (y1 >= self.Y_SIZE - 2):
                    pass
                elif (x1 <= 2) or (y1 <= 2):
                    pass
                else:
                    for dist in range(self.DIST_MIN, self.DIST_MAX):
                        x2 = x1 + numpy.cos(t + offset + error) * dist
                        y2 = y1 + numpy.sin(t + offset + error) * dist
                        if (x2 >= self.X_SIZE - 2) or (y2 >= self.Y_SIZE - 2):
                            break
                        elif (x2 <= 2) or (y2 <= 2):
                            break
                        else:
                             continue
                    x_vals = numpy.linspace(x1, x2, dist).astype(int)
                    y_vals = numpy.linspace(y1, y2, dist).astype(int)
                    self.left_spooler_map[x_vals, y_vals] = 1
    
    ## Draw Right Spooler Map   
    def draw_right_spooler_map(self, snapshot):
        print('\t\t[Drawing Right Spooper Map]')
        self.right_spooler_map = numpy.zeros([self.X_SIZE, self.Y_SIZE])
        (x, y, t) = self.scout_right_position
        x_all = []
        y_all = []
        for offset in snapshot:
            for error in numpy.linspace(-0.05, 0.05):
                x1 = x + numpy.cos(t + offset + error) * self.DIST_MIN
                y1 = y + numpy.sin(t + offset + error) * self.DIST_MIN
                if (x1 >= self.X_SIZE - 2) or (y1 >= self.Y_SIZE - 2):
                    pass
                elif (x1 <= 2) or (y1 <= 2):
                    pass
                else:
                    for dist in range(self.DIST_MIN, self.DIST_MAX):
                        x2 = x1 + numpy.cos(t + offset + error) * dist
                        y2 = y1 + numpy.sin(t + offset + error) * dist
                        if (x2 >= self.X_SIZE - 2) or (y2 >= self.Y_SIZE - 2):
                            break
                        elif (x2 <= 2) or (y2 <= 2):
                            break
                        else:
                             continue
                    x_vals = numpy.linspace(x1, x2, dist).astype(int)
                    y_vals = numpy.linspace(y1, y2, dist).astype(int)
                    self.right_spooler_map[x_vals, y_vals] = 1

    ## Predict Tree Locations        
    def predict_trees(self, tree_map):
        print('\t[Predicting Tree Locations] %s' % datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
        tree_locations = []
        if len(tree_locations) < self.NUM_TREES:
            for (a,b) in self.double_overlap_trees:
                if tree_map[a,b] >= 255 * 3: # might throw dim error
                    tree_locations.append( (a, b) )
        if len(tree_locations) < self.NUM_TREES:
            for (a,b) in self.single_overlap_trees:
                if tree_map[a,b] >= 255 * 2: # might throw dim error
                    tree_locations.append( (a, b) )
        if len(tree_locations) < self.NUM_TREES:
            for (a,b) in self.blind_trees:
                if tree_map[a,b] >= 255 * 1: # might throw dim error
                    tree_locations.append( (a, b) )
        detected_trees = list(set(tree_locations))
        print('\tTrees: %s' % str(self.detected_trees))
        return detected_trees
    
    ## Predict Robot Locations
    def predict_robots(self):
        print('\t\t[Predicting Robot Locations] %s' % datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
        (scout_left_x, scout_left_y, scout_left_t) = self.scout_left_position
        (scout_right_x, scout_right_y, scout_right_t) = self.scout_right_position
        (spooler_x, spooler_y, spooler_t) = self.spooler_position
        robot_positions = {
            'scout_left' : (int(scout_left_x), int(scout_left_y), int(scout_left_t)),
            'scout_right' : (int(scout_right_x), int(scout_right_y), int(scout_right_t)),
            'spooler' : (int(spooler_x), int(spooler_y), int(spooler_t))
        }
        return robot_positions
    
    ## Calculate Minimum Hamiltonian Path
    def find_path(self, trees):
        print('\t\t[Find Shortest Path] %s' % datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
        try:
            #points = trees.append((48,1)) # add start
            ## Find First tree
            first_tree_paths = []
            for i in range(len(trees)):
                d = self.dist((48,1), trees[i])
                first_tree_paths.append((d,i))
            (min_first_tree_dist, min_first_tree_index) = min(first_tree_paths)
            first_tree = trees[min_first_tree_index]
            trees.pop(min_first_tree_index)
            ## Find Second Tree
            second_tree_paths = []
            for i in range(len(trees)):
                d = self.dist(first_tree, trees[i])
                second_tree_paths.append((d,i))
            (min_second_tree_dist, min_second_tree_index) = min(second_tree_paths)
            second_tree = trees[min_second_tree_index]
            trees.pop(min_second_tree_index)
            print('\t\tRemaining Trees: %d' % len(trees))
            ## Find Shortest Path
            try:
                print('\t\tGenerating permutations ...')
                paths = []
                for p in it.permutations(trees):
                    p = p + (second_tree, first_tree, (48,1))
                    paths.append(p)
            except Exception as error:
                print('\t\tERROR: Failed to generate all permutations: %s' % str(error))
            try:
                print('\t\tFinding path distances ...')
                path_distances = [ sum(map(lambda x: self.dist(x[0],x[1]), zip(p[:-1],p[1:]))) for p in paths ]
            except Exception as error:
                print('\t\tERROR: Failed to calculate all distances: %s' % str(error))
            try:
                print('\t\tFinding min index ...')
                min_index = numpy.argmin(path_distances)
            except Exception:
                print('\t\t\tERROR: Failed to find min index')
            try:
                print('\t\tFinding shortest path by index ...')
                shortest_path = paths[min_index]
                print('\tPath: %s' % str(shortest_path[::-1]))
                return shortest_path[::-1]
            except Exception:
                print('\t\t\tERROR: Failed to find shortest path')
        except Exception as error:
            print('\t\t\tERROR: %s' % str(error))
    
    ## Calculate the True Path for Spooler to Travel
    def find_true_path(self, path):
        print('\t\t[Find True Path] %s' % datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
        true_path = [(self.SPOOLER_DEFAULT_X, self.SPOOLER_DEFAULT_Y)]
        ## Add pivots
        for i in range(1, len(path) - 1):
            try:
                previous = true_path[-1] #!TODO
                current = path[i]
                next = path[i+1]
                points = self.pivot_point(previous, current, next)
                for p in points:
                    true_path.append(p)
            except Exception as error:
                print('\t\t\tERROR: %s' % str(error))
        ## Add anchor points
        current = path[-2]
        last = path[-1]
        anchor_points = self.anchor_points(current, last)
        for point in anchor_points:
            true_path.append(point)
        print('\t\t\tTrue Path: %s' % str(true_path))
        return true_path
    
    ## Distance Function
    def dist(self, x, y):
        return math.hypot( y[0] - x[0], y[1] - x[1] )
        
    ## Pivot Point #!TODO fix bad pivots
    def pivot_point(self, tree1, tree2, tree3):
        print('\t[Calculating Pivot Point]')
        print('\t\tPoint 1: %s' % str(tree1))
        print('\t\tPoint 2: %s' % str(tree2))
        print('\t\tPoint 3: %s' % str(tree3))
        (x1, y1) = tree1
        (x2, y2) = tree2
        (x3, y3) = tree3
        m1 = self.slope(tree1, tree3)
        m2 = self.median_slope(tree1, tree2, tree3)
        print('\t\t1-3 Slope: %s' % str(m1))
        print('\t\tBisected Slope: %s' % str(m2))
        dx = self.PIVOT_DISTANCE
        dy = self.PIVOT_DISTANCE
        if numpy.isinf(m2):
            x4_plus = x2
            y4_plus = y2 + dy
            x4_minus = x2
            y4_minus = y2 - dy
        else:
            x4_plus = x2 + dx / numpy.sqrt(1 + m2**2)
            y4_plus = y2 + dy * m2 / numpy.sqrt(1 + m2**2)
            x4_minus = x2 - dx / numpy.sqrt(1 + m2**2)
            y4_minus = y2 - dy * m2 / numpy.sqrt(1 + m2**2)
        p_a = (x4_plus, y4_minus)
        p_b = (x4_minus, y4_plus)
        p_c = (x4_minus, y4_minus)
        p_d = (x4_plus, y4_plus)
        points = [p_a, p_b, p_c, p_d]
        p_int = self.intersecting_point( m1, m2, tree1, tree2 )
        print('\t\tIntersection Point: %s' % str(p_int))
        m_a = self.slope(p_int, p_a)
        m_b = self.slope(p_int, p_b)
        m_c = self.slope(p_int, p_c)
        m_d = self.slope(p_int, p_d)
        slopes = [ m_a, m_b, m_c, m_d ]
        pivots = []
        if numpy.allclose(m_a, m2, atol=0.01):
            pivots.append( (int(p_a[0]), int(p_a[1])) )
        if numpy.allclose(m_b, m2, atol=0.01):
            pivots.append( (int(p_b[0]), int(p_b[1])) )
        if numpy.allclose(m_c, m2, atol=0.01):
            pivots.append( (int(p_c[0]), int(p_c[1])) )
        if numpy.allclose(m_d, m2, atol=0.01):
            pivots.append( (int(p_d[0]), int(p_d[1])) )
        distances = [ self.dist(p_int, p) for p in pivots ]
        p_pivot = pivots[numpy.argmax(distances)]
        print('\t\tPossible Pivots: %s' % str(p_pivot))
        angle = abs(self.orientation(tree2, tree1) - self.orientation(tree2, tree3))
        print('\t\tTurning Angle: %s' % str(angle))
        if (angle > numpy.pi / 2.0) or (angle == 0):
            pivots = [p_pivot]
        else:
            m3 = self.perpendicular_slope(m2)
            print('\t\tPerpendicular slope: %s' % str(m3))
            dx = self.PIVOT_DISTANCE
            dy = self.PIVOT_DISTANCE
            x_pivot_plus = p_pivot[0] + dx / numpy.sqrt(1 + m3**2)
            y_pivot_plus = p_pivot[1] + dy * m3 / numpy.sqrt(1 + m3**2)
            x_pivot_minus = p_pivot[0] - dx / numpy.sqrt(1 + m3**2)
            y_pivot_minus = p_pivot[1] - dy * m3 / numpy.sqrt(1 + m3**2)
            p_a = (x_pivot_plus, y_pivot_minus)
            p_b = (x_pivot_minus, y_pivot_plus)
            p_c = (x_pivot_minus, y_pivot_minus)
            p_d = (x_pivot_plus, y_pivot_plus)
            points = [p_a, p_b, p_c, p_d]
            m_a = self.slope(p_pivot, p_a)
            m_b = self.slope(p_pivot, p_b)
            m_c = self.slope(p_pivot, p_c)
            m_d = self.slope(p_pivot, p_d)
            slopes = [ m_a, m_b, m_c, m_d ]
            pivots = []
            if numpy.allclose(m_a, m3, atol=0.01):
                pivots.append( (int(p_a[0]), int(p_a[1])) )
            if numpy.allclose(m_b, m3, atol=0.01):
                pivots.append( (int(p_b[0]), int(p_b[1])) )
            if numpy.allclose(m_c, m3, atol=0.01):
                pivots.append( (int(p_c[0]), int(p_c[1])) )
            if numpy.allclose(m_d, m3, atol=0.01):
                pivots.append( (int(p_d[0]), int(p_d[1])) )
            if self.dist(tree1, pivots[0]) > self.dist(tree1, pivots[1]):
                pivots = pivots[::-1]
        print('\t\tPivot Points: %s' % str(pivots))
        return pivots
    
    ## Point of Intersection
    def intersecting_point(self, slope1, slope2, point1, point2):
        print('\t\t[Intersection Point]')
        (x1, y1) = point1
        (x2, y2) = point2
        m1 = slope1
        m2 = slope2
        if numpy.isinf(m1):
            c2 = y2 - m2*x2
            pt_int = (x1, c2 + m2*x1)
        elif numpy.isinf(m2):
            c1 = y1 - m1*x1
            pt_int = (x2, c1 + m1*x2)
        else:
            c1 = y1 - m1*x1
            c2 = y2 - m2*x2
            a = numpy.array([[-m1,1], [-m2,1]])
            b = numpy.array([c1,c2])       
            pt_float = numpy.linalg.solve(a, b)
            pt_int = (pt_float[0], pt_float[1])
        return pt_int
    
    ## Anchor Points #!TODO improve point calculations
    def anchor_points(self, tree1, tree2):
        print ('\t[Calculating Anchor Points]')
        print('\t\tSecond-to-Last Tree: %s' % str(tree1))
        print('\t\tLast Tree: %s' % str(tree2))
        (x1, y1) = tree1
        (x2, y2) = tree2
        m1 = self.slope(tree1, tree2)
        m2 = self.perpendicular_slope(m1)
        if numpy.isinf(m1):
            x3 = int(x2)
            y3 = int(y2 + self.PIVOT_DISTANCE)
            x5 = int(x2)
            y5 = int(y2 - self.PIVOT_DISTANCE)
        else:
            x3 = int(x2 + self.PIVOT_DISTANCE / numpy.sqrt(1 + m1**2))
            y3 = int(y2 + self.PIVOT_DISTANCE * m1 / numpy.sqrt(1 + m1**2))
            x5 = int(x2 - self.PIVOT_DISTANCE / numpy.sqrt(1 + m1**2))
            y5 = int(y2 - self.PIVOT_DISTANCE * m1 / numpy.sqrt(1 + m1**2))
        if numpy.isinf(m2):
            x4 = int(x2)
            y4 = int(y2 + self.PIVOT_DISTANCE)
            x6 = int(x2)
            y6 = int(y2 - self.PIVOT_DISTANCE)
        else:
            x4 = int(x2 + self.PIVOT_DISTANCE / numpy.sqrt(1 + m2**2))
            y4 = int(y2 + self.PIVOT_DISTANCE * m2 / numpy.sqrt(1 + m2**2))
            x6 = int(x2 - self.PIVOT_DISTANCE / numpy.sqrt(1 + m2**2))
            y6 = int(y2 - self.PIVOT_DISTANCE * m2 / numpy.sqrt(1 + m2**2))
        
        ### Clockwise vs. Counter-Clockwise
        if self.dist(tree1, (x3, y3)) < self.dist(tree1, (x5, y5)):
            if self.dist(tree1, (x4, y4)) < self.dist(tree1, (x6, y6)):
                points = [ (x3, y3), (x4, y4), (x5, y5), (x6, y6) ]
            else:
                points = [ (x3, y3), (x6, y6), (x5, y5), (x4, y4) ]
        else:
            if self.dist(tree1, (x4, y4)) < self.dist(tree1, (x6, y6)):
                points = [ (x5, y5), (x4, y4), (x3, y3), (x6, y6) ]
            else:
                points = [ (x5, y5), (x6, y6), (x3, y3), (x4, y4) ]
        return points
        
    ## Find slope
    def slope(self, pt1, pt2):
        print('\t\t[Finding Slope]')
        (x1, y1) = pt1
        (x2, y2) = pt2
        try:
            m = float(y2 - y1) / float(x2 - x1)
        except Exception as error:
            if (x2 - x1) >= 0:
                m = numpy.inf
            elif (x2 - x1) < 0:
                m = -numpy.inf
        return m
    
    ## Find Perpedicular Slope
    def perpendicular_slope(self, m1):
        try:
            m2 = -1 / m1
        except Exception as error:
            m2 = numpy.inf
        return m2
    
    def median_slope(self, p_1, p_2, p_3):
        print('\t\t[Median Slope]')
        try:
            (x_1, y_1) = p_1
            (x_2, y_2) = p_2
            (x_3, y_3) = p_3
            x_median = (x_1 + x_3) / 2.0
            y_median = (y_1 + y_3) / 2.0
            m_median = (y_median - y_2) / (x_median - x_2)
        except Exception as error:
            m_median = numpy.inf
        return m_median
    
    ## Angle of Orientation
    def orientation(self, pt1, pt2):
        (x, y) = pt1
        (target_x, target_y) = pt2
        try:
            m = float(target_y - y) / float(target_x - x)
        except Exception as error:
            if (target_y - y) > 0:
                m = numpy.inf
            elif (target_y - y) < 0:
                m = -numpy.inf
        at = numpy.arctan(m)
        if target_y > y:
            if target_x > x:
                t = at
            elif target_x < x:
                t = at + numpy.pi
            else:
                t = numpy.pi / 2.0
        elif target_y < y:
            if target_x > x:
                t = at + 2.0 * numpy.pi
            elif target_x < x:
                t = at + numpy.pi
            else:
                t = 3.0 * numpy.pi / 2.0
        else:
            if target_x > x:
                t = 0
            elif target_x < x:
                t = numpy.pi
            else:
                t = numpy.nan # a = b
        t_round = numpy.around(t, self.ORIENTATION_PRECISION)
        return t_round
    
    ## Close State Machine
    def close(self):
        print('[Closing State Machine] %s' % datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
        
def main():
    gtk.main()
    
if __name__ == '__main__':
    host = Host(CONFIG)
    main()
