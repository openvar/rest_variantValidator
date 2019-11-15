import rest_VariantValidator
from flask_restplus import Api
# from .hello import api as ns_hello
# from .name import api as ns_name
from .variantvalidator_endpoints import api as ns_vv
from .variantformatter_endpoints import api as ns_vf

# Define the API as api
api = Api(version=rest_VariantValidator.__version__,
          title="rest_variantValidator",
          description="### REST API for [VariantValidator](https://github.com/openvar/variantValidator) and"
                      " [VariantFormatter](https://github.com/openvar/variantFormatter)"
                      "&nbsp;&nbsp;&nbsp;\n"
                      "- [Source code](https://github.com/openvar/rest_variantValidator)\n"
                      "- [Terms of use and about VariantValidator](https://github.com/openvar/variantValidator/blob"
                      "/master/README.md)")

# api.add_namespace(ns_hello)
# api.add_namespace(ns_name)
api.add_namespace(ns_vv)
api.add_namespace(ns_vf)


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
