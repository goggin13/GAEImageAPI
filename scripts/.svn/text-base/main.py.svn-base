# Matt Goggin
# 
# the main handler for this artmkt
# includes bindings for all the URLs
# to their Python class equivalents

# commands to start server and update
# dev_appserver.py /Applications/MAMP/htdocs/artmkt7/trunk/GAEImageAPI
# appcfg.py update /Applications/MAMP/htdocs/artmkt7/trunk/GAEImageAPI

import os
import sys
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import logging

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from uploader import Form
from uploader import UploadHandler

# /_ah/warmup
# simply here to suppress 404's on our dashboard from GAE using this URL
class WarmupHandler(webapp.RequestHandler):
    def get(self):
        logging.info('Warmup Request') 

application = webapp.WSGIApplication(
                                    [
                                     ('/', Form),
                                     ('/upload', UploadHandler),
                                     ('/_ah/warmup',WarmupHandler)
                                    ], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

