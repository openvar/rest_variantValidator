import pytest

from rest_VariantValidator.utils.object_pool import (
    vval_object_pool,
    simple_variant_formatter_pool,
    g2t_object_pool,
)

POOLS = [vval_object_pool, g2t_object_pool, simple_variant_formatter_pool]

@pytest.fixture(scope='function')
def check_object_pool_leaks():
    counts = [(pool, len(pool)) for pool in POOLS]
    yield
    assert [(pool, len(pool)) for pool in POOLS] == counts
