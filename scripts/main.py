# Matt Goggin
# 
# the main handler for this artmkt
# includes bindings for all the URLs
# to their Python class equivalents

# commands to start server and update
# dev_appserver.py /Applications/MAMP/htdocs/artmkt/GAEImageAPI
# appcfg.py update /Applications/MAMP/htdocs/artmkt/GAEImageAPI

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import logging

import os
import sys
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from uploader import Form
from uploader import UploadHandler
from uploader import UpdateTheme
from uploader import Delete
from server import ServeHandler
from server import ServeThemed
from api import API
from api import Test
from api import Themes
from api import FlushCache
from api import SendMail

# /_ah/warmup
# simply here to suppress 404's on our dashboard from GAE using this URL
class WarmupHandler(webapp.RequestHandler):
    def get(self):
        logging.info('Warmup Request') 

application = webapp.WSGIApplication(
                                    [
                                     ('/', Form),
                                     ('/upload', UploadHandler),
                                     ('/update_theme', UpdateTheme),
                                     ('/serve/([^/]+)?', ServeHandler),
                                     ('/serve_themed', ServeThemed),
                                     ('/delete',Delete),
                                     ('/API', API),
                                     ('/test',Test),
                                     ('/themes',Themes),
                                     ('/flush_cache',FlushCache),
                                     ('/send_mail',SendMail),
                                     ('/_ah/warmup',WarmupHandler)
                                    ], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

