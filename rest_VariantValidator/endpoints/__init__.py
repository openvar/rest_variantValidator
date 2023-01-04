import rest_VariantValidator
import VariantValidator
import VariantFormatter
from flask_restx import Api
from flask import url_for
from .variantvalidator_endpoints import api as ns_vv
from .variantformatter_endpoints import api as ns_vf
from .lovd_endpoints import api as ns_lovd
from .vijs_endpoints import api as ns_vijs
from .hello import api as ns_hello

# Obtain VariantValidator related metadata
vval = VariantValidator.Validator()
config_dict = vval.my_config()


# Override standard specs_url to allow reverse-proxy access through mod_wsgi
class CustomAPI(Api):
    @property
    def specs_url(self):
        """
        The Swagger specifications absolute url (ie. `swagger.json`)

        This method returns the path relative to the APP required for reverse proxy access

        :rtype: str
        """
        return url_for(self.endpoint('specs'), _external=False)


# Define the API as api
api = CustomAPI(version=rest_VariantValidator.__version__,
                title="rest_VariantValidator",
                description="## By continuing to use this service you agree to our terms and conditions of Use\n"
                      "- [Terms and Conditions](https://github.com/openvar/variantValidator/blob"
                      "/master/README.md)\n\n"
                      "## Powered by\n"
                      "- [VariantValidator](https://github.com/openvar/rest_variantValidator) version "
                      + VariantValidator.__version__ + "\n"
                      "- [VariantFormatter](https://github.com/openvar/variantFormatter) version "
                      + VariantFormatter.__version__ + "\n"
                      " - [vv_hgvs](https://github.com/openvar/vv_hgvs) version "
                      + config_dict['variantvalidator_hgvs_version'] + "\n"
                      " - [VVTA](https://www528.lamp.le.ac.uk/) release "
                      + config_dict['vvta_version'] + "\n"
                      " - [vvSeqRepo](https://www528.lamp.le.ac.uk/) release "
                      + config_dict['vvseqrepo_db'].split('/')[-2]
          )

# Add the namespaces to the API
api.add_namespace(ns_vv)
api.add_namespace(ns_vf)
api.add_namespace(ns_lovd)
api.add_namespace(ns_vijs)
api.add_namespace(ns_hello)


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
