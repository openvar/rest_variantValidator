# Import modules
from flask import make_response
from dicttoxml import dicttoxml

"""
Representations
 - Adds a response-type into the "Response content type" drop-down menu displayed in Swagger
 - When selected, the APP will return the correct response-header and content type
 - The default for flask-RESTPlus is application/json

Note
 - These will only be used by namespaces so are undecorated. Decorated versions will appear in app.py
"""


def xml(data, code, headers):
    data = dicttoxml(data)
    resp = make_response(data, code)
    resp.headers['Content-Type'] = 'application/xml'
    return resp


def application_json(data, code, headers):
    resp = make_response(data, code)
    resp.headers['Content-Type'] = 'application/json'
    return resp

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
