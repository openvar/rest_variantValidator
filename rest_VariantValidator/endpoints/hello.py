import time
from flask_restx import Namespace, Resource
from rest_VariantValidator.utils import request_parser, representations, exceptions
from rest_VariantValidator.utils.limiter import limiter, concurrency_limit
from flask import abort
from rest_VariantValidator.utils.object_pool import vval_object_pool

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

        # Import object from vval pool
        vval = vval_object_pool.get_object()

        # Collect Arguments
        args = parser.parse_args()
        config_dict = vval.my_config()
        config_dict['vvseqrepo_db'] = config_dict['vvseqrepo_db'].split('/')[-2]

        # Return object to vval pool
        vval_object_pool.return_object(vval)

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

@api.route('/limit')
class LimitedRateHelllo(Resource):
    @limiter.limit("1/second")
    @api.expect(parser, validate=True)
    def get(self):
        return { "status": "not yet hitting the rate limit" }

@api.route('/limit_concurrent')
class LimitedConcurrencyHelllo(Resource):
    @limiter.limit("1/second")
    @concurrency_limit()
    @api.expect(parser, validate=True)
    def get(self):
        time.sleep(2)
        return { "status": "not yet hitting the concurrency limit" }



@api.route('/trigger_error/<int:error_code>')
class ExceptionClass(Resource):
    @api.expect(parser, validate=True)
    def get(self, error_code):
        if error_code == 400:
            abort(400)
        elif error_code == 403:
            abort(403)
        elif error_code == 404:
            abort(404)
        elif error_code == 500:
            abort(500)
        elif error_code == 429:
            abort(429)
        elif error_code == 999:
            raise exceptions.RemoteConnectionError('https://rest.variantvalidator.org/variantvalidator currently '
                                                   'unavailable')


# <LICENSE>
# Copyright (C) 2016-2025 VariantValidator Contributors
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
