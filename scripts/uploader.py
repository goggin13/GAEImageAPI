#
# Matt Goggin
#
# front end forms and functions for uploading, deleting both images and themes
#

from models import BlobImage
import urllib
from google.appengine.ext import webapp
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import memcache
from google.appengine.api import images
import os
import sys
import functions
import logging

from google.appengine.ext import db
from models import ImageTheme

MAX_IMAGE_WIDTH = 800
MAX_IMAGE_HEIGHT = 800

MIN_IMAGE_WIDTH = 250
MIN_IMAGE_HEIGHT = 250

# /upload?msg=MSG&class=CLASS&alt_root=ALT_ROOT
# Main form for uploading images; this can be visited from a browser as is, but in artmkt
# it is piped in via drupal at artmkt.com.  The ALT_ROOT variable tells the form where to redirect
# to on submission.  Msg displays with the form, assigned the class CLASS
class Form(webapp.RequestHandler):  
    def get(self):

        msg = self.request.get('msg')
        msg_class = self.request.get('msg_class')

        alt_root = '&alt_root='+self.request.get('alt_root') if self.request.get('alt_root') else ''
        upload_url = blobstore.create_upload_url('/upload?'+alt_root)

        template_values = {
            'upload_url': upload_url,
            'msg': msg,
            'msg_class': msg_class
        }
        
        path = os.path.join(os.path.dirname(__file__), '../html/index.html')
        self.response.out.write(template.render(path, template_values)) 

# Form posts to the appengine BlobStore, which redirects to this handler.
# Does the actual insert of the blob into the blobstore, and saves a reference as a 
# BlobImage.  Redirects back to form if image is too small
class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):   
    def post(self):
        base_path = self.request.get('alt_root') if self.request.get('alt_root') else ''

        if not self.get_uploads('file'):
           msg = 'please select an image to upload'
           path = '%s?msg=%s&msg_class=%s' % (base_path, msg, 'err') 
           self.redirect(path)
           return

        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        blob_info = upload_files[0]
        blob_key = blob_info.key()

        width = functions.getWidth(str(blob_key))
        height = functions.getHeight(str(blob_key))

        if height < MIN_IMAGE_HEIGHT or width < MIN_IMAGE_WIDTH:
            msg = 'please ensure your image is at least %d X %d pixels' % (MIN_IMAGE_HEIGHT, MIN_IMAGE_WIDTH)
            path = '%s?msg=%s&msg_class=%s' % (base_path, msg, 'err')
            blobstore.delete(blob_key)
            self.redirect(path)
            return

        BI = BlobImage(blob=blob_key)
        BI.put()
        
        self.redirect(base_path + '/delete?show_form=1&image_id='+str(BI.key()))

# /update_theme?label=LABEL&width=xxx&height=yyy
# creates or updatesthe theme with label = LABEL"""
class UpdateTheme(webapp.RequestHandler):
    def get(self):
        label = self.request.get('label')
        height = int(self.request.get('height'))
        width = int(self.request.get('width'))

        if not (label and height and width):
            self.response.out.write('all arguments, label, width, height, are required')
            
        # delete previous labels with this name
        q = db.GqlQuery("SELECT __key__ FROM ImageTheme WHERE label = :1", label)
        results = q.fetch(100)
        db.delete(results)

        theme = ImageTheme(label=label, height=height, width=width)
        theme.put()
        functions.flushCacheLabel(theme.key())
        self.response.out.write('saved theme ' + label + ' ( ' + str(width) + ', ' + str(height) +' ) ')

# /delete?image_id=ID&show_form=1&alt_root=ALT_ROOT
# Same class both shows a form for deletes, and does the actual delete.  if request
# contains show_form=1, then the form is showed.  Otherwise image is actually deleted.
# alt_root is used as above to dictate a redirect as necessary. 
class Delete(webapp.RequestHandler):
    def get(self):
        image_id = self.request.get('image_id')
        base_path = self.request.get('alt_root') if self.request.get('alt_root') else ''
        
        if not image_id:
            self.response.out.write('image_id is a required argument')
            return

        try:
            blob_image = BlobImage.get(image_id)
        except db.BadKeyError:
            msg = 'no results found for image_id %s' % image_id
            alt_root = '&alt_root='+base_path
            path = '?msg=%s&msg_class=%s&image_id=%s%s' % (msg,'err',image_id,alt_root)
            self.response.out.write(msg)
            return

        if self.request.get('show_form'):
            path = os.path.join(os.path.dirname(__file__), '../html/delete.html')
            self.response.out.write(template.render(path, {'image_id' : image_id,
                                                           'alt_root' : base_path})) 
            return

        blob_key = blob_image.blob.key()
        blobstore.delete(blob_key)
        functions.flushCacheImage(str(blob_image.key()))
        blob_image.delete()

        msg = 'successfully deleted image %s' % image_id
        path = '%s?msg=%s&msg_class=%s' % (base_path, msg, 'msg')
        self.redirect(path)

