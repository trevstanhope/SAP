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
    
    ## Store to Mongo
    def store(self, doc):
        try:
            self.collection.insert(doc)
        except Exception as error:
            print('--> ERROR: ' + str(error))
        
    ## Get Request
    def receive(self):
        print('[Receiving Request]')
        try:
            request = json.loads(self.socket.recv())
            return request
        except Exception as error:
            print('--> ERROR: ' + str(error))
            return None
    
    ## Send Response
    def send(self, response):
        print('[Sending Response]')
        try:
            dump = json.dumps(response)
            result = self.socket.send(dump)
            return result
        except Exception as error:
            print('--> ERROR: ' + str(error))
            return None
    
    ## Handle Request
    def handle_request(self, request):
        if request['class'] == 'action':
            response = self.handle_action(request)
        else:
            return None
    
    ## Handle action
    def handle_action(request):
        return 
        
    ## Listen
    def listen(self):
        ### Get Handle Requests
        request = self.receive_request()
        response = self.handle_request(request)
        result = self.send(response)
        ### Log to Mongo
        self.store(request)
        self.store(response)
        
    ## Render Index
    @cherrypy.expose
    def index(self):
        html = open('static/index.html').read()
        return html        

if __name__ == '__main__':
    root = Host(CONFIG)
    cherrypy.server.socket_host = root.CHERRYPY_ADDR
    cherrypy.server.socket_port = root.CHERRYPY_PORT
    currdir = os.path.dirname(os.path.abspath(__file__))
    conf = {
        '/': {'tools.staticdir.on':True, 'tools.staticdir.dir':os.path.join(currdir,'static')},
    }
    cherrypy.quickstart(root, '/', config=conf)
