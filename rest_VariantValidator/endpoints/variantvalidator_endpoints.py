# Import modules
from flask_restplus import Namespace, Resource
from . import request_parser
from . import representations
# import requests
# from requests.exceptions import ConnectionError
# from . import exceptions

# Import VariantValidator  code
import VariantValidator
vval = VariantValidator.Validator()

"""
Create a parser object locally
"""
parser = request_parser.parser

api = Namespace('VariantValidator', description='VariantValidator API Endpoints')


@api.route("/variantvalidator/<string:genome_build>/<string:variant_description>/<string:select_transcripts>")
@api.param("select_transcripts", "***Return all possible transcripts***\n"
                                 ">   all\n"
                                 "\n***Single***\n"
                                 ">   NM_000093.4\n"
                                 "\n***Multiple***\n"
                                 ">   NM_000093.4|NM_001278074.1|NM_000093.3")
@api.param("variant_description", "***HGVS***\n"
                                  ">   - NM_000088.3:c.589G>T\n"
                                  ">   - NC_000017.10:g.48275363C>A\n"
                                  ">   - NG_007400.1:g.8638G>T\n"
                                  ">   - LRG_1:g.8638G>T\n"
                                  ">   - LRG_1t1:c.589G>T\n"
                                  "\n***Pseudo-VCF***\n"
                                  ">   - 17-50198002-C-A\n"
                                  ">   - 17:50198002:C:A\n"
                                  ">   - GRCh38-17-50198002-C-A\n"
                                  ">   - GRCh38:17:50198002:C:A\n"
                                  "\n***Hybrid***\n"
                                  ">   - chr17:50198002C>A\n "
                                  ">   - chr17:50198002C>A(GRCh38)\n"
                                  ">   - chr17(GRCh38):50198002C>A\n"
                                  ">   - chr17:g.50198002C>A\n"
                                  ">   - chr17:g.50198002C>A(GRCh38)\n"
                                  ">   - chr17(GRCh38):g.50198002C>A")
@api.param("genome_build", "***Accepted:***\n"
                           ">   - GRCh37\n"
                           ">   - GRCh38\n"
                           ">   - hg19\n"
                           ">   - hg38")
class VariantValidatorClass(Resource):
    # Add documentation about the parser
    @api.expect(parser, validate=True)
    def get(self, genome_build, variant_description, select_transcripts):

        # Validate using the VariantValidator Python Library
        validate = vval.validate(variant_description, genome_build, select_transcripts)
        content = validate.format_as_dict(with_meta=True)

        # Collect Arguments
        args = parser.parse_args()

        # Overrides the default response route so that the standard HTML URL can return any specified format
        if args['content-type'] == 'application/json':
            # example: http://127.0.0.1:5000.....bob?content-type=application/json
            return representations.application_json(content, 200, None)
        # example: http://127.0.0.1:5000.....?content-type=application/xml
        elif args['content-type'] == 'application/xml':
            return representations.xml(content, 200, None)
        else:
            # Return the api default output
            return content


@api.route("/tools/gene2transcripts/<string:gene_query>")
@api.param("gene_query", "***HGNC gene symbol or transcript ID***\n"
                         "\nCurrent supported transcript IDs"
                         "\n- RefSeq")
class Gene2transcriptsClass(Resource):
    # Add documentation about the parser
    @api.expect(parser, validate=True)
    def get(self, gene_query):
        content = vval.gene2transcripts(gene_query)

        # Collect Arguments
        args = parser.parse_args()

        # Overrides the default response route so that the standard HTML URL can return any specified format
        if args['content-type'] == 'application/json':
            # example: http://127.0.0.1:5000.....bob?content-type=application/json
            return representations.application_json(content, 200, None)
        # example: http://127.0.0.1:5000.....?content-type=application/xml
        elif args['content-type'] == 'application/xml':
            return representations.xml(content, 200, None)
        else:
            # Return the api default output
            return content


@api.route("/tools/hgvs2reference/<string:hgvs_description>")
@api.param("hgvs_description", "***hgvs_description***\n"
                               "\nSequence variation description in the HGVS format\n"
                               "\n *Intronic descriptions in the context of transcript reference sequences are currentl"
                               "y "
                               "unsupported*")
class Hgvs2referenceClass(Resource):
    # Add documentation about the parser
    @api.expect(parser, validate=True)
    def get(self, hgvs_description):
        content = vval.hgvs2ref(hgvs_description)

        # Collect Arguments
        args = parser.parse_args()

        # Overrides the default response route so that the standard HTML URL can return any specified format
        if args['content-type'] == 'application/json':
            # example: http://127.0.0.1:5000.....bob?content-type=application/json
            return representations.application_json(content, 200, None)
        # example: http://127.0.0.1:5000.....?content-type=application/xml
        elif args['content-type'] == 'application/xml':
            return representations.xml(content, 200, None)
        else:
            # Return the api default output
            return content


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
