# Import modules
import ast
from flask_restx import Namespace, Resource
from rest_VariantValidator.utils import request_parser, representations, input_formatting
from rest_VariantValidator.utils.object_pool import simple_variant_formatter_pool
from rest_VariantValidator.utils.limiter import limiter, fmt_rate  # <- import fmt_rate

# get login authentication, if needed, or dummy auth if not present
try:
    from VariantValidator_APIs.db_auth.verify_password import auth
except ModuleNotFoundError:
    from rest_VariantValidator.utils.verify_password import auth


def ordereddict_to_dict(value):
    for k, v in value.items():
        if isinstance(v, dict):
            value[k] = ordereddict_to_dict(v)
    return dict(value)


"""
Create a parser object locally
"""
parser = request_parser.parser

api = Namespace('LOVD', description='LOVD API Endpoints')


@api.route("/lovd/<string:genome_build>/<string:variant_description>/<string:transcript_model>/"
           "<string:select_transcripts>/<string:checkonly>/<string:liftover>", strict_slashes=False)
@api.doc(description="Recommended: 4 requests/sec to avoid hitting limits; higher rates may be throttled dynamically.")
@api.param("variant_description", "***Genomic HGVS***\n"
                                  ">   - NC_000017.10:g.48275363C>A\n"
                                  "\n***Pseudo-VCF***\n"
                                  ">   - 17-50198002-C-A\n"
                                  ">   - 17:50198002:C:A\n"
                                  "\n>  *Notes*\n"
                                  ">   - *pVCF, multiple comma separated ALTs are supported*\n "
                                  ">   - *Multiple variants can be submitted, separated by the pipe '|' character*\n"
                                  ">   - *Recommended maximum is 10 variants per submission*")
@api.param("transcript_model", "***Accepted:***\n"
                               ">   - refseq\n"
                               ">   - ensembl\n"
                               ">   - all")
@api.param("select_transcripts", "***Return all possible transcripts***\n"
                                 ">   None or all\n"
                                 ">   raw\n"
                                 ">   select\n"
                                 ">   mane\n"
                                 ">   mane_select\n"
                                 "\n***Single***\n"
                                 ">   NM_000093.4\n"
                                 "\n***Multiple***\n"
                                 ">   NM_000093.4|NM_001278074.1|NM_000093.3")
@api.param("genome_build", "***Accepted:***\n"
                           ">   - GRCh37\n"
                           ">   - GRCh38\n"
                           ">   - hg19\n"
                           ">   - hg38")
@api.param("checkonly", "***Accepted:***\n"
                        ">   - True\n"
                        ">   - False\n"
                        ">   - tx")
@api.param("liftover", "***Accepted***\n"
                        ">   - True\n"
                        ">   - primary\n"
                        ">   - False")
class LOVDClass(Resource):
    @api.expect(parser, validate=True)
    @auth.login_required()
    @limiter.limit(fmt_rate)  # <- dynamic rate limiter
    def get(self, genome_build, variant_description, transcript_model, select_transcripts, checkonly, liftover, user_id=None):

        # Normalise incoming values
        if transcript_model.lower() == 'none':
            transcript_model = None
        if select_transcripts.lower() == 'none':
            select_transcripts = None

        # checkonly supports True/False/tx
        if checkonly.lower() == 'false':
            checkonly = False
        elif checkonly.lower() == 'true':
            checkonly = True
        # 'tx' passes through unchanged

        # liftover supports True/False/"primary"
        if liftover.lower() == 'true':
            liftover = True
        elif liftover.lower() == 'false':
            liftover = False
        # 'primary' passes through unchanged

        # Get formatter instance from pool
        simple_formatter = simple_variant_formatter_pool.get()

        try:
            # Convert multi-value inputs
            variant_description = input_formatting.format_input(variant_description)
            select_transcripts = input_formatting.format_input(select_transcripts)

            # Escape single-value lists
            if select_transcripts == '["all"]':
                select_transcripts = "all"
            if select_transcripts == '["raw"]':
                select_transcripts = "raw"
            if select_transcripts == '["mane"]':
                select_transcripts = "mane"
            if select_transcripts == '["mane_select"]':
                select_transcripts = "mane_select"

            # Format via pool object
            content = simple_formatter.format(
                variant_description,
                genome_build,
                transcript_model,
                select_transcripts,
                checkonly,
                liftover
            )

        except Exception as e:
            return {"error": str(e)}, 500

        finally:
            simple_variant_formatter_pool.return_object(simple_formatter)

        # Convert ordered dict → plain dict
        to_dict = ordereddict_to_dict(content)

        # Fix quotes via ast (this matches your existing behaviour)
        content = str(to_dict).replace("'", '"')
        content = ast.literal_eval(content)

        # Collect Arguments
        args = parser.parse_args()

        # Return in requested format
        if args['content-type'] == 'application/json':
            return representations.application_json(content, 200, None)

        elif args['content-type'] == 'text/xml':
            return representations.xml(str(content), 200, None)

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
