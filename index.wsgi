#!/local/python/2.7.12/bin/python

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
import rest_variantValidator
import rest_variantValidator.validator_api
from rest_variantValidator.validator_api import app as application
