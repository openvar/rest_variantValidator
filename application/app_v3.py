"""
Simple rest interface for VariantVlidator built using Flask Flask-RESTPlus and Swagger UI
"""

# Import modules
from flask import Flask, make_response
from flask_restx import Api, Resource, reqparse
import requests
from dicttoxml import dicttoxml

# Define the application as a Flask app with the name defined by __name__ (i.e. the name of the current module)
# Most tutorials define application as "app", but I have had issues with this when it comes to deployment,
# so application is recommended
application = Flask(__name__)

# Define the API as api
api = Api(app = application)

# Define a parser:
parser = reqparse.RequestParser()
parser.add_argument('content-type',
                    type = str,
                    help = 'Accepted:\n- application/json\n- text/xml')

# Add API representations:
# For xml:
@api.representation('text/xml')
def xml(data, code, headers):
    data = dicttoxml(data)
    resp = make_response(data, code)
    resp.headers['Content-Type'] = 'text/xml'
    return resp

# For json:
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
    def get(self):
        return {
            "greeting": "Hello World"
        }


name_space = api.namespace('name', description='Return a name provided by the user')
@name_space.route("/<string:name>")
class NameClass(Resource):
    def get(self, name):
        return {
            "My name is" : name
        }
    
# Exercise 2 part 1:
vv_space = api.namespace('VariantValidator', description='VariantValidator APIs')
@vv_space.route("/variantvalidator/<string:genome_build>/<string:var_desc>/<string:select_transcripts>")
class VariantValidatorClass(Resource):
    
    @api.doc(parser = parser)

    def get(self, genome_build, var_desc, select_transcripts):

        # Make a request to the curent VariantValidator rest-API
        url = f"https://rest.variantvalidator.org/{genome_build}/{var_desc}/{select_transcripts}"
        validation = requests.get(url)
        content = validation.json()
        
        # Collect arguments from the parser:
        args = parser.parse_args()
        
        # If content-type specified - return the content object in that format:
        if args['content-type'] == 'application/json':
            return json(content, 200, None)
        
        elif args['content-type'] == 'text/xml':
            return xml(content, 200, None)
        
        # Return in the default format:
        else:
            return content

# Exercise 2 part 3:


# Allows app to be run in debug mode
if __name__ == '__main__':
    application.debug = True # Enable debugging mode
    application.run(host="127.0.0.1", port=5000) # Specify a host and port fot the app