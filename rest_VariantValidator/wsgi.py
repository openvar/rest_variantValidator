"""
Gunicorn WSGI gateway file for VVrest
"""

import os
import logging
from configparser import ConfigParser

from VariantValidator.settings import CONFIG_DIR
from rest_VariantValidator.app import application as app


# -----------------------------------------------------
# Load configuration
# -----------------------------------------------------
config = ConfigParser()
config.read(CONFIG_DIR)


# -----------------------------------------------------
# Logging master switch
# -----------------------------------------------------
log_enabled = config.get("logging", "log", fallback="true").lower() not in (
    "false", "0", "no", "off"
)


# -----------------------------------------------------
# Logging level (console = behaviour driver)
# -----------------------------------------------------
console_level = config.get("logging", "console", fallback="INFO").upper()
numeric_level = getattr(logging, console_level, logging.INFO)


# -----------------------------------------------------
# Determine debug + exception behaviour
# -----------------------------------------------------
if not log_enabled:
    # Hard override: everything OFF (production-safe)
    app.debug = False
    app.config["PROPAGATE_EXCEPTIONS"] = False

else:
    # Debug mode driven by logging verbosity
    is_debug_mode = numeric_level < logging.ERROR

    app.debug = is_debug_mode
    app.config["PROPAGATE_EXCEPTIONS"] = is_debug_mode


# -----------------------------------------------------
# Dev server (NOT used by gunicorn)
# -----------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="127.0.0.1", port=port)


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
