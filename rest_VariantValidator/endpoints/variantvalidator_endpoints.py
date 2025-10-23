# Import modules
from flask_restx import Namespace, Resource
from rest_VariantValidator.utils import exceptions, request_parser, representations, input_formatting, request_parser_g2t
from rest_VariantValidator.utils.object_pool import vval_object_pool, g2t_object_pool
from rest_VariantValidator.utils.limiter import vval_pool_limit, g2t_pool_limit  # <-- using new blocking decorators
# get login authentication, if needed, or dummy auth if not present
try:
    from VariantValidator_APIs.db_auth.verify_password import auth
except ModuleNotFoundError:
    from rest_VariantValidator.utils.verify_password import auth

# Create parser objects locally
parser = request_parser.parser
parser_g2t = request_parser_g2t.parser

api = Namespace('VariantValidator', description='VariantValidator API Endpoints')


@api.route("/variantvalidator/<string:genome_build>/<string:variant_description>/<string:select_transcripts>",
           strict_slashes=False)
@api.doc(description="This endpoint uses a dynamic blocking limiter based on pool availability. "
                     "Requests wait up to 60 seconds if all validator objects are in use.")
@api.param("select_transcripts", "***Return all possible transcripts***\n"
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
    @api.expect(parser, validate=True)
    @auth.login_required()
    @vval_pool_limit()  # <-- new blocking limiter
    def get(self, genome_build, variant_description, select_transcripts, user_id=None):
        # Acquire a validator object from the pool (blocks up to 60s if all are busy)
        vval = vval_object_pool.get_object()

        transcript_model = "refseq"

        # Deprecated check for 'all' or 'raw' for genomic variants
        if ("all" in select_transcripts or "raw" in select_transcripts) and "auth" not in select_transcripts:
            if not any(x in variant_description for x in ("c.", "n.", "r.", "p.")):
                return {"Not Found": "Setting select_transcripts to 'all' or 'raw' is deprecated for genomic "
                                     "variant processing using this endpoint. Use the LOVD endpoint for pipelines."}, 404
        elif "auth_all" in select_transcripts:
            select_transcripts = "all"
        elif "auth_raw" in select_transcripts:
            select_transcripts = "raw"

        # Normalise input
        variant_description = input_formatting.format_input(variant_description)
        select_transcripts = input_formatting.format_input(select_transcripts)
        if select_transcripts == '["all"]': select_transcripts = "all"
        if select_transcripts == '["raw"]': select_transcripts = "raw"

        try:
            validate = vval.validate(
                variant_description,
                genome_build,
                select_transcripts,
                transcript_set=transcript_model,
                lovd_syntax_check=True
            )
            content = validate.format_as_dict(with_meta=True)
        except TimeoutError:
            return {
                "error": "Server busy — all processing slots are currently in use. Please retry later."
            }, 429
        except Exception as e:
            return {"error": str(e)}, 500
        finally:
            vval_object_pool.return_object(vval)

        args = parser.parse_args()
        if args['content-type'] == 'application/json':
            return representations.application_json(content, 200, None)
        elif args['content-type'] == 'text/xml':
            return representations.xml(content, 200, None)
        else:
            return content


@api.route("/variantvalidator_ensembl/<string:genome_build>/<string:variant_description>/<string:select_transcripts>",
           strict_slashes=False)
class VariantValidatorEnsemblClass(Resource):
    @api.expect(parser, validate=True)
    @auth.login_required()
    @vval_pool_limit()
    def get(self, genome_build, variant_description, select_transcripts, user_id=None):
        vval = vval_object_pool.get_object()
        transcript_model = "ensembl"

        if ("all" in select_transcripts or "raw" in select_transcripts) and "auth" not in select_transcripts:
            if not any(x in variant_description for x in ("c.", "n.", "r.", "p.")):
                return {"Not Found": "Setting select_transcripts to 'all' or 'raw' is deprecated for genomic "
                                     "variant processing using this endpoint. Use the LOVD endpoint for pipelines."}, 404
        elif "auth_all" in select_transcripts:
            select_transcripts = "all"
        elif "auth_raw" in select_transcripts:
            select_transcripts = "raw"

        variant_description = input_formatting.format_input(variant_description)
        select_transcripts = input_formatting.format_input(select_transcripts)
        if select_transcripts == '["all"]': select_transcripts = "all"
        if select_transcripts == '["raw"]': select_transcripts = "raw"

        try:
            validate = vval.validate(
                variant_description,
                genome_build,
                select_transcripts,
                transcript_set=transcript_model,
                lovd_syntax_check=True
            )
            content = validate.format_as_dict(with_meta=True)
        except TimeoutError:
            return {
                "error": "Server busy — all processing slots are currently in use. Please retry later."
            }, 429
        except Exception as e:
            return {"error": str(e)}, 500
        finally:
            vval_object_pool.return_object(vval)

        args = parser.parse_args()
        if args['content-type'] == 'application/json':
            return representations.application_json(content, 200, None)
        elif args['content-type'] == 'text/xml':
            return representations.xml(content, 200, None)
        else:
            return content


@api.route("/tools/gene2transcripts/<string:gene_query>", strict_slashes=False)
class Gene2transcriptsClass(Resource):
    @api.expect(parser, validate=True)
    @auth.login_required()
    @g2t_pool_limit()
    def get(self, gene_query, user_id=None):
        vval = g2t_object_pool.get_object()
        gene_query = input_formatting.format_input(gene_query)
        try:
            content = vval.gene2transcripts(gene_query, lovd_syntax_check=True)[0]
        except TimeoutError:
            return {
                "error": "Server busy — all processing slots are currently in use. Please retry later."
            }, 429
        except ConnectionError:
            g2t_object_pool.return_object(vval)
            raise exceptions.RemoteConnectionError("Cannot connect to rest.genenames.org, please try again later")
        finally:
            g2t_object_pool.return_object(vval)

        args = parser.parse_args()
        if args['content-type'] == 'application/json':
            return representations.application_json(content, 200, None)
        elif args['content-type'] == 'text/xml':
            return representations.xml(content, 200, None)
        else:
            return content


@api.route("/tools/gene2transcripts_v2/<string:gene_query>/<string:limit_transcripts>/<string:transcript_set>/"
           "<string:genome_build>", strict_slashes=False)
class Gene2transcriptsV2Class(Resource):
    @api.expect(parser_g2t, validate=True)
    @auth.login_required()
    @g2t_pool_limit()
    def get(self, gene_query, limit_transcripts, transcript_set, genome_build, user_id=None):
        vval = g2t_object_pool.get_object()

        args = parser_g2t.parse_args()
        bypass_genomic_spans = not bool(args['show_exon_info'])

        gene_query = input_formatting.format_input(gene_query)
        limit_transcripts = input_formatting.format_input(limit_transcripts)
        if len(limit_transcripts) == 1:
            limit_transcripts = limit_transcripts[0]

        try:
            if genome_build not in ["GRCh37", "GRCh38"]:
                genome_build = None
            if limit_transcripts in ["False", "false", False]:
                limit_transcripts = None
            content = vval.gene2transcripts(
                gene_query,
                select_transcripts=limit_transcripts,
                transcript_set=transcript_set,
                genome_build=genome_build,
                batch_output=True,
                validator=vval,
                bypass_genomic_spans=bypass_genomic_spans,
                lovd_syntax_check=True
            )
        except TimeoutError:
            return {
                "error": "Server busy — all processing slots are currently in use. Please retry later."
            }, 429
        except ConnectionError:
            g2t_object_pool.return_object(vval)
            raise exceptions.RemoteConnectionError("Cannot connect to rest.genenames.org, please try again later")
        finally:
            g2t_object_pool.return_object(vval)

        if args['content-type'] == 'application/json':
            return representations.application_json(content, 200, None)
        elif args['content-type'] == 'text/xml':
            return representations.xml(content, 200, None)
        else:
            return content


@api.route("/tools/hgvs2reference/<string:hgvs_description>", strict_slashes=False)
class Hgvs2referenceClass(Resource):
    @api.expect(parser, validate=True)
    @auth.login_required()
    @vval_pool_limit()
    def get(self, hgvs_description, user_id=None):
        vval = vval_object_pool.get_object()
        try:
            content = vval.hgvs2ref(hgvs_description)
        except TimeoutError:
            return {
                "error": "Server busy — all processing slots are currently in use. Please retry later."
            }, 429
        except Exception as e:
            return {"error": str(e)}, 500
        finally:
            vval_object_pool.return_object(vval)

        args = parser.parse_args()
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
