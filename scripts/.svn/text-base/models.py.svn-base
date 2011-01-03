from google.appengine.ext import db
from google.appengine.ext import blobstore

# just to save references to the images we are storing
class BlobImage(db.Model):
    blob = blobstore.BlobReferenceProperty()

# an image theme dictates a height and width used to display an image
# The label is used during requests to ask for a specific theme
class ImageTheme(db.Model):
    label = db.StringProperty()
    width = db.IntegerProperty()
    height = db.IntegerProperty()

# used to cache resized images so we don't have to resize every time.
# theme_key and image_key are keys from the datastore linking to
# ImageTheme and BlobImage respectively. 
class ImageThemeCache(db.Model):
    theme_key = db.StringProperty()
    image_key = db.StringProperty()
    image_data = db.BlobProperty()