from flask import request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import time
import threading

from rest_VariantValidator.utils.object_pool import (
    vval_object_pool,
    g2t_object_pool,
    simple_variant_formatter_pool
)

# --------------------------
# Initialize Flask-Limiter
# --------------------------
limiter = Limiter(key_func=get_remote_address)

# --------------------------
# Helper: Dynamic pool-based rate calculation
# --------------------------
def pool_dynamic_limit(pool, max_rate, min_rate=1):
    """
    Returns a dynamic rate (operations per second) based on pool availability.
    """
    with pool.lock:
        if hasattr(pool, "objects"):
            available = len(pool.objects)
        elif hasattr(pool, "pool"):
            available = len(pool.pool)
        else:
            available = max_rate

    # Clamp rate between min_rate and max_rate
    rate = max(min_rate, min(available, max_rate))
    return rate  # numeric rate, not string

# --------------------------
# Custom blocking limiter
# --------------------------
def blocking_rate_limit(pool, max_rate, min_rate=1, timeout=60):
    """
    Decorator that enforces a dynamic, blocking rate limit.
    If limit is hit, waits until capacity becomes available (up to `timeout` seconds).
    """

    lock = threading.Lock()
    last_times = []

    def decorator(fn):
        def wrapped(*args, **kwargs):
            rate = pool_dynamic_limit(pool, max_rate, min_rate)
            interval = 1.0 / rate if rate > 0 else 1.0

            nonlocal last_times
            now = time.time()

            with lock:
                # Remove expired timestamps
                last_times = [t for t in last_times if now - t < 1.0]

                # Wait for capacity if at limit
                start_wait = time.time()
                while len(last_times) >= rate:
                    if time.time() - start_wait > timeout:
                        return jsonify({
                            "error": "rate_limited",
                            "message": f"Request delayed too long (>{timeout}s) due to load."
                        }), 429
                    time.sleep(0.05)  # short sleep before checking again
                    now = time.time()
                    last_times = [t for t in last_times if now - t < 1.0]

                # Record this request timestamp
                last_times.append(time.time())

            return fn(*args, **kwargs)

        wrapped.__name__ = fn.__name__
        return wrapped
    return decorator

# --------------------------
# Pool-specific convenience wrappers
# --------------------------
def vval_pool_limit():
    return blocking_rate_limit(vval_object_pool, max_rate=8)

def g2t_pool_limit():
    return blocking_rate_limit(g2t_object_pool, max_rate=6)

def formatter_pool_limit():
    return blocking_rate_limit(simple_variant_formatter_pool, max_rate=8)

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
