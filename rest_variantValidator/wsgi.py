#!python

import site
site.addsitedir('/local/python/2.7.12/lib/python2.7/site-packages/')

import os
import sys
import logging
from configparser import ConfigParser
from VariantValidator.settings import CONFIG_DIR
logging.basicConfig(stream=sys.stderr)

# Set path to file
WSGI_ROOT = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, WSGI_ROOT)

# Run the server (if file is called directly by python, server is internal dev server)
if __name__ == '__main__':
    from validator_api import app as application
    config = ConfigParser()
    config.read(CONFIG_DIR)
    if config["logging"]["log"] == "True":
        application.debug = True
        application.config['PROPAGATE_EXCEPTIONS'] = True
    else:
        application.debug = False
        application.config['PROPAGATE_EXCEPTIONS'] = False
    application.run(host='0.0.0.0')
else:
    from validator_api import app as application

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