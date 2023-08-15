"""
Simple rest interface for VariantVlidator built using Flask Flask-RESTPlus and Swagger UI
"""

# Import modules
from flask import Flask, make_response, request
from flask_restplus import Api, Resource, reqparse, fields, abort
import requests
from requests.exceptions import ConnectionError
from dicttoxml import dicttoxml

"""
Logging
"""
import logging
import logging.handlers as handlers
import time

logger = logging.getLogger('rest_api')
# We are setting 2 types of logging. To screen at the level DEBUG
logger.setLevel(logging.INFO)

# We will also log to a file
# Log with a rotating file-handler. This sets the maximum size of the log to 0.5Mb and allows two additional logs
# The logs are then deleted and replaced in rotation
logHandler = handlers.RotatingFileHandler('rest_api.log', maxBytes=500000, backupCount=2)
# We want to minimise the amount of information we log to capturing bugs
logHandler.setLevel(logging.ERROR)
logger.addHandler(logHandler)

# Define the application as a Flask app with the name defined by __name__ (i.e. the name of the current module)
# Most tutorials define application as "app", but I have had issues with this when it comes to deployment,
# so application is recommended
application = Flask(__name__)

# Define the API as api
api = Api(app = application)

# Create a RequestParser object to identify specific content-type requests in HTTP URLs
# The requestparser allows us to specify arguements passed via a URL, in this case, ....?content-type=application/json
parser = reqparse.RequestParser()
parser.add_argument('content-type',
                    type=str,
                    help='Accepted:\n- application/json\n- text/xml')

"""
Register custom exceptions
"""
class RemoteConnectionError(Exception):
    code=504

"""
Representations
 - Adds a response-type into the "Response content type" drop-down menu displayed in Swagger
 - When selected, the APP will return the correct response-header and content type
 - The default for flask-restplus is aspplication/json
"""
# Add additional representations using the @api.representation decorator
# Requires the module make_response from flask and dicttoxml
@api.representation('text/xml')
def xml(data, code, headers):
    data = dicttoxml(data)
    resp = make_response(data, code)
    resp.headers['Content-Type'] = 'text/xml'
    return resp

@api.representation('application/json')
def json(data, code, headers):
    resp = make_response(data, code)
    resp.headers['Content-Type'] = 'application/json'
    return resp

# Define a name-space to be read Swagger UI which is built in to Flask-RESTPlus
# The first variable is the path of the namespace the second variable describes the space
hello_space = api.namespace('hello', description='Simple API that returns a greeting')
@hello_space.route("/")

class HelloClass(Resource):

    # Add documentation about the parser
    @api.doc(parser=parser)
    def get(self):

        # Collect Arguements
        args = parser.parse_args()

        # Overides the default response route so that the standard HTML URL can return any specified format
        if args['content-type'] == 'application/json':
            # example: http://127.0.0.1:5000/name/name/bob?content-type=application/json
            return json({
                "greeting" : "Hello World"
            },
                200, None)
        # example: http://127.0.0.1:5000/name/name/bob?content-type=text/xml
        elif args['content-type'] == 'text/xml':
            return xml({
                 "greeting" : "Hello World"
            },
                200, None)
        else:
            # Return the api default output
            return {
                 "greeting" : "Hello World"
            }

name_space = api.namespace('name', description='Return a name provided by the user')
@name_space.route("/<string:name>")
class NameClass(Resource):


    # Add documentation about the parser
    @api.doc(parser=parser)
    def get(self, name):

        # Collect Arguements
        args = parser.parse_args()

        # Overides the default response route so that the standard HTML URL can return any specified format
        if args['content-type'] == 'application/json':
            # example: http://127.0.0.1:5000/name/name/bob?content-type=application/json
            return json({
                "My name is" : name
            },
                200, None)
        # example: http://127.0.0.1:5000/name/name/bob?content-type=text/xml
        elif args['content-type'] == 'text/xml':
            return xml({
                "My name is": name
            },
                200, None)
        else:
            # Return the api default output
            return {
                "My name is" : name
            }

vv_space = api.namespace('VariantValidator', description='VariantValidator APIs')
@vv_space.route("/variantvalidator/<string:genome_build>/<string:variant_description>/<string:select_transcripts>")
class VariantValidatorClass(Resource):

    # Add documentation about the parser
    @api.doc(parser=parser)
    def get(self, genome_build, variant_description, select_transcripts):

        # Make a request to the curent VariantValidator rest-API
        url = '/'.join(['http://rest.variantvalidator.org/variantvalidator', genome_build, variant_description, select_transcripts])

        # Likley error source, Test be switching off internet connection!
        try:
            validation = requests.get(url)
        except ConnectionError:
            raise RemoteConnectionError('https://rest.variantvalidator.org/variantvalidator currently unavailable')
        content = validation.json()

        # Collect Arguements
        args = parser.parse_args()

        # Overides the default response route so that the standard HTML URL can return any specified format
        if args['content-type'] == 'application/json':
            # example: http://127.0.0.1:5000.....bob?content-type=application/json
            return json(content, 200, None)
        # example: http://127.0.0.1:5000.....?content-type=text/xml
        elif args['content-type'] == 'text/xml':
            return xml(content, 200, None)
        else:
            # Return the api default output
            return content


"""
Error handlers
"""
# Simple function that creates an error message that we will log
def log_exception(type):
    # We want to know the arguments passed and the path so we can replicate the error
    params = dict(request.args)
    params['path'] = request.path
    # Create the message and log
    message = '%s occurred at %s with params=%s' % (type, time.ctime(), params)
    logger.exception(message, exc_info=True)


@application.errorhandler(RemoteConnectionError)
def remote_connection_error_handler(e):
    # Add the Exception to the log ensuring that exc_info is True so that a traceback is also logged
    log_exception('RemoteConnectionError')

    # Collect Arguments
    args = parser.parse_args()
    if args['content-type'] != 'text/xml':
        return json({'message': str(e)},
                                504,
                                None)
    else:
        return xml({'message': str(e)},
                   504,
                   None)


@application.errorhandler(404)
def not_found_error_handler(e):
    # Collect Arguments
    args = parser.parse_args()
    if args['content-type'] != 'text/xml':
        return json({'message': 'Requested Endpoint not found'},
                                404,
                                None)
    else:
        return xml({'message': 'Requested Endpoint not found'},
                   404,
                   None)


@application.errorhandler(500)
def default_error_handler(e):
    # Add the Exception to the log ensuring that exc_info is True so that a traceback is also logged
    log_exception('RemoteConnectionError')

    # Collect Arguments
    args = parser.parse_args()
    if args['content-type'] != 'text/xml':
        return json({'message': 'unhandled error: contact https://variantvalidator.org/contact_admin/'},
                                500,
                                None)
    else:
        return xml({'message': 'unhandled error: contact https://variantvalidator.org/contact_admin/'},
                   500,
                   None)


# Allows app to be run in debug mode
if __name__ == '__main__':
    application.debug = True # Enable debugging mode
    application.run(host="127.0.0.1", port=5000) # Specify a host and port fot the app