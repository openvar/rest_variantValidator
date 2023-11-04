from flask_restx import reqparse


# Create a RequestParser object to identify specific content-type requests in HTTP URLs
# The request-parser allows us to specify arguments passed via a URL, in this case, ....?content-type=application/json
parser = reqparse.RequestParser()
parser.add_argument('content-type',
                    type=str,
                    help='***Select the response format***',
                    choices=['application/json', 'text/xml'])
