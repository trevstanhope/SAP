"""
Host
"""

import json
import zmq
import sys
import os
import cherrypy
from cherrypy.process.plugins import Monitor
from cherrypy import tools
from pymongo import MongoClient

# Constants
try:
    CONFIG = sys.argv[1]
except Exception as err:
    CONFIG = 'settings.json'

class Server:

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
    
    ## Listen
    def listen(self):
        request = self.receive()
        self.send(request)
        
    ## Render Index
    @cherrypy.expose
    def index(self):
        html = open('static/index.html').read()
        return html        

if __name__ == '__main__':
    root = Server(CONFIG)
    cherrypy.server.socket_host = root.CHERRYPY_ADDR
    cherrypy.server.socket_port = root.CHERRYPY_PORT
    currdir = os.path.dirname(os.path.abspath(__file__))
    conf = {
        '/': {'tools.staticdir.on':True, 'tools.staticdir.dir':os.path.join(currdir,'static')},
    }
    cherrypy.quickstart(root, '/', config=conf)
