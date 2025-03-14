from flask_restx import reqparse

# Custom boolean conversion function
def str_to_bool(value):
    if isinstance(value, bool):
        return value
    if value.lower() in ['true', '1', 't', 'yes', 'y']:
        return True
    elif value.lower() in ['false', '0', 'f', 'no', 'n']:
        return False
    else:
        raise ValueError('Boolean value expected.')

# Create a RequestParser object to identify specific content-type requests in HTTP URLs
parser = reqparse.RequestParser()
parser.add_argument('content-type',
                    type=str,
                    help='***Select the response format***',
                    choices=['application/json', 'text/xml'])
parser.add_argument('show_exon_info',
                    type=str_to_bool,
                    help='***Show Exon structures and alignment data***',
                    choices=[True, False])


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
