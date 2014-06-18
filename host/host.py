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
            true_path = self.state_machine.true_path
            self.display.show_board(trees, robots, path, true_path)
            self.database.store(request, response)

    ## Stop 
    def stop(self, object):
        print('[Stopping] %s' % datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
        self.running = False
        
    ## Reset 
    def reset(self, object):
        print('[Stopping] %s' % datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
        self.state_machine = StateMachine(self)
        
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
    def show_board(self, tree_locations, robot_locations, path, true_path):
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
            self.PIVOT_DISTANCE = object.PIVOT_DISTANCE
            self.X_SIZE = object.X_SIZE
            self.Y_SIZE = object.Y_SIZE
            self.DIST_MIN = object.DIST_MIN
            self.DIST_MAX = object.DIST_MAX
            self.CAMERA_ERROR = object.CAMERA_ERROR
            self.ORIENTATION_PRECISION = object.ORIENTATION_PRECISION
            self.detected_trees = []
            self.path = []
            self.true_path = []
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
            self.spooler_position = (object.SPOOLER_DEFAULT_X, object.SPOOLER_DEFAULT_Y, object.SPOOLER_DEFAULT_T)
            self.scout_left_position = (object.SCOUT_LEFT_DEFAULT_X, object.SCOUT_LEFT_DEFAULT_Y, object.SCOUT_LEFT_DEFAULT_T)
            self.scout_right_position = (object.SCOUT_RIGHT_DEFAULT_X, object.SCOUT_RIGHT_DEFAULT_Y, object.SCOUT_RIGHT_DEFAULT_T)
            self.SPOOLER_LARGE_MOVEMENT = object.SPOOLER_LARGE_MOVEMENT
            self.SPOOLER_FINE_MOVEMENT = object.SPOOLER_FINE_MOVEMENT
            self.SPOOLER_LARGE_TURN = object.SPOOLER_LARGE_TURN
            self.SPOOLER_FINE_TURN = object.SPOOLER_FINE_TURN
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
            position = self.spooler_position
            self.detected_trees = self.predict_trees()
            if len(self.detected_trees) < self.NUM_TREES:
                print('\tWARNING: Not enough trees detected')
                self.update_map(snapshot, position) 
                command = 'wait'
            elif len(self.path) < self.NUM_TREES:
                print('\tWARNING: Ready to calculate path')
                self.path = self.find_path(self.detected_trees)
                self.true_path = self.find_true_path(self.path)
                self.target_points = self.true_path[1:]
                command = 'wait'
            elif len(self.target_points) > 0:
                print('\tWARNING: Running Path')
                #!TODO decide movement actions for spooler
                (target_x, target_y) = self.target_points[0]
                (x, y, t) = position
                if numpy.allclose(x, target_x, atol=1) and numpy.allclose(y, target_y, atol=1):
                    print('\tWARNING: Reached Target, proceeding to Next Point!')
                    self.target_points.pop(0)
                    (target_x, target_y) = self.target_points[0]
                print('\tTarget Point: %s' % str((target_x, target_y)))
                target_orientation = self.orientation((x,y), (target_x, target_y))
                print('\tTarget Orientation: %s' % str(target_orientation))
                distance_to_target = int(numpy.linalg.norm(numpy.array((target_x,target_y)) - numpy.array((x,y))))
                print('\tDistance to Target: %s' % str(distance_to_target))
                print('\tCurrent Orientation: %s' % str(t))
                print('\tCurrent Position: %s' % str((x,y)))
                ### Move Forward
                if numpy.allclose(t, target_orientation, atol=self.SPOOLER_FINE_TURN):
                    print('\tCosine: %s' % str(numpy.cos(t)))
                    print('\tSin: %s' % (numpy.sin(t)))
                    if numpy.less(distance_to_target, self.SPOOLER_LARGE_MOVEMENT):
                        command = 'forward_fine'
                        new_x = int(x + self.SPOOLER_FINE_MOVEMENT * numpy.cos(t))
                        new_y = int(y + self.SPOOLER_FINE_MOVEMENT * numpy.sin(t))
                    else:
                        command = 'forward_large'
                        new_x = int(x + self.SPOOLER_LARGE_MOVEMENT * numpy.cos(t))
                        new_y = int(y + self.SPOOLER_LARGE_MOVEMENT * numpy.sin(t))
                    self.spooler_position = (new_x, new_y, t)
                ### Turn Right #!TODO Fine vs Large, Turning right from wide to 0 also broken
                elif numpy.less(t, target_orientation) and ((target_orientation-t) < numpy.pi):
                    command = 'right'
                    new_t = t + self.SPOOLER_FINE_TURN
                    if new_t > 2 * numpy.pi:
                        new_t_round = numpy.around(new_t - 2 * numpy.pi, self.ORIENTATION_PRECISION)
                    else:
                        new_t_round = numpy.around(new_t, self.ORIENTATION_PRECISION)
                    self.spooler_position = (x, y, new_t_round)
                ### Turn Right #!TODO fine vs large
                elif numpy.greater(t, target_orientation) or ((target_orientation - t) < 2 * numpy.pi):
                    command = 'left'
                    new_t = t - self.SPOOLER_FINE_TURN
                    if new_t < 0:
                        new_t = numpy.around(2 * numpy.pi + new_t, self.ORIENTATION_PRECISION)
                    else:
                        new_t = numpy.around(new_t, self.ORIENTATION_PRECISION)
                    self.spooler_position = (x, y, new_t)
                ### Move Backward #!TODO
                elif False:
                    command = 'backward'
                else:
                    command = 'wait'
                time.sleep(1)
            else:
                command = 'wait'
        except Exception as error:
            print('\tERROR: %s' % str(error))
        print('\tCommand: %s' % str(command))
        response = {
            'type' : 'response', 
            'command' : command
        }
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
        (x, y, t) = position
        for offset in snapshot:
            for orientation in [-self.CAMERA_ERROR, 0, self.CAMERA_ERROR]: # #!TODO more then 3
                x1 = x + numpy.cos(t + offset + self.CAMERA_ERROR) * self.DIST_MIN
                y1 = y + numpy.sin(t + offset + self.CAMERA_ERROR) * self.DIST_MIN
                for dist in range(self.DIST_MIN, self.DIST_MAX):
                    x2 = x1 + numpy.cos(t + offset + self.CAMERA_ERROR) * dist
                    y2 = y1 + numpy.sin(t + offset + self.CAMERA_ERROR) * dist
                    if (x2 >= self.X_SIZE - 2) or (y2 >= self.Y_SIZE - 2):
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
        robot_positions = {
            'scout_left' : self.scout_left_position,
            'scout_right' : self.scout_right_position,
            'spooler' : self.spooler_position
        }
        return robot_positions
    
    ## Calculate Minimum Hamiltonian Path
    def find_path(self, trees):
        print('[Find Shortest Path] %s' % datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
        points = trees.append((48,1)) # add start
        paths = [ p for p in it.permutations(trees) ]
        path_distances = [ sum(map(lambda x: self.dist(x[0],x[1]),zip(p[:-1],p[1:]))) for p in paths ]
        min_index = numpy.argmin(path_distances)
        shortest_path = paths[min_index]
        print('\tPath: %s' % str(shortest_path[::-1]))
        return shortest_path[::-1]
    
    ## Calculate the True Path for Spooler to Travel
    def find_true_path(self, path):
        print('[Find True Path] %s' % datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
        true_path = [(48,1)]
        ## Add pivots
        for i in range(1, len(path) - 1):
            try:
                previous = path[i-1]
                current = path[i]
                next = path[i+1]
                point = self.pivot_point(previous, current, next)
                true_path.append(point)
            except Exception as error:
                print('\tERROR: %s' % str(error))
        ## Add anchor points
        current = path[-2]
        last = path[-1]
        anchor_points = self.anchor_points(current, last)
        for point in anchor_points:
            true_path.append(point)
        print('\tTrue Path: %s' % str(true_path))
        return true_path
    
    ## Distance Function
    def dist(self, x, y):
        return math.hypot( y[0] - x[0], y[1]-x[1] )
        
    ## Pivot Point #!TODO fix bad pivots
    def pivot_point(self, tree1, tree2, tree3):
        print('\t[Calculating Pivot Point]')
        (x1, y1) = tree1
        (x2, y2) = tree2
        (x3, y3) = tree3
        m1 = self.slope(tree1, tree3)
        m2 = self.perpendicular_slope(m1)
        print('\t\tSlope 1: %s' % str(m1))
        print('\t\tSlope 2: %s' % str(m2))
        ## Conditional for direction
        if (x2 < x1) or (x2 < x3):
            dx = -self.PIVOT_DISTANCE
        else:
            dx = self.PIVOT_DISTANCE
        if (y2 > y1) and (y2 > y3):
            dy = self.PIVOT_DISTANCE
        else:
            dy = -self.PIVOT_DISTANCE
        ## Handle Infinite cases
        if numpy.isinf(m2):
            x4 = x2 + dx
            y4 = y2 + dy
        else:
            x4 = x2 + dx / numpy.sqrt(1 + m2**2)
            y4 = y2 + dy * m2 / numpy.sqrt(1 + m2**2)
        print('\t\tdx: %s' % str(dx))
        print('\t\tdy: %s' % str(dx))
        point = (int(x4), int(y4))
        return point
    
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
        points = [ (x3, y3), (x4, y4), (x5, y5), (x6, y6) ]
        return points
        
    ## Find slope
    def slope(self, pt1, pt2):
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
    
    ## Angle of Orientation
    def orientation(self, pt1, pt2):
        (x, y) = pt1
        (target_x, target_y) = pt2
        try:
            m = float(target_y - y) / float(target_x - x)
        except Exception as error:
            print('\tERROR: %s' % str(error))
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
        print('\tArcTan: %s' % str(at))
        print('\tAdjusted ArcTan: %s' % str(t))
        print('\tSlope: %s' % str(m))
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
