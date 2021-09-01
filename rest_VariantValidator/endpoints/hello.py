from flask_restplus import Namespace, Resource
from . import request_parser
from . import representations

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
        # example: http://127.0.0.1:5000/name/name/bob?content-type=application/xml
        elif args['content-type'] == 'application/xml':
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


# <LICENSE>
# Copyright (C) 2016-2021 VariantValidator Contributors
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
