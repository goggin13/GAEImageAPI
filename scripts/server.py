#
# Matt Goggin
#
# Classes to serve images, most especially ServeThemed, which serves themed images from the
# datastore
#

import urllib
from google.appengine.ext import webapp
from google.appengine.ext import blobstore
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext.webapp import blobstore_handlers
from models import BlobImage
from models import ImageTheme
import functions
import logging
from datetime import datetime,timedelta
from models import ImageThemeCache

# /serve/([^/]+)?
# serves a raw blob based on the key passed
class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)

# /serve_themed?image_id=ID&theme=LABEL
# serves the image image_id using theme LABEL
class ServeThemed(blobstore_handlers.BlobstoreDownloadHandler):

    # sets the L1 cache and writes the image data
    def serveJPEG(self,img_data,cache_key): 
        self.setCacheL1(cache_key,img_data)
        self.response.headers['Content-Type']   = 'image/jpeg'
        self.response.headers['Cache-Control']  = 'public; max-age=300'     
        self.response.out.write(img_data)      

    # save data in memcache to cache_key
    def setCacheL1(self,cache_key,data):
        logging.debug('setting L1 cache %s ' % cache_key)
        memcache.set(cache_key,data)
    
    # saves data in datastore as ImageThemeCache
    def setCacheL2(self, image_key, theme_key, image_data):
        itc = ImageThemeCache(theme_key = theme_key,
                              image_key = image_key,
                              image_data = image_data)
        itc.put()
        cache_key = image_key+theme_key
        self.setCacheL1(cache_key,image_data)
    
    # retrieve data from memcache using cache_key
    def getImageFromCacheL1(self, cache_key):
        logging.debug('requesting memcache key %s ' % cache_key)
        return memcache.get(cache_key)
      
    # check ImageThemeCache for image_key, theme_key  
    def getImageFromCacheL2(self, image_key, theme_key):
        logging.debug('requesting datastore cache keys %s, %s ' % (image_key, theme_key) )
        q = ImageThemeCache.all().filter('theme_key = ', theme_key).filter('image_key = ', image_key).get()
        return q.image_data if q else None

    # serve the image image_key, sized according to theme theme_label
    def ServeImage(self, image_key,theme_label):
 
        theme = ImageTheme.all().filter('label = ', theme_label).get()
        if not theme:
           self.response.out.write('no theme entry for ' + theme_label)
           return

        theme_key = str(theme.key())
        cache_key = image_key + theme_key
        
        # try memcache first
        themed = self.getImageFromCacheL1(cache_key)
        if themed:
            logging.debug('served from memcache')
            self.serveJPEG(themed, cache_key)
            return
    
        # no luck in memcache; try to get the resized image from datastore
        themed = self.getImageFromCacheL2(image_key, theme_key)

        if themed:
            logging.debug('served from datastore cache')
            self.serveJPEG(themed, cache_key)
            return
        
        # still no luck; we have to go to the blobstore and do all the work
        # of fetching and resizing
        try:
            blob_image = BlobImage.get(image_key)
        except db.BadKeyError:
            self.response.out.write('no blob found for image_id ' + image_key)
            return
   
        if not blob_image:
           self.response.out.write('no blob found for image_id ' + image_key)
           return

        if theme_label == 'actual':
           self.send_blob(blob_image.blob)
           return

        width = theme.width
        height = theme.height
        blob_key = blob_image.blob.key()

        themed = functions.rescale(str(blob_key),width,height)
        logging.debug('remade from scratch')

        self.setCacheL2(image_key, theme_key, themed)            # save to datastore cache
        
        self.serveJPEG(themed,cache_key)                         # saves to memcache before serving
        
    # pull out the request variables and pass them to ServeImage to locate
    # and serve the image
    def get(self):
        image_id = self.request.get('image_id')
        theme_label = self.request.get('theme') if self.request.get('theme') else 'default'

        if not image_id:
           self.response.out.write('image_id is required')
           return

        self.ServeImage(image_id,theme_label)
           
