#!python

import site
site.addsitedir('/local/python/2.7.12/lib/python2.7/site-packages/')

import os
import sys
import logging
logging.basicConfig(stream=sys.stderr)

# Set path to file
WSGI_ROOT = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, WSGI_ROOT)

# Import app from 1 level above
# parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# os.sys.path.insert(0,parentdir)
# import variantValidator_interactive

# Run the server (if file is called directly by python, server is internal dev server)
if __name__ == '__main__':
    from validator_api import app as application
    application.debug=True
    application.config['PROPAGATE_EXCEPTIONS'] = True
    application.run()
else:
    from validator_api import app as application