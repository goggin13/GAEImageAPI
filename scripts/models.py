from google.appengine.ext import db
from google.appengine.ext import blobstore

class ImageURL(db.Model):
    blob_key = db.StringProperty()
    url = db.StringProperty()	