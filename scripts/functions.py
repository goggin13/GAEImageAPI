#
# Matt Goggin
#
# utility functions for flushing the cache and resizing images
#


from google.appengine.api import images
import logging
from models import ImageThemeCache
from google.appengine.ext import db
from google.appengine.api import memcache

# flush all themes that match theme_key from datastore cache
# flush all of memcache
# if argument is omitted flush everything
def flushCacheLabel(theme_key=None):
    
    if theme_key:
        q = db.GqlQuery("SELECT __key__ FROM ImageThemeCache WHERE theme_key = :1", theme_key)
    else:
        q = ImageThemeCache.all()
    
    results = q.fetch(100)
    db.delete(results)

    memcache.flush_all()


# flush all images that match image_key from datastore cache
# flush all of memcache
def flushCacheImage(image_key):
    
    if not image_key:
	    return
    q = db.GqlQuery("SELECT __key__ FROM ImageThemeCache WHERE image_key = :1", image_key)
    results = q.fetch(100)
    db.delete(results)
    memcache.flush_all()

# makes an image from blob_key, and finds the width
def getWidth(blob_key, strip_size=0.01): 
    im = images.Image(blob_key=blob_key)
    im.crop(0.0,0.0,1.0,strip_size) 
    im_strip = images.Image(image_data=im.execute_transforms()) 
    return im_strip.width 

# makes an image from blob_key, and finds the height
def getHeight(blob_key, strip_size=0.01): 
    im = images.Image(blob_key=blob_key)
    im.crop(0.0,0.0,strip_size,1.0) 
    im_strip = images.Image(image_data=im.execute_transforms()) 
    return im_strip.height 

# Resize then optionally crop a given image.
#    blob_key: key for the data to be retrieved
#    width: The desired width
#    height: The desired height
#    halign: Acts like photoshop's 'Canvas Size' function, horizontally
#            aligning the crop to left, middle or right
#    valign: Verticallly aligns the crop to top, middle or bottom
#
# this function is adapted from a post on StackOverflow at
# http://stackoverflow.com/questions/1944112/app-engine-cropping-to-a-specific-width-and-height
def rescale(blob_key, width, height, halign='middle', valign='middle'):

    image = images.Image(blob_key=blob_key)
    
    imageHeight = getHeight(blob_key)
    imageWidth = getWidth(blob_key)
    
    desired_wh_ratio = float(width) / float(height)
    wh_ratio = float(imageWidth) / float(imageHeight)

    if desired_wh_ratio > wh_ratio:
        image.resize(width=width)               # resize to width, then crop to height
        newHeight = width / wh_ratio
        trim_y = max((float(newHeight - height) / 2) / newHeight,0.0)
        if valign == 'top':
            image.crop(0.0, 0.0, 1.0, 1 - (2 * trim_y))
        elif valign == 'bottom':
            image.crop(0.0, (2 * trim_y), 1.0, 1.0)
        else:
            logging.debug(str(trim_y) + ' = trim_y')

            image.crop(0.0, trim_y, 1.0, 1 - trim_y)
    else:
        image.resize(height=height)              # resize to height, then crop to width
        newWidth = wh_ratio * height
        trim_x = max((float(newWidth - width) / 2) / newWidth,0.0)
        if halign == 'left':
            image.crop(0.0, 0.0, 1 - (2 * trim_x), 1.0)
        elif halign == 'right':
            image.crop((2 * trim_x), 0.0, 1.0, 1.0)
        else:
            image.crop(trim_x, 0.0, 1 - trim_x, 1.0)
    
    image.im_feeling_lucky()
    return image.execute_transforms()
