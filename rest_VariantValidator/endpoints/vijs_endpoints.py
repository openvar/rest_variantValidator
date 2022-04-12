# Import modules
from flask_restplus import Namespace, Resource
from . import request_parser
from . import representations

# Import variantFormatter
import VariantFormatter
import VariantFormatter.simpleVariantFormatter
import VariantValidator
vval = VariantValidator.Validator()

"""
Create a list containing common warnings which are not errors
"""
my_warnings = [
    "A more recent version of the selected reference sequence",
    "No transcripts found that fully overlap the described variation",
    "is pending therefore changes may be made to the LRG reference sequence",
    "This coding sequence variant description spans at least one intron",
    "RefSeqGene record not available",
    "automapped to equivalent RefSeq record",
    "Protein level variant descriptions are not fully supported",
    "is HGVS compliant and contains a valid reference amino acid description"
]


"""
Create a parser object locally
"""
parser = request_parser.parser

api = Namespace('VariantsInJournals', description='Endpoints to ensure variants submitted to journals are validated')


@api.route("/transcript_descriptions/<string:genome_build>/<string:variant_description>")
@api.param("variant_description", "***HGVS***\n"
                                  ">   - NM_000088.3:c.589G>T\n"
                                  ">   - LRG_1t1:c.589G>T\n"
                                  ">   - *Recommended maximum is 60 variants per submission*\n")
@api.param("genome_build", "***Accepted:***\n"
                           ">   - GRCh37\n"
                           ">   - GRCh38\n"
                           ">   - hg19\n"
                           ">   - hg38")
class VariantValidatorClass(Resource):
    # Add documentation about the parser
    @api.expect(parser, validate=True)
    def get(self, genome_build, variant_description):

        # List the submitted descriptions and the allowed reference sequence types
        description_list = variant_description.split()
        allowed_references = ["NM_",
                              "NR_",
                              "ENST",
                              "NP_",
                              "ENSP",
                              "t",
                              "p"]

        # Check correct variant type (Currently transcript but also accepts Protein
        # even though we do not advertise this
        variant_description_outs = []
        for description in description_list:
            for reference in allowed_references:
                if reference in description:
                    variant_description_outs.append(description)
        variant_description = "|".join(variant_description_outs)

        # Refresh the content
        refreshed_content = {}
        if variant_description == "":
            refreshed_content = {"error": "Unsupported variant type"}
        else:
            # Validate using the VariantValidator Python Library
            validate = vval.validate(variant_description, genome_build, select_transcripts='all', liftover_level=None)
            content = validate.format_as_dict(with_meta=True)

            for k, v in content.items():
                if k == "metadata":
                    refreshed_content[k] = v
                elif k == "flag":
                    continue
                else:
                    refreshed_content[v["submitted_variant"]] = {}
                    refreshed_content[v["submitted_variant"]]['pass'] = False
                    refreshed_content[v["submitted_variant"]]['errors'] = []
                    refreshed_content[v["submitted_variant"]]['correction'] = None

                    # Handle transcript variant inputs
                    if "p." not in v["submitted_variant"]:
                        # Filter the errors/warnings i.e. removing any warnings that are not actual errors
                        # Warnings which are not errors are contained in the my_warnings list
                        error_found = []
                        if v["validation_warnings"] is not []:
                            for warning in v["validation_warnings"]:
                                safe_found = False
                                for safe in my_warnings:
                                    if safe in warning:
                                        safe_found = True
                                        break
                                if safe_found is False:
                                    error_found.append(warning)
                            refreshed_content[v["submitted_variant"]]['errors'] = error_found

                        # Is the input == to the output?
                        if "LRG" not in v["submitted_variant"]:
                            if v["submitted_variant"] == v["hgvs_transcript_variant"]:
                                refreshed_content[v["submitted_variant"]]['pass'] = True
                            else:
                                refreshed_content[v["submitted_variant"]]['correction'] = v["hgvs_transcript_variant"]
                        else:
                            if v["submitted_variant"] == v["hgvs_lrg_transcript_variant"]:
                                refreshed_content[v["submitted_variant"]]['pass'] = True
                            else:
                                refreshed_content[v["submitted_variant"]]['correction'] = v["hgvs_lrg_transcript"
                                                                                            "_variant"]

                    else:
                        # Filter the errors/warnings i.e. removing any warnings that are not actual errors
                        # Warnings which are not errors are contained in the my_warnings list
                        error_found = []
                        if v["validation_warnings"] is not []:
                            for warning in v["validation_warnings"]:
                                safe_found = False
                                for safe in my_warnings:
                                    if safe in warning:
                                        safe_found = True
                                        break
                                if safe_found is False:
                                    error_found.append(warning)
                            refreshed_content[v["submitted_variant"]]['errors'] = error_found

                        # Is the input == to the output?
                        if "LRG" not in v["submitted_variant"]:
                            if v["submitted_variant"] == v["hgvs_predicted_protein_consequence"]["tlr"]:
                                refreshed_content[v["submitted_variant"]]['pass'] = True
                            elif v["submitted_variant"] == v["hgvs_predicted_protein_consequence"]["slr"]:
                                refreshed_content[v["submitted_variant"]]['pass'] = True
                            else:
                                if v["hgvs_predicted_protein_consequence"]["tlr"] != "":
                                    refreshed_content[v["submitted_variant"]]['correction'] = v[
                                        "hgvs_predicted_protein_consequence"]["tlr"]
                                else:
                                    refreshed_content[v["submitted_variant"]]['correction'] = None
                        else:
                            if v["submitted_variant"] == v["hgvs_predicted_protein_consequence"]["lrg_tlr"]:
                                refreshed_content[v["submitted_variant"]]['pass'] = True
                            elif v["submitted_variant"] == v["hgvs_predicted_protein_consequence"]["lrg_slr"]:
                                refreshed_content[v["submitted_variant"]]['pass'] = True
                            else:
                                if v["hgvs_predicted_protein_consequence"]["lrg_tlr"] != "":
                                    refreshed_content[v["submitted_variant"]]['correction'] = v[
                                        "hgvs_predicted_protein_consequence"]["lrg_tlr"]
                                else:
                                    refreshed_content[v["submitted_variant"]]['correction'] = None

        # Collect Arguments
        args = parser.parse_args()

        # Overrides the default response route so that the standard HTML URL can return any specified format
        if args['content-type'] == 'application/json':
            # example: http://127.0.0.1:5000.....bob?content-type=application/json
            return representations.application_json(refreshed_content, 200, None)
        # example: http://127.0.0.1:5000.....?content-type=application/xml
        elif args['content-type'] == 'application/xml':
            return representations.xml(refreshed_content, 200, None)
        else:
            # Return the api default output
            return refreshed_content


@api.route("/genomic_descriptions/<string:genome_build>/<string:variant_description>/")
@api.param("variant_description", "***Genomic HGVS***\n"
                                  ">   - NC_000017.10:g.48275363C>A\n"
                                  ">   - *Recommended maximum is 60 variants per submission*\n")
@api.param("genome_build", "***Accepted:***\n"
                           ">   - GRCh37\n"
                           ">   - GRCh38\n"
                           ">   - hg19\n"
                           ">   - hg38\n")
class LOVDClass(Resource):
    # Add documentation about the parser
    @api.expect(parser, validate=True)
    def get(self, genome_build, variant_description):
        transcript_model = 'all'
        select_transcripts = None
        checkonly = True
        liftover = False

        # List the submitted descriptions and the allowed reference sequence types
        description_list = variant_description.split()
        allowed_references = ["NC_",
                              "NG_"]

        # Check correct variant type (Currently transcript but also accepts Protein
        # even though we do not advertise this
        variant_description_outs = []
        for description in description_list:
            for reference in allowed_references:
                if reference in description:
                    variant_description_outs.append(description)
        variant_description = "|".join(variant_description_outs)

        # Refresh the content
        refreshed_content = {}
        if variant_description is "":
            refreshed_content = {"error": "Unsupported variant type"}
        else:
            # Validate using the VariantValidator Python Library
            content = VariantFormatter.simpleVariantFormatter.format(variant_description,
                                                                     genome_build,
                                                                     transcript_model,
                                                                     select_transcripts,
                                                                     checkonly,
                                                                     liftover)

            for k, v in content.items():
                if k == "metadata":
                    refreshed_content[k] = v
                else:
                    for k2, v2 in v.items():
                        if k2 == "flag" or k2 == "errors":
                            continue

                        # else
                        refreshed_content[k2] = {}
                        refreshed_content[k2]['pass'] = False
                        refreshed_content[k2]['errors'] = []
                        refreshed_content[k2]['correction'] = None

                        # Filter the errors/warnings i.e. removing any warnings that are not actual errors
                        # Warnings which are not errors are contained in the my_warnings list
                        error_found = []
                        if v2["genomic_variant_error"] is not None:
                            safe_found = False
                            for safe in my_warnings:
                                if safe in v2["genomic_variant_error"]:
                                    safe_found = True
                                    break
                            if safe_found is False:
                                    error_found.append(v2["genomic_variant_error"])
                            refreshed_content[k2]['errors'] = error_found

                        # Populate the rest of the output
                        if k2 == v2["g_hgvs"]:
                            refreshed_content[k2]["pass"] = True
                        else:
                            refreshed_content[k2]["correction"] = v2["g_hgvs"]

        # Collect Arguments
        args = parser.parse_args()

        # Overrides the default response route so that the standard HTML URL can return any specified format
        if args['content-type'] == 'application/json':
            # example: http://127.0.0.1:5000.....bob?content-type=application/json
            return representations.application_json(refreshed_content, 200, None)
        # example: http://127.0.0.1:5000.....?content-type=application/xml
        elif args['content-type'] == 'application/xml':
            return representations.xml(refreshed_content, 200, None)
        else:
            # Return the api default output
            return refreshed_content


# <LICENSE>
# Copyright (C) 2016-2022 VariantValidator Contributors
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
