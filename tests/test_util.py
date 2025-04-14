import pytest

from rest_VariantValidator.utils.object_pool import ObjectPool, \
    ObjectPoolTimeoutException


def test_object_pool_ensure():
    pool = ObjectPool(int)
    assert len(pool) == 0
    pool.ensure(2)
    assert len(pool) == 2

def test_object_pool_allocates():
    pool = ObjectPool(int, initial_pool_size=0, max_pool_size=1)
    assert len(pool) == 0
    with pool.item():
        assert len(pool) == 1
    assert len(pool) == 1

def test_object_pool_blocks():
    pool = ObjectPool(int, initial_pool_size=0, max_pool_size=1)
    assert len(pool) == 0
    with pool.item():
        with pytest.raises(ObjectPoolTimeoutException):
            with pool.item(timeout=1.0):
                pass

def test_object_pool_returns_on_error():
    pool = ObjectPool(int, initial_pool_size=1, max_pool_size=1)
    assert len(pool) == 1
    try:
        with pool.item():
            raise ValueError("test")
    except ValueError:
        pass
    assert len(pool) == 1
