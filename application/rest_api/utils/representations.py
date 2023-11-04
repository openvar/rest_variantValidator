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
    resp.headers['Content-Type'] = 'text/xml'
    return resp


def application_json(data, code, headers):
    resp = make_response(data, code)
    resp.headers['Content-Type'] = 'application/json'
    return resp
