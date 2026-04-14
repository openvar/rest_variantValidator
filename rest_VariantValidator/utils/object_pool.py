import threading
import logging
import platform
import gc
import resource
from configparser import ConfigParser

import psutil
import mysql.connector

from VariantValidator import Validator, settings as vv_settings
from VariantFormatter.simpleVariantFormatter import SimpleVariantFormatter


# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
logger = logging.getLogger("rest_VariantValidator")


# =============================================================================
# UTILS
# =============================================================================

def _total_ram_mb():
    return psutil.virtual_memory().total // (1024 * 1024)


# =============================================================================
# MEMORY ESTIMATION
# =============================================================================

def _estimate_rss_mb(factory, safety_factor=2.0):
    """
    Generic RSS delta estimator for a callable factory.
    """
    gc.collect()
    before = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

    obj = factory()
    del obj

    gc.collect()
    after = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    delta = max(after - before, 0)

    # macOS reports bytes, Linux reports KB
    if platform.system() == "Darwin":
        delta_mb = delta / (1024 * 1024)
    else:
        delta_mb = delta / 1024

    estimate = int(delta_mb * safety_factor)
    return max(estimate, 0)


def _estimate_validator_mem_mb():
    mem = _estimate_rss_mb(Validator, safety_factor=2.0)
    if mem <= 0:
        logger.warning(
            "Validator memory estimate unreliable; defaulting to 64 MB"
        )
        return 64
    return max(mem, 64)


def _estimate_formatter_mem_mb(validator_cost):
    """
    Formatter MUST cost at least as much as a Validator,
    because it owns a Validator internally.
    """
    mem = _estimate_rss_mb(SimpleVariantFormatter, safety_factor=2.0)
    if mem <= 0:
        logger.warning(
            "Formatter memory estimate unreliable; using Validator cost"
        )
        return validator_cost
    return max(mem, validator_cost)


# =============================================================================
# MYSQL
# =============================================================================

def _mysql_max_connections_from_config():
    config = ConfigParser()
    config.read(vv_settings.CONFIG_DIR)

    if not config.has_section("mysql"):
        raise RuntimeError("No [mysql] section found in VariantValidator config")

    conn = mysql.connector.connect(
        host=config.get("mysql", "host"),
        port=config.getint("mysql", "port"),
        user=config.get("mysql", "user"),
        password=config.get("mysql", "password"),
        database=config.get("mysql", "database"),
    )

    try:
        cur = conn.cursor()
        cur.execute("SHOW VARIABLES LIKE 'max_connections'")
        _, value = cur.fetchone()
        return int(value)
    finally:
        conn.close()


# =============================================================================
# CAPACITY COMPUTATION (RAM + MYSQL, WEIGHTED)
# =============================================================================

def compute_pool_sizes():
    total_ram = _total_ram_mb()
    usable_ram = int(total_ram * 0.45)  # policy

    validator_cost = _estimate_validator_mem_mb()
    formatter_cost = _estimate_formatter_mem_mb(validator_cost)

    mysql_max = _mysql_max_connections_from_config()
    mysql_reserved = max(10, int(mysql_max * 0.15))
    mysql_limit = max(mysql_max - mysql_reserved, 1)

    # Allocation ratios
    VVAL_RATIO = 0.4
    VF_RATIO   = 0.4

    ram_for_vval = int(usable_ram * VVAL_RATIO)
    ram_for_vf   = int(usable_ram * VF_RATIO)
    ram_for_g2t  = usable_ram - ram_for_vval - ram_for_vf

    vval_size = max(1, ram_for_vval // validator_cost)
    vf_size   = max(1, ram_for_vf   // formatter_cost)
    g2t_size  = max(1, ram_for_g2t  // validator_cost)

    total_units = vval_size + vf_size + g2t_size

    # Enforce MySQL ceiling
    if total_units > mysql_limit:
        scale = mysql_limit / float(total_units)
        vval_size = max(1, int(vval_size * scale))
        vf_size   = max(1, int(vf_size * scale))
        g2t_size  = max(1, mysql_limit - vval_size - vf_size)

    logger.warning(
        "Capacity scan:"
        " RAM=%dMB (usable=%dMB), "
        "validator_cost=%dMB, "
        "formatter_cost=%dMB, "
        "mysql_usable=%d",
        total_ram,
        usable_ram,
        validator_cost,
        formatter_cost,
        mysql_limit,
    )

    logger.warning(
        "Pool sizes:"
        " vval=%d, vf=%d, g2t=%d (total=%d)",
        vval_size,
        vf_size,
        g2t_size,
        vval_size + vf_size + g2t_size,
    )

    return vval_size, vf_size, g2t_size


# =============================================================================
# FIXED OBJECT POOL
# =============================================================================

class FixedObjectPool:
    """Strict fixed-size blocking pool."""

    def __init__(self, factory, size):
        if size <= 0:
            raise ValueError("Pool size must be > 0")

        self._size = size
        self._available = []
        self._in_use = 0

        self._lock = threading.Lock()
        self._condition = threading.Condition(self._lock)

        for _ in range(size):
            self._available.append(factory())

    def available(self):
        with self._lock:
            return len(self._available)

    def total(self):
        return self._size

    def get_object(self):
        with self._condition:
            while not self._available:
                self._condition.wait()
            self._in_use += 1
            return self._available.pop()

    def return_object(self, obj):
        with self._condition:
            if self._in_use <= 0:
                raise RuntimeError("Pool underflow detected")
            self._in_use -= 1
            self._available.append(obj)
            self._condition.notify()


# =============================================================================
# POOLS (EXPORT NAMES EXPECTED BY ENDPOINTS)
# =============================================================================

vval_size, vf_size, g2t_size = compute_pool_sizes()

# Validator-only pools
vval_object_pool = FixedObjectPool(Validator, vval_size)
g2t_object_pool  = FixedObjectPool(Validator, g2t_size)

# Formatter pool (OBJECT MODE ONLY)
vf_tool_object_pool = FixedObjectPool(SimpleVariantFormatter, vf_size)

# Backwards-compatible alias expected by codebase
simple_variant_formatter_pool = vf_tool_object_pool


# -----------------------------------------------------------------------------
# FINAL LOGGING
# -----------------------------------------------------------------------------
logger.warning("Object pools initialised:")

logger.warning("  vval_object_pool: %d", vval_object_pool.total())
logger.warning("  simple_variant_formatter_pool: %d", simple_variant_formatter_pool.total())
logger.warning("  g2t_object_pool: %d", g2t_object_pool.total())

logger.warning(
    "Total Validator-weighted capacity: %d",
    vval_object_pool.total()
    + simple_variant_formatter_pool.total()
    + g2t_object_pool.total(),
)


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
