"""
Simple rest interface for VariantVlidator built using Flask Flask-RESTPlus and Swagger UI
"""

# Import modules
from flask import Flask
from flask_restplus import Api, Resource

# Define the application as a Flask app with the name defined by __name__ (i.e. the name of the current module)
# Most tutorials define application as "app", but I have had issues with this when it comes to deployment,
# so application is recommended
application = Flask(__name__)

# Define the API as api
api = Api(app = application)

# Define a name-space to be read Swagger UI which is built in to Flask-RESTPlus
# The first variable is the path of the namespace the second variable describes the space
hello_space = api.namespace('hello', description='Simple API that returns a greeting')
@hello_space.route("/")
class HelloClass(Resource):
	def get(self):
		return {
			"greeting": "Hello World"
		}


# Allows app to be run in debug mode
if __name__ == '__main__':
	application.debug = True # Enable debugging mode
	application.run(host="127.0.0.1", port=5000) # Specify a host and port fot the app