from flask_restplus import Namespace, Resource
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
        # example: http://127.0.0.1:5000/name/name/bob?content-type=application/xml
        elif args['content-type'] == 'application/xml':
            return representations.xml({
                 "greeting": "Hello World"
            },
                200, None)
        else:
            # Return the api default output
            return {
                 "greeting": "Hello World"
            }


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
