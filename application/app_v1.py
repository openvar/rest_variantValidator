"""
Simple rest interface for VariantVlidator built using Flask Flask-RESTPlus and Swagger UI
"""

# Import modules
from flask import Flask, jsonify
from flask_restplus import Api, Resource

# Define the app as a Flask application with the name defined by __name__ (i.e. the name of the current module)
flask_app = Flask(__name__)
# Most tutorials will call this app, but this causes problems with deployment, so we will call the app application
application = Api(app = flask_app)

# Define a name-space to be read Swagger UI which is built in to Flask-RESTPlus
# The first variable is the path of the namespace the second variable describes the space
name_space = application.namespace('variantvaldator', description='VariantValidator APIs')

@name_space.route("/")
class HelloClass(Resource):
	def get(self):
		return jsonify({
			"greeting": "Hello World"
		})


# Allows app to be run in debug mode
if __name__ == '__main__':
    flask_app.debug = True # Enable debugging mode
    flask_app.config['PROPAGATE_EXCEPTIONS'] = True # Enables the Werkzeug interactive debugging interface
    flask_app.run(host="127.0.0.1", port=5000) # Specify a host and port fot the app