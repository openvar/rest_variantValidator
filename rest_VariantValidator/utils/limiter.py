from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import threading
from math import ceil

# Import pools
from rest_VariantValidator.utils.object_pool import vval_object_pool, g2t_object_pool, simple_variant_formatter_pool


# Create Limiter instance (the app will bind this later)
limiter = Limiter(key_func=get_remote_address)


# --- Simple exponential smoother for stability ---
class RateSmoother:
    def __init__(self, alpha=0.3):
        self.alpha = alpha
        self.value = None
        self.lock = threading.Lock()

    def smooth(self, sample):
        with self.lock:
            if self.value is None:
                self.value = sample
            else:
                self.value = (self.alpha * sample) + ((1 - self.alpha) * self.value)
            return self.value


# One smoother per pool (keeps them stable independently)
vval_smoother = RateSmoother(alpha=0.25)
g2t_smoother = RateSmoother(alpha=0.25)
fmt_smoother = RateSmoother(alpha=0.25)


def _compute_rate(pool, min_rate, pool_limit, smoother):
    """
    Compute dynamic rate:
        min_rate + (available / pool_size) * pool_limit
    Returns a string Flask-Limiter understands, e.g. "50 per minute".
    """
    available = pool.available()
    total = max(pool.total(), 1)

    fraction = available / total
    raw_rate = min_rate + (fraction * pool_limit)

    if smoother:
        raw_rate = smoother.smooth(raw_rate)

    rate_val = max(min_rate, int(ceil(raw_rate)))

    return f"{rate_val} per minute"


# Per-pool functions used by @limiter.limit()
def vval_rate():
    return _compute_rate(
        pool=vval_object_pool,
        min_rate=5,
        pool_limit=150,
        smoother=vval_smoother
    )


def g2t_rate():
    return _compute_rate(
        pool=g2t_object_pool,
        min_rate=2,
        pool_limit=40,
        smoother=g2t_smoother
    )


def fmt_rate():
    return _compute_rate(
        pool=simple_variant_formatter_pool,
        min_rate=10,
        pool_limit=300,
        smoother=fmt_smoother
    )


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
