"""
Simple rest interface for VariantValidator built using Flask Flask-RESTPlus and Swagger UI
"""

# Import modules
from flask import Flask
from endpoints import api, representations, exceptions, request_parser

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
def xml(data, code, headers):
    resp = representations.xml(data, code, headers)
    return resp


@api.representation('application/json')
def application_json(data, code, headers):
    resp = representations.application_json(data, code, headers)
    return resp


"""
Error handlers
"""

# exceptions has now been imported from utils!


@application.errorhandler(exceptions.RemoteConnectionError)
def remote_connection_error_handler(e):
    # Collect Arguments
    args = parser.parse_args()
    if args['content-type'] != 'application/xml':
        return application_json({'message': str(e)},
                                504,
                                None)
    else:
        return xml({'message': str(e)},
                   504,
                   None)


@application.errorhandler(404)
def not_found_error_handler():
    # Collect Arguments
    args = parser.parse_args()
    if args['content-type'] != 'application/xml':
        return application_json({'message': 'Requested Endpoint not found'},
                                404,
                                None)
    else:
        return xml({'message': 'Requested Endpoint not found'},
                   404,
                   None)


@application.errorhandler(500)
def default_error_handler():
    # Collect Arguments
    args = parser.parse_args()
    if args['content-type'] != 'application/xml':
        return application_json({'message': 'unhandled error: contact https://variantvalidator.org/contact_admin/'},
                                500,
                                None)
    else:
        return xml({'message': 'unhandled error: contact https://variantvalidator.org/contact_admin/'},
                   500,
                   None)


# Allows app to be run in debug mode
if __name__ == '__main__':
    application.debug = True  # Enable debugging mode
    application.run(host="127.0.0.1", port=5000)  # Specify a host and port fot the app
