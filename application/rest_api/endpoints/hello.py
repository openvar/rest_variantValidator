from flask_restx import Namespace, Resource
from . import request_parser
from . import representations


"""
Create a parser object locally
"""
parser = request_parser.parser


"""
The assignment of api changes
"""

api = Namespace('hello', description='Simple API that returns a greeting')

"""
We also need to re-assign the route ans other decorated functions to api
"""


@api.route("/")
class HelloClass(Resource):

    # Add documentation about the parser
    @api.expect(parser, validate=True)
    def get(self):

        # Collect Arguments
        args = parser.parse_args()

        # Overrides the default response route so that the standard HTML URL can return any specified format
        if args['content-type'] == 'application/json':
            # example: http://127.0.0.1:5000/name/name/bob?content-type=application/json
            return representations.application_json({
                "greeting": "Hello World"
            },
                200, None)
        # example: http://127.0.0.1:5000/name/name/bob?content-type=text/xml
        elif args['content-type'] == 'text/xml':
            return representations.xml({
                 "greeting": "Hello World"
            },
                200, None)
        else:
            # Return the api default output
            return {
                 "greeting": "Hello World"
            }
