# Import modules
from flask_restx import Namespace, Resource
from rest_VariantValidator.utils import request_parser, representations, input_formatting
from rest_VariantValidator.utils.object_pool import simple_variant_formatter_pool
from rest_VariantValidator.utils.limiter import formatter_pool_limit  # <-- blocking limiter decorator
# get login authentication, if needed, or dummy auth if not present
try:
    from VariantValidator_APIs.db_auth.verify_password import auth
except ModuleNotFoundError:
    from rest_VariantValidator.utils.verify_password import auth

"""
Create a parser object locally
"""
parser = request_parser.parser

api = Namespace('VariantFormatter', description='VariantFormatter API Endpoints')


@api.route("/variantformatter/<string:genome_build>/<string:variant_description>/<string:transcript_model>/"
           "<string:select_transcripts>/<string:checkonly>", strict_slashes=False)
@api.doc(description="This endpoint uses a dynamic blocking limiter based on pool availability. "
                     "If all formatter objects are in use, requests will wait for up to 60 seconds.")
@api.param("variant_description", "***Genomic HGVS***\n"
                                  ">   - NC_000017.10:g.48275363C>A\n"
                                  "\n***Pseudo-VCF***\n"
                                  ">   - 17-50198002-C-A\n"
                                  ">   - 17:50198002:C:A\n"
                                  "\n>  *Notes*\n"
                                  ">   - *pVCF, multiple comma separated ALTs are supported*\n"
                                  ">   - *Multiple variants can be submitted, separated by the pipe '|' character*\n"
                                  ">   - *Recommended maximum is 10 variants per submission*")
@api.param("transcript_model", "***Accepted:***\n"
                               ">   - refseq (return data for RefSeq transcript models)\n"
                               ">   - ensembl (return data for Ensembl transcript models)\n"
                               ">   - all")
@api.param("select_transcripts", "***Return all possible transcripts***\n"
                                 ">   None or all (all transcripts at the latest versions)\n"
                                 ">   raw (all transcripts all version)\n"
                                 ">   select (select transcripts)\n"
                                 ">   mane (MANE select transcripts)\n"
                                 ">   mane_select (MANE select and MANE Plus Clinical transcripts)\n"
                                 "\n***Single***\n"
                                 ">   NM_000093.4\n"
                                 "\n***Multiple***\n"
                                 ">   NM_000093.4|NM_001278074.1|NM_000093.3")
@api.param("genome_build", "***Accepted:***\n"
                           ">   - GRCh37\n"
                           ">   - GRCh38")
@api.param("checkonly", "***Accepted:***\n"
                        ">   - True (return ONLY the genomic variant descriptions and not transcript and protein descriptions)\n"
                        ">   - False")
class VariantFormatterClass(Resource):
    # Add documentation about the parser
    @api.expect(parser, validate=True)
    @auth.login_required()
    @formatter_pool_limit()  # <-- new blocking limiter
    def get(self, genome_build, variant_description, transcript_model, select_transcripts, checkonly, user_id=None):
        # Normalize input values
        if transcript_model in ('None', 'none'):
            transcript_model = None
        if select_transcripts in ('None', 'none'):
            select_transcripts = None
        if checkonly in ('False', 'false'):
            checkonly = False
        if checkonly in ('True', 'true'):
            checkonly = True

        # Acquire a formatter from the pool (blocks up to 60s if all are busy)
        simple_formatter = simple_variant_formatter_pool.get()

        # Convert inputs to JSON arrays
        variant_description = input_formatting.format_input(variant_description)
        select_transcripts = input_formatting.format_input(select_transcripts)
        if select_transcripts == '["all"]':
            select_transcripts = "all"
        if select_transcripts == '["raw"]':
            select_transcripts = "raw"

        try:
            content = simple_formatter.format(
                variant_description, genome_build, transcript_model,
                select_transcripts, checkonly
            )
        except TimeoutError:
            return {
                "error": "Server busy — all processing slots are currently in use. Please retry later."
            }, 429
        except Exception as e:
            return {"error": str(e)}, 500
        finally:
            simple_variant_formatter_pool.return_object(simple_formatter)

        # Parse query arguments
        args = parser.parse_args()

        # Return content in requested format
        if args['content-type'] == 'application/json':
            return representations.application_json(content, 200, None)
        elif args['content-type'] == 'text/xml':
            return representations.xml(content, 200, None)
        else:
            return content


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
