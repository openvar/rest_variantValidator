from flask_restx import Namespace, Resource
from rest_VariantValidator.utils import request_parser, representations, exceptions
from flask import abort

# Import VariantValidator  code
import VariantValidator
vval = VariantValidator.Validator()

"""
Create a parser object locally
"""
parser = request_parser.parser


"""
The assignment of api changes
"""

api = Namespace('hello', description='Endpoint to check services are "alive" and display the current software and '
                                     'database versions')

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
        config_dict = vval.my_config()
        config_dict['vvseqrepo_db'] = config_dict['vvseqrepo_db'].split('/')[-2]

        # Overrides the default response route so that the standard HTML URL can return any specified format
        if args['content-type'] == 'application/json':
            # example: http://127.0.0.1:5000/name/name/bob?content-type=application/json
            return representations.application_json({
                "status": "hello_world",
                "metadata": config_dict
            },
                200, None)
        # example: http://127.0.0.1:5000/name/name/bob?content-type=text/xml
        elif args['content-type'] == 'text/xml':
            return representations.xml({
                 "status": "hello_world",
                 "metadata": config_dict
            },
                200, None)
        else:
            # Return the api default output
            return {
                 "status": "hello_world",
                 "metadata": config_dict
            }


@api.route('/trigger_error/<int:error_code>')
class ExceptionClass(Resource):
    @api.expect(parser, validate=True)
    def get(self, error_code):
        print("WUWUWU")
        print(error_code)
        if error_code == 400:
            abort(400, "Bad Request")
        elif error_code == 403:
            abort(403, "Forbidden")
        elif error_code == 404:
            abort(404, "Not Found")
        elif error_code == 500:
            abort(500, "Internal Server Error")
        elif error_code == 999:
            print("HERE")
            raise exceptions.RemoteConnectionError('https://rest.variantvalidator.org/variantvalidator currently '
                                                   'unavailable')


# <LICENSE>
# Copyright (C) 2016-2023 VariantValidator Contributors
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
