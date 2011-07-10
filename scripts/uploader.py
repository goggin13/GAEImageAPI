#
# Matt Goggin
#
# front end forms and functions for uploading, deleting both images and themes
#

import urllib
import os
import sys
import functions
import logging
from google.appengine.api import images
from google.appengine.ext import webapp
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import blobstore
from google.appengine.ext import db
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from models import ImageURL

MIN_IMAGE_WIDTH = 250
MIN_IMAGE_HEIGHT = 250

# /upload?msg=MSG&class=CLASS&alt_root=ALT_ROOT&url=url
# Main form for uploading images; this can be visited from a browser as is, but in artmkt
# it is piped in via drupal at artmkt.com.  The ALT_ROOT variable tells the form where to redirect
# to on submission.  Msg displays with the form, assigned the class CLASS
class Form(webapp.RequestHandler):  
    def get(self):

        msg = self.request.get('msg')
        url = self.request.get('url') if self.request.get('url') else ''
        msg_class = self.request.get('msg_class')
        upload_url = blobstore.create_upload_url('/upload')

        template_values = {
            'upload_url': upload_url,
            'msg': msg,
            'msg_class': msg_class,
            'url' : url,
        }
        
        path = os.path.join(os.path.dirname(__file__), '../html/index.html')
        self.response.out.write(template.render(path, template_values)) 

# Form posts to the appengine BlobStore, which redirects to this handler.
# Does the actual insert of the blob into the blobstore, and saves a reference as a 
# BlobImage.  Redirects back to form if image is too small
class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):   
    def post(self):

        if not self.get_uploads('file'):
           msg = 'please select an image to upload'
           path = '?msg=%s&msg_class=%s' % (msg, 'err') 
           self.redirect(path)
           return

        upload_files = self.get_uploads('file')      # 'file' is file upload field in the form
        blob_info = upload_files[0]
        blob_key = blob_info.key()

        #width = functions.getWidth(str(blob_key))
        #height = functions.getHeight(str(blob_key))

        #if height < MIN_IMAGE_HEIGHT or width < MIN_IMAGE_WIDTH:
            #pass
            #msg = 'please ensure your image is at least %d X %d pixels' % (MIN_IMAGE_HEIGHT, MIN_IMAGE_WIDTH)
            #path = '?msg=%s&msg_class=%s' % (msg, 'err')
            #blobstore.delete(blob_key)
            #self.redirect(path)
            #return
        
        url =  images.get_serving_url(blob_key)
        blob_key = str(blob_key)
        img = ImageURL(blob_key=blob_key, url = url)
        img.put()

        self.redirect('/?url=%s' % (url) )


