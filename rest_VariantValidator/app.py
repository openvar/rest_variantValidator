"""
Simple rest interface for VariantValidator built using Flask Flask-RESTPlus and Swagger UI
"""

# Import modules
from flask import Flask, request
from rest_VariantValidator.endpoints import api, representations, exceptions, request_parser
from logging import handlers
import time
import os
from pathlib import Path
import logging.config
from configparser import ConfigParser
from VariantValidator import settings as vv_settings

# Set document root
ROOT = os.path.dirname(os.path.abspath(__file__))
path = Path(ROOT)
parent = path.parent.absolute()

# Change settings based on config
config = ConfigParser()
config.read(vv_settings.CONFIG_DIR)

"""
Logging
"""
if config['logging'].getboolean('log') is True:
    logger = logging.getLogger('rest_VariantValidator')
    # We are setting 2 types of logging. To screen at the level DEBUG
    console_level = config['logging']['console'].upper()
    log_console_level = logging.getLevelName(console_level)
    logger.setLevel(log_console_level)

    # We will also log to a file
    # Log with a rotating file-handler
    # This sets the maximum size of the log to 0.5Mb and allows two additional logs
    # The logs are then deleted and replaced in rotation
    logHandler = handlers.RotatingFileHandler(str(parent) + '/rest_VariantValidator.log', 
                                              maxBytes=500000, 
                                              backupCount=2)
    # We want to minimise the amount of information we log to capturing bugs
    file_level = config['logging']['file'].upper()
    log_file_level = logging.getLevelName(file_level)
    logHandler.setLevel(log_file_level)
    logger.addHandler(logHandler)

"""
Create a parser object locally
"""
parser = request_parser.parser

# Define the application as a Flask app with the name defined by __name__ (i.e. the name of the current module)
# Most tutorials define application as "app", but I have had issues with this when it comes to deployment,
# so application is recommended
application = Flask(__name__)

api.init_app(application)

# By default, show all endpoints (collapsed)
application.config.SWAGGER_UI_DOC_EXPANSION = 'list'


"""
Representations
 - Adds a response-type into the "Response content type" drop-down menu displayed in Swagger
 - When selected, the APP will return the correct response-header and content type
 - The default for flask-RESTPlus is application/json
 
Note 
 - The decorators are assigned to the functions
"""
# Add additional representations using the @api.representation decorator
# Requires the module make_response from flask and dict-to-xml


@api.representation('application/xml')
def application_xml(data, code, headers):
    resp = representations.xml(data, code, headers)
    resp.headers['Content-Type'] = 'application/xml'
    return resp


@api.representation('application/json')
def application_json(data, code, headers):
    resp = representations.application_json(data, code, headers)
    resp.headers['Content-Type'] = 'application/json'
    return resp


"""
Error handlers
    - exceptions has now been imported from utils!
"""


# Simple function that creates an error message that we will log
def log_exception(exception_type):
    # We want to know the arguments passed and the path so we can replicate the error
    params = dict(request.args)
    params['path'] = request.path
    # Create the message and log
    message = '%s occurred at %s with params=%s' % (exception_type, time.ctime(), params)
    logger.exception(message, exc_info=True)


@application.errorhandler(exceptions.RemoteConnectionError)
def remote_connection_error_handler(e):
    # Add the Exception to the log ensuring that exc_info is True so that a traceback is also logged
    if config['logging'].getboolean('log') is True:
        log_exception('RemoteConnectionError')

    # Collect Arguments
    args = parser.parse_args()
    if args['content-type'] != 'application/xml':
        return application_json({'message': str(e)},
                                504,
                                None)
    else:
        return application_xml({'message': str(e)},
                               504,
                               None)


@application.errorhandler(404)
def not_found_error_handler(e):
    # Add the Exception to the log ensuring that exc_info is True so that a traceback is also logged
    if config['logging'].getboolean('log') is True:
        log_exception('NotFoundError')

    # Collect Arguments
    args = parser.parse_args()
    if args['content-type'] != 'application/xml':
        return application_json({'message': 'Requested Endpoint not found'},
                                404,
                                None)
    else:
        return application_xml({'message': 'Requested Endpoint not found'},
                               404,
                               None)


@application.errorhandler(500)
def default_error_handler(e):
    # Add the Exception to the log ensuring that exc_info is True so that a traceback is also logged
    if config['logging'].getboolean('log') is True:
        log_exception('InternalServerError')

    # Collect Arguments
    args = parser.parse_args()
    if args['content-type'] != 'application/xml':
        return application_json({'message': 'unhandled error: contact https://variantvalidator.org/contact_admin/'},
                                500,
                                None)
    else:
        return application_xml({'message': 'unhandled error: contact https://variantvalidator.org/contact_admin/'},
                               500,
                               None)


# Allows app to be run in debug mode
if __name__ == '__main__':
    application.debug = True  # Enable debugging mode
    application.run(host="127.0.0.1", port=5000)  # Specify a host and port fot the app


# <LICENSE>
# Copyright (C) 2019 VariantValidator Contributors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# </LICENSE>
