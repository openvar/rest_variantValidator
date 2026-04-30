"""
mod_wsgi gateway wsgi file
"""

import logging
from configparser import ConfigParser

from VariantValidator.settings import CONFIG_DIR
from rest_VariantValidator.app import application as application


# --------------------------------------------------
# Load config
# --------------------------------------------------
config = ConfigParser()
config.read(CONFIG_DIR)


# --------------------------------------------------
# Logging master switch
# --------------------------------------------------
log_enabled = config.get("logging", "log", fallback="true").lower() not in (
    "false", "0", "no", "off"
)


# --------------------------------------------------
# Logging level (console drives behaviour)
# --------------------------------------------------
console_level = config.get("logging", "console", fallback="INFO").upper()
numeric_level = getattr(logging, console_level, logging.INFO)


# --------------------------------------------------
# Determine debug + exception behaviour
# --------------------------------------------------
if not log_enabled:
    # Master override → everything off
    application.debug = False
    application.config["PROPAGATE_EXCEPTIONS"] = False

else:
    # Level-driven behaviour
    is_debug_mode = numeric_level < logging.ERROR

    application.debug = is_debug_mode
    application.config["PROPAGATE_EXCEPTIONS"] = is_debug_mode


# --------------------------------------------------
# Dev server (only if directly executed)
# --------------------------------------------------
if __name__ == "__main__":
    application.run(host="127.0.0.1", port=8000)

# <LICENSE>
# Copyright (C) 2016-2026 VariantValidator Contributors
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
