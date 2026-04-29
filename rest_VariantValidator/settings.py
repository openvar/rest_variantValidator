# settings.py

from pathlib import Path
from configparser import ConfigParser

# --------------------------------------------------
# BASE PATHS (HOME, not project)
# --------------------------------------------------
HOME_DIR = Path.home()

# Hidden VV directory in home
LOG_DIR = HOME_DIR / ".rest_variantvalidator"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Log files
VV_LOG = LOG_DIR / "VariantValidator.log"
REST_LOG = LOG_DIR / "rest_VariantValidator.log"

# --------------------------------------------------
# READ CONFIG (~/.variantvalidator)
# --------------------------------------------------
CONFIG_FILE = HOME_DIR / ".variantvalidator"

config = ConfigParser()
config.read(CONFIG_FILE)

# --------------------------------------------------
# GLOBAL LOGGING SWITCH
# --------------------------------------------------
logging_enabled = True

if config.has_section("logging"):
    logging_enabled = config.getboolean("logging", "log", fallback=True)

# --------------------------------------------------
# DEFAULT LEVELS
# --------------------------------------------------
console_level = "INFO"
file_level = "ERROR"

# --------------------------------------------------
# APPLY CONFIG OVERRIDES (ONLY IF ENABLED)
# --------------------------------------------------
if logging_enabled and config.has_section("logging"):

    raw_console = config.get("logging", "console", fallback=console_level)
    raw_file = config.get("logging", "file", fallback=file_level)

    console_level = raw_console.upper()
    file_level = raw_file.upper()

# --------------------------------------------------
# FORCE LOGGING OFF
# --------------------------------------------------
if not logging_enabled:
    console_level = "CRITICAL"
    file_level = "CRITICAL"

# --------------------------------------------------
# LOGGING CONFIG
# --------------------------------------------------
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "console": {
            "format": "[%(asctime)s] %(levelname)-8s | %(name)s | %(message)s",
        },
        "verbose": {
            "format": (
                "%(asctime)s | %(levelname)-8s | %(name)s | "
                "%(filename)s:%(lineno)d | %(message)s"
            ),
        },
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": console_level,
            "formatter": "console",
        },

        "vv_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": file_level,
            "filename": str(VV_LOG),
            "maxBytes": 5_000_000,
            "backupCount": 3,
            "formatter": "verbose",
        },

        "rest_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": file_level,
            "filename": str(REST_LOG),
            "maxBytes": 5_000_000,
            "backupCount": 3,
            "formatter": "verbose",
        },
    },

    "loggers": {
        "VariantValidator": {
            "handlers": ["console", "vv_file"],
            "level": console_level,
            "propagate": False,
        },

        "rest_VariantValidator": {
            "handlers": ["console", "rest_file"],
            "level": console_level,
            "propagate": True,
        },
    },

    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}


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
