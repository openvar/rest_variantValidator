# Import modules
from flask import Flask, request
from rest_VariantValidator.endpoints import api
from flask_cors import CORS
from rest_VariantValidator.utils import exceptions, request_parser, representations
from logging import handlers
import time
import os
from pathlib import Path
import logging.config
from configparser import ConfigParser
from VariantValidator import settings as vv_settings
from rest_VariantValidator.utils.limiter import limiter
from werkzeug.exceptions import InternalServerError, Forbidden, TooManyRequests

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
    console_level = config['logging']['console'].upper()
    log_console_level = logging.getLevelName(console_level)
    logger.setLevel(log_console_level)

    try:
        parent = config['logging']['file_path']
    except KeyError:
        pass
    logHandler = handlers.RotatingFileHandler(str(parent) + '/rest_VariantValidator.log',
                                              maxBytes=500000,
                                              backupCount=2)

    file_level = config['logging']['file'].upper()
    log_file_level = logging.getLevelName(file_level)
    logHandler.setLevel(log_file_level)
    logger.addHandler(logHandler)

"""
Create a parser object locally
"""
parser = request_parser.parser

# Define the application as a Flask app with the name defined by __name__
application = Flask(__name__)

# Create a limiter instance and attach it to your Flask application
limiter.init_app(application)
api.init_app(application)

# By default, show all endpoints (collapsed)
application.config.SWAGGER_UI_DOC_EXPANSION = 'list'

# enable CORS
CORS(application, resources={r'/*': {'origins': '*'}})

"""
Representations
"""
@api.representation('text/xml')
def application_xml(data, code, headers):
    resp = representations.xml(data, code, headers)
    resp.headers['Content-Type'] = 'text/xml'
    return resp


@api.representation('application/json')
def application_json(data, code, headers):
    resp = representations.application_json(data, code, headers)
    resp.headers['Content-Type'] = 'application/json'
    return resp

"""
Error handlers
"""


def log_exception(exception_type):
    params = dict(request.args)
    params['path'] = request.path
    message = '%s occurred at %s with params=%s\n' % (exception_type, time.ctime(), params)
    logger.exception(message, exc_info=True)


@application.errorhandler(exceptions.RemoteConnectionError)
def remote_connection_error_handler(e):
    log_exception('ApplicationRemoteConnectionError')
    args = parser.parse_args()
    if args['content-type'] != 'text/xml':
        return application_json({'message': str(e)},
                                504,
                                None)
    else:
        return application_xml({'message': str(e)},
                               504,
                               None)


@application.errorhandler(404)
def not_found_error_handler(e):
    log_exception('ApplicationNotFoundError')
    logger.warning(str(e))
    args = parser.parse_args()
    if args['content-type'] != 'text/xml':
        return application_json({'message': 'Requested Endpoint not found: See the documentation at https://rest.variantvalidator.org'},
                                404,
                                None)
    else:
        return application_xml({'message': 'Requested Endpoint not found: See the documentation at https://rest.variantvalidator.org'},
                               404,
                               None)


@application.errorhandler(500)
def internal_server_error_handler(e):
    log_exception('ApplicationInternalServerError')
    args = parser.parse_args()
    if args['content-type'] != 'text/xml':
        return application_json({'message': 'Unhandled error: contact https://variantvalidator.org/contact_admin/'},
                                500,
                                None)
    else:
        return application_xml({'message': 'Unhandled error: contact https://variantvalidator.org/contact_admin/'},
                               500,
                               None)


@application.errorhandler(429)
def too_many_requests_error_handler(e):
    log_exception('ApplicationTooManyRequestsError')
    args = parser.parse_args()
    if args['content-type'] != 'text/xml':
        return application_json({'message': 'Rate limit hit for this endpoint: See the endpoint documentation at https://rest.variantvalidator.org'},
                                429,
                                None)
    else:
        return application_xml({'message': 'Rate limit hit for this endpoint: See the endpoint documentation at https://rest.variantvalidator.org'},
                               429,
                               None)


@application.errorhandler(403)
def forbidden_error_handler(e):
    log_exception('ApplicationForbiddenError')
    args = parser.parse_args()
    if args['content-type'] != 'text/xml':
        return application_json({'message': 'Forbidden: You do not have the necessary permissions.'},
                                403,
                                None)
    else:
        return application_xml({'message': 'Forbidden: You do not have the necessary permissions.'},
                               403,
                               None)


@api.errorhandler(InternalServerError)
def api_internal_server_error_handler(e):
    log_exception('APIInternalServerError')
    args = parser.parse_args()
    if args['content-type'] != 'text/xml':
        return {'message': 'Unhandled error: contact https://variantvalidator.org/contact_admin/'}, 500, {'Content-Type': 'application/json'}
    else:
        return {'message': 'Unhandled error: contact https://variantvalidator.org/contact_admin/'}, 500, {'Content-Type': 'text/xml'}


@api.errorhandler(TooManyRequests)
def api_too_many_requests_error_handler(e):
    log_exception('APITooManyRequestsError')
    args = parser.parse_args()
    if args['content-type'] != 'text/xml':
        return {'message': 'Rate limit hit for this endpoint: See the endpoint documentation at https://rest.variantvalidator.org'}, 429, {'Content-Type': 'application/json'}
    else:
        return {'message': 'Rate limit hit for this endpoint: See the endpoint documentation at https://rest.variantvalidator.org'}, 429, {'Content-Type': 'text/xml'}


@api.errorhandler(Forbidden)
def api_forbidden_error_handler(e):
    log_exception('APIForbiddenError')
    args = parser.parse_args()
    if args['content-type'] != 'text/xml':
        return {'message': 'Forbidden: You do not have the necessary permissions.'}, 403, {'Content-Type': 'application/json'}
    else:
        return {'message': 'Forbidden: You do not have the necessary permissions.'}, 403, {'Content-Type': 'text/xml'}


# Allows app to be run in debug mode
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    application.debug = True
    application.run(host="127.0.0.1", port=port)

# <LICENSE>
# Copyright (C) 2016-2025 VariantValidator Contributors
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
