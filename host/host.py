"""
Host

TODO:
- break into classes
"""

import json
import zmq
import sys
import os
import cherrypy
import datetime,time
from cherrypy.process.plugins import Monitor
from cherrypy import tools
from pymongo import MongoClient

# Constants
try:
    CONFIG = sys.argv[1]
except Exception as err:
    CONFIG = 'settings.json'

class Host:

    def __init__(self, config):
    
        ### Configs
        print('[Loading Config File]')
        with open(config) as config_file:
            settings = json.loads(config_file.read())
            print('--> settings : ' + json.dumps(settings, sort_keys=True, indent=4))
            for key in settings:
                try:
                    getattr(self, key)
                except AttributeError as error:
                    setattr(self, key, settings[key])         
        ### ZMQ
        print('[Initializing ZMQ]')
        try:
            self.context = zmq.Context()
            self.socket = self.context.socket(zmq.REP)
            self.socket.bind(self.ZMQ_SERVER)
        except Exception as error:
            print('--> ERROR: ' + str(error))
            
        ### CherryPy Monitors
        print('[Enabling Monitors]')
        try:
            Monitor(cherrypy.engine, self.listen, frequency=self.CHERRYPY_LISTEN_INTERVAL).subscribe()
        except Exception as error:
            print('--> ERROR: ' + str(error))
            
        ### Mongo 
        print('[Connecting to Mongo]')
        try:
            client = MongoClient()
            database = client[self.MONGO_DB]
            trial_name = datetime.datetime.now().strftime(self.TIME_FORMAT)
            self.collection = database[trial_name]
        except Exception as error:
            print('--> ERROR: ' + str(error))
    
    ## Store to Mongo(DICT) --> _ID
    def store(self, request, response):
        print('[Storing to Mongo]')
        try:
            doc = {
                'request': request,
                'response':response
            }
            _id = self.collection.insert(doc)
            print _id
            return _id
        except Exception as error:
            print('--> ERROR: ' + str(error))
            return None
        
    ## Get Request() --> DICT
    def receive_request(self):
        print('[Receiving Request]')
        try:
            request = json.loads(self.socket.recv())
            print json.dumps(request, sort_keys=True, indent=4)
            return request
        except Exception as error:
            print('--> ERROR: ' + str(error))
            return None
    
    ## Send Response(DICT) --> DICT
    def send_response(self, response):
        print('[Sending Response]')
        try:
            dump = json.dumps(response, sort_keys=True, indent=4)
            print dump
            result = self.socket.send(dump)
            return result
        except Exception as error:
            print('--> ERROR: ' + str(error))
            return None
    
    ## Handle Request(DICT) --> DICT
    def handle_request(self, request):
        if request['class'] == 'action':
            response = self.determine_action(request)
        elif request['class'] == 'status':
            response = self.determine_status(request)
        else:
            response = None
        return response
    
    ## Determine action(DICT) --> DICT
    def determine_action(self,request):
        """
        This is where the Mapper comes into the picture
        """
        response = {
            'type':'response',
            'class':'action',
            'action':{
                'primary':222,
                'secondary':323
            }
        }
        return response
    
    ## Determine Status(DICT) --> DICT
    def determine_status(self, request):
        """
        This is where the Mapper comes into the picture
        """
        response = {
            'type':'response',
            'class':'status',
            'status':{
                'position': [0,0],
                'orientation': 0,
                'time': time.time()
            }
        }
        return response
        
    ## Listen
    def listen(self):
        request = self.receive_request()
        response = self.handle_request(request)
        result = self.send_response(response)
        self.store(request, response)

    ## Render Index
    @cherrypy.expose
    def index(self, post=None):
        post = cherrypy.request.body.params
        print post
        html = open('static/index.html').read()
        return html 
        
    ## Handle Posts
    @cherrypy.expose
    def default(self,*args,**kwargs):
        print 'YAY'
        return "It works!"

if __name__ == '__main__':
    root = Host(CONFIG)
    cherrypy.server.socket_host = root.CHERRYPY_ADDR
    cherrypy.server.socket_port = root.CHERRYPY_PORT
    currdir = os.path.dirname(os.path.abspath(__file__))
    conf = {
        '/': {'tools.staticdir.on':True, 'tools.staticdir.dir':os.path.join(currdir,'static')},
    }
    cherrypy.quickstart(root, '/', config=conf)
