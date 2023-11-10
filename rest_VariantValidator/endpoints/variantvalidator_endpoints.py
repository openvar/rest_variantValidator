# Import modules
from flask_restx import Namespace, Resource
from rest_VariantValidator.utils import exceptions, request_parser, representations
from rest_VariantValidator.utils.object_pool import vval_object_pool

"""
Create a parser object locally
"""
parser = request_parser.parser

api = Namespace('VariantValidator', description='VariantValidator API Endpoints')


@api.route("/variantvalidator/<string:genome_build>/<string:variant_description>/<string:select_transcripts>")
@api.param("select_transcripts", "***Return all possible transcripts***\n"
                                 ">   all (at latest version for each transcript)\n"
                                 ">   raw (all versions of each transcript)\n"
                                 "\n***Return only 'select' transcripts***\n"
                                 ">   select\n"
                                 ">   mane_select\n"
                                 ">   mane (MANE and MANE Plus Clinical)\n"
                                 ">   refseq_select\n"
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

        vval = vval_object_pool.get_object()

        # Validate using the VariantValidator Python Library
        validate = vval.validate(variant_description, genome_build, select_transcripts)
        vval_object_pool.return_object(vval)

        content = validate.format_as_dict(with_meta=True)

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


@api.route("/tools/gene2transcripts/<string:gene_query>")
@api.param("gene_query", "***HGNC gene symbol or transcript ID***\n"
                         "\nCurrent supported transcript IDs"
                         "\n- RefSeq")
class Gene2transcriptsClass(Resource):
    # Add documentation about the parser
    @api.expect(parser, validate=True)
    def get(self, gene_query):

        vval = vval_object_pool.get_object()

        try:
            content = vval.gene2transcripts(gene_query)
        except ConnectionError:
            message = "Cannot connect to rest.genenames.org, please try again later"
            vval_object_pool.return_object(vval)
            raise exceptions.RemoteConnectionError(message)
        vval_object_pool.return_object(vval)

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


@api.route("/tools/gene2transcripts_v2/<string:gene_query>/<string:limit_transcripts>/<string:transcript_set>/"
           "<string:genome_build>")
@api.param("gene_query", "***HGNC gene symbol, HGNC ID or transcript ID***\n"
                         "\nCurrent supported transcript IDs"
                         "\n- RefSeq or Ensembl""\n"
                                 "\n***Single***\n"
                                 ">   COL1A1\n"
                                 "\n***Multiple***\n"
                                 ">   COL1A1|COL1A2|COL5A1\n")
@api.param("limit_transcripts",  "***Return all possible transcripts***\n"
                                 ">   False\n"
                                 "\n***Single***\n"
                                 ">   NM_000088.4\n"
                                 "\n***Multiple***\n"
                                 ">   NM_000088.4|NM_000088.3\n"
                                 "\n***Limit to select transcripts***\n"
                                 ">    mane_select = MANE Select transcript only\n"
                                 ">    mane = Mane Select and MANE Plus Clinical\n"
                                 ">    select = All transcripts that have been classified as canonical")
@api.param("transcript_set", "***RefSeq or Ensembl***\n"
                             "\nall = all transcripts, refseq = RefSeq only, ensembl = Ensembl only")
@api.param("genome_build", "***GRCh37 or GRCh38***\n"
                           "\nall = all builds, GRCh37 = GRCh37 only, GRCh38 = GRCh38 only")
class Gene2transcriptsV2Class(Resource):
    # Add documentation about the parser
    @api.expect(parser, validate=True)
    def get(self, gene_query, limit_transcripts, transcript_set, genome_build):

        vval = vval_object_pool.get_object()

        if genome_build not in ["GRCh37", "GRCh38"]:
            genome_build = None
        if "False" in limit_transcripts or "false" in limit_transcripts or limit_transcripts is False:
            limit_transcripts = None
        try:
            content = vval.gene2transcripts(gene_query, select_transcripts=limit_transcripts,
                                            transcript_set=transcript_set, genome_build=genome_build,
                                            batch_output=True)
        except ConnectionError:
            message = "Cannot connect to rest.genenames.org, please try again later"
            vval_object_pool.return_object(vval)
            raise exceptions.RemoteConnectionError(message)
        vval_object_pool.return_object(vval)

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

        vval = vval_object_pool.get_object()
        content = vval.hgvs2ref(hgvs_description)
        vval_object_pool.return_object(vval)

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
