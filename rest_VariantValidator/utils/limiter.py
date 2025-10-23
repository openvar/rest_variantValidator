from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from rest_VariantValidator.utils.object_pool import (
    vval_object_pool,
    g2t_object_pool,
    simple_variant_formatter_pool
)

# Initialize Flask-Limiter
limiter = Limiter(key_func=get_remote_address)

# --------------------------
# Dynamic pool-based rate limiter
# --------------------------
def pool_dynamic_limit(pool, max_rate, min_rate=1):
    """
    Returns a dynamic Flask-Limiter rate string based on the number of available objects in a pool.
    """
    with pool.lock:
        if hasattr(pool, "objects"):        # ObjectPool (Validator)
            available = len(pool.objects)
        elif hasattr(pool, "pool"):         # SimpleVariantFormatterPool
            available = len(pool.pool)
        else:
            available = max_rate

    # Clamp the rate between min_rate and max_rate
    rate = max(min_rate, min(available, max_rate))
    return f"{rate}/second"

# --------------------------
# Convenience functions for each pool with custom max_rate
# --------------------------
def vval_pool_limit():
    return pool_dynamic_limit(vval_object_pool, max_rate=8)

def g2t_pool_limit():
    return pool_dynamic_limit(g2t_object_pool, max_rate=6)

def formatter_pool_limit():
    return pool_dynamic_limit(simple_variant_formatter_pool, max_rate=8)
