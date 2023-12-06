# Import modules
import ast
from flask_restx import Namespace, Resource
from rest_VariantValidator.utils import request_parser, representations, input_formatting
from rest_VariantValidator.utils.object_pool import simple_variant_formatter_pool


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
           "<string:select_transcripts>/<string:checkonly>/<string:liftover>")
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
                               ">   - refseq (return data for RefSeq transcript models)\n"
                               ">   - ensembl (return data for ensembl transcript models)\n"
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
                           ">   - GRCh38\n"
                           ">   - hg19\n"
                           ">   - hg38\n")
@api.param("checkonly", "***Accepted:***\n"
                        ">   - True (return ONLY the genomic variant descriptions and not transcript and protein"
                        " descriptions)\n"
                        ">   - False\n"
                        ">   - tx (Stop at transcript level, exclude protein)")
@api.param("liftover", "***Accepted***\n"
                        ">   - True - (liftover to all genomic loci)\n"
                        ">   - primary - (lift to primary assembly only)\n"
                        ">   - False")
class LOVDClass(Resource):
    # Add documentation about the parser
    @api.expect(parser, validate=True)
    def get(self, genome_build, variant_description, transcript_model, select_transcripts, checkonly, liftover):
        if transcript_model == 'None' or transcript_model == 'none':
            transcript_model = None
        if select_transcripts == 'None' or select_transcripts == 'none':
            select_transcripts = None
        if checkonly == 'False' or checkonly == 'false':
            checkonly = False
        if checkonly == 'True' or checkonly == 'true':
            checkonly = True
        if liftover == 'True' or liftover == 'true':
            liftover = True
        if liftover == 'False' or liftover == 'false':
            liftover = False

        # Import formatter object from pool
        simple_formatter = simple_variant_formatter_pool.get()

        # Convert inputs to JSON arrays
        variant_description = input_formatting.format_input(variant_description)
        select_transcripts = input_formatting.format_input(select_transcripts)

        try:
            content = simple_formatter.format(variant_description, genome_build, transcript_model,
                                              select_transcripts, checkonly, liftover)
        except Exception as e:
            # Handle the exception and customize the error response
            return {"error": str(e)}, 500
        finally:
            simple_variant_formatter_pool.return_object(simple_formatter)

        to_dict = ordereddict_to_dict(content)
        content = str(to_dict)
        content = content.replace("'", '"')
        content = ast.literal_eval(content)

        # Collect Arguments
        args = parser.parse_args()

        # Overrides the default response route so that the standard HTML URL can return any specified format
        if args['content-type'] == 'application/json':
            # example: http://127.0.0.1:5000.....bob?content-type=application/json
            return representations.application_json(content, 200, None)
        # example: http://127.0.0.1:5000.....?content-type=text/xml
        elif args['content-type'] == 'text/xml':
            return representations.xml(str(content), 200, None)
        else:
            # Return the api default output
            return content


# <LICENSE>
# Copyright (C) 2016-2023 VariantValidator Contributors
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
