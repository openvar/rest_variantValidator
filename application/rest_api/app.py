"""
Simple rest interface for VariantValidator built using Flask Flask-RESTPlus and Swagger UI
"""

# Import modules
from flask import Flask
from endpoints import api, representations, exceptions

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


@api.errorhandler
def default_error_handler():
    return {'message': 'unhandled error: contact https://variantvalidator.org/contact_admin/'}, 500


# exceptions has now been imported from utils!
@api.errorhandler(exceptions.RemoteConnectionError)
def remote_connection_error_handler(e):
    return {'message': str(e)}, 500


# Allows app to be run in debug mode


if __name__ == '__main__':
    application.debug = True  # Enable debugging mode
    application.run(host="127.0.0.1", port=5000)  # Specify a host and port fot the app
