from flask_restx import Namespace, Resource
from . import request_parser
from . import representations
import requests
from requests.exceptions import ConnectionError
from . import exceptions

"""
Create a parser object locally
"""
parser = request_parser.parser

api = Namespace('VariantValidator', description='VariantValidator API Endpoints')


@api.route("/variantvalidator/<string:genome_build>/<string:variant_description>/<string:select_transcripts>")
@api.param("select_transcripts", "***'all'***\n"
                                 ">   Return all possible transcripts\n"
                                 "\n***Single***\n"
                                 ">   NM_000093.4\n"
                                 "\n***Multiple***\n"
                                 ">   NM_000093.4|NM_001278074.1|NM_000093.3")
@api.param("variant_description", "***HGVS***\n"
                                  ">   NM_000088.3:c.589G>T\n"
                                  ">   NC_000017.10:g.48275363C>A\n"
                                  ">   NG_007400.1:g.8638G>T\n"
                                  ">   LRG_1:g.8638G>T\n"
                                  ">   LRG_1t1:c.589G>T\n"
                                  "\n***Pseudo-VCF***\n"
                                  ">   17-50198002-C-A\n"
                                  ">   17:50198002:C:A\n"
                                  ">   GRCh38-17-50198002-C-A\n"
                                  ">   GRCh38:17:50198002:C:A\n"
                                  "\n***Hybrid***\n"
                                  ">   chr17:50198002C>A\n "
                                  ">   chr17:50198002C>A(GRCh38)\n"
                                  ">   chr17:g.50198002C>A\n"
                                  ">   chr17:g.50198002C>A(GRCh38)")
@api.param("genome_build", "***Accepted:***\n"
                           ">   GRCh37\n"
                           ">   GRCh38\n"
                           ">   hg19\n"
                           ">   hg38")
class VariantValidatorClass(Resource):
    # Add documentation about the parser
    @api.expect(parser, validate=True)
    def get(self, genome_build, variant_description, select_transcripts):

        # Make a request to the current VariantValidator rest-API
        url = '/'.join(['https://rest.variantvalidator.org/variantvalidator',
                        genome_build,
                        variant_description,
                        select_transcripts
                        ])
        try:
            validation = requests.get(url)
        except ConnectionError:
            raise exceptions.RemoteConnectionError('https://rest.variantvalidator.org/variantvalidator currently '
                                                   'unavailable')
        content = validation.json()

        # Collect Arguments
        args = parser.parse_args()

        # Overrides the default response route so that the standard HTML URL can return any specified format
        if args['content-type'] == 'application/json':
            # example: http://127.0.0.1:5000.....bob?content-type=application/json
            return representations.application_json(content, 200, None)
        # example: http://127.0.0.1:5000.....?content-type=text/xml
        elif args['content-type'] == 'text/xml':
            return representations.xml(content, 200, None)
        else:
            # Return the api default output
            return content
