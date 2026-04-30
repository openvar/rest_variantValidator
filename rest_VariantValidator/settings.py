"""
VVrest logging settings (fully aligned system-wide)
"""

import logging
from pathlib import Path
from configparser import ConfigParser


# --------------------------------------------------
# BASE PATHS
# --------------------------------------------------
HOME_DIR = Path.home()

HIDDEN_LOG_DIR = HOME_DIR / ".rest_variantvalidator"
VISIBLE_LOG_DIR = HOME_DIR / "log"


# --------------------------------------------------
# READ CONFIG (~/.variantvalidator)
# --------------------------------------------------
CONFIG_FILE = HOME_DIR / ".variantvalidator"

config = ConfigParser()
config.read(CONFIG_FILE)


# --------------------------------------------------
# GLOBAL LOGGING SWITCH
# --------------------------------------------------
logging_enabled = config.get("logging", "log", fallback="true").lower() not in (
    "false", "0", "no", "off"
)


# --------------------------------------------------
# DEFAULT LEVELS
# --------------------------------------------------
console_level = "INFO"
file_level = "ERROR"


# --------------------------------------------------
# APPLY CONFIG OVERRIDES (IF ENABLED)
# --------------------------------------------------
if logging_enabled and config.has_section("logging"):
    console_level = config.get("logging", "console", fallback=console_level).upper()
    file_level = config.get("logging", "file", fallback=file_level).upper()


# --------------------------------------------------
# FORCE LOGGING OFF (MASTER OVERRIDE)
# --------------------------------------------------
if not logging_enabled:
    console_level = "CRITICAL"
    file_level = "CRITICAL"


# --------------------------------------------------
# DETERMINE NUMERIC LEVEL
# --------------------------------------------------
numeric_level = getattr(logging, console_level, logging.INFO)


# --------------------------------------------------
# SELECT LOG DIRECTORY (FINAL RULE)
# --------------------------------------------------
if not logging_enabled:
    # Master override → hide logs
    LOG_DIR = HIDDEN_LOG_DIR

elif numeric_level >= logging.ERROR:
    # Production → visible logs
    LOG_DIR = VISIBLE_LOG_DIR

else:
    # Dev/debug → hidden logs
    LOG_DIR = HIDDEN_LOG_DIR

LOG_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# LOG FILES
# --------------------------------------------------
VV_LOG = LOG_DIR / "VariantValidator.log"
REST_LOG = LOG_DIR / "rest_VariantValidator.log"


# --------------------------------------------------
# LOGGING CONFIG
# --------------------------------------------------
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,

    # ---------------- FORMATTERS ----------------
    "formatters": {
        "console": {
            "format": (
                "%(asctime)s | %(levelname)-8s | %(name)s | "
                "%(filename)s:%(lineno)d | %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "verbose": {
            "format": (
                "%(asctime)s | %(levelname)-8s | %(name)s | "
                "%(filename)s:%(lineno)d | %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },

    # ---------------- HANDLERS ----------------
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

    # ---------------- LOGGERS ----------------
    "loggers": {

        # VariantValidator core
        "VariantValidator": {
            "handlers": ["console", "vv_file"],
            "level": console_level,
            "propagate": False,
        },

        # REST layer
        "rest_VariantValidator": {
            "handlers": ["console", "rest_file"],
            "level": console_level,
            "propagate": True,   # allow upstream logs (gunicorn, etc.)
        },
    },

    # ---------------- ROOT ----------------
    "root": {
        "handlers": ["console"],
        "level": "ERROR",  # production-safe fallback
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
