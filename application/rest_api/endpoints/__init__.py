from flask_restx import Api

from .hello import api as ns_hello
from .name import api as ns_name
from .variantvalidator_endpoints import api as ns_vv

# Define the API as api
api = Api(version="1.0",
          title="rest_variantValidator",
          description="### REST API for [VariantValidator](https://github.com/openvar/variantValidator) and"
                      " [VariantFormatter](https://github.com/openvar/variantFormatter)<br>"
                      "&nbsp;&nbsp;&nbsp;"
                      "- [Source code](https://github.com/openvar/rest_variantValidator)")

api.add_namespace(ns_hello)
api.add_namespace(ns_name)
api.add_namespace(ns_vv)