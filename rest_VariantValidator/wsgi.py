"""
Gunicorn wsgi gateway file
"""
import os
from rest_VariantValidator.app import application as app
from configparser import ConfigParser
from VariantValidator.settings import CONFIG_DIR

config = ConfigParser()
config.read(CONFIG_DIR)

if config["logging"]["log"] == "True":
    app.debug = True
    app.config['PROPAGATE_EXCEPTIONS'] = True
else:
    app.debug = False
    app.config['PROPAGATE_EXCEPTIONS'] = False

if __name__ == '__main__':
    # Read the port from the environment variable, defaulting to 8000 if not set
    port = int(os.environ.get('PORT', 8000))
    app.run(host="127.0.0.1", port=port)

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
