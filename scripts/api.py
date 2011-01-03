#
# Matt Goggin
#
# The classes are utility functions accessable via HTTP to perform various tasks
#

import os
from google.appengine.ext.webapp import template
from google.appengine.api import mail
from models import ImageTheme
from models import ImageThemeCache
from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.ext import db
import functions

# /flush_cache?theme=label
# flush out all these themes from the datastore cache table,
# and empty out memcache (since we don't know which images in there have
# the dirty theme)
class FlushCache(webapp.RequestHandler):
    def get(self):
        theme_label = self.request.get('theme')
        functions.flushCacheLabel(theme_label)
        self.response.out.write('caches cleared')

# /API
# display the API docs
class API(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), '../html/api.html')
        self.response.out.write(template.render(path,{})) 

# /themes
# display the existing themes
class Themes(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), '../html/themes.html')
        self.response.out.write(template.render(path,{ 'themes' : ImageTheme.all() })) 

# /send_mail
# pings an address with an email (used from automated unit tests for reporting emergencies)
class SendMail(webapp.RequestHandler):
    def get(self):
        msg = self.request.get('msg')
        subject = self.request.get('subject')
        mail.send_mail(sender = "GAEImageAPI <goggin13@gmail.com>",
                       to      = "Matt Goggin <goggin13@gmail.com>",
                       subject = subject,
                       body    = msg) 
       
        self.response.out.write('mail sent') 

# /test
# display unit tests.  The unit tests simply throw some different themes at these
# images, which run a variety of sizes and dimensions.  If there are no broken images
# on the test page then nothing (obvious) is wrong
class Test(webapp.RequestHandler):
    def get(self):
        
        img_ids = [{'id':'agcyMTM0MTI1chELEglCbG9iSW1hZ2UYtKIZDA', 
                    'size': 44,
                    'dims': '450x438',
                    },
                    {'id':'agcyMTM0MTI1chELEglCbG9iSW1hZ2UY7bwYDA', 
                    'size': 136,
                    'dims': '1024x768',
                    },
                    {'id':'agcyMTM0MTI1chELEglCbG9iSW1hZ2UYjdkZDA', 
                    'size': 4400,
                    'dims': '4000x3000',
                    },
                    {'id':'agcyMTM0MTI1chELEglCbG9iSW1hZ2UYjeIWDA', 
                    'size': 1100,
                    'dims': '2270x1704',
                    },
                    {'id':'agcyMTM0MTI1chELEglCbG9iSW1hZ2UY8t0aDA', 
                    'size': 252,
                    'dims': '600x900',
                    }
                   ]
        test_themes = ['default','small_square','medium_square','large_square',
                        'thin_x_strip', 'thin_y_strip']

        template_values = {
            'test_images' : img_ids,
            'test_themes' : test_themes
        }

        path = os.path.join(os.path.dirname(__file__), '../html/test.html')
        self.response.out.write(template.render(path,template_values)) 