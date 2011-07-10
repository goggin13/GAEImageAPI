# utility functions for resizing images
#

from google.appengine.api import images

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