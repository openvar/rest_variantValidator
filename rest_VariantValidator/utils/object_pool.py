import contextlib
import threading
from VariantValidator import Validator
from VariantFormatter import simpleVariantFormatter

class ObjectPoolTimeoutException(Exception):
    pass

class ObjectPool:
    def __init__(self, factory, initial_pool_size=0, max_pool_size=10):
        self.factory = factory
        self.max_pool_size = max_pool_size
        self._pool_size = initial_pool_size
        self._available = [factory() for _ in range(initial_pool_size)]
        self._pool_size = len(self._available)
        self._lock = threading.RLock()
        self._condition = threading.Condition(self._lock)

    def __len__(self):
        with self._lock:
            return self._pool_size

    def ensure(self, min_size):
        """Ensure that at least min_size items are available in the pool."""

        if min_size > self.max_pool_size:
            raise ValueError("min_size cannot be greater than max_pool_size")
        with self._condition:
            if self._pool_size >= min_size:
                return
            need = min_size - self._pool_size
            to_add = [self.factory() for _ in range(need)]
            self._available.extend(to_add)
            self._pool_size += len(to_add)
            self._condition.notify(need)

    @contextlib.contextmanager
    def item(self, timeout=None):
        """Check out an item from the pool and ensure it is returned.

        This must be used as a context manager for reliable cleanup:

            with pool.item() as obj:
                # use obj
                pass
        """

        with self._condition:
            if len(self._available) > 0:
                obj = self._available.pop()
            elif self._pool_size < self.max_pool_size:
                # Create a new object to add to the pool
                obj = self.factory()
                self._pool_size += 1
            else:
                if not self._condition.wait_for(lambda: len(self._available) > 0,
                                                timeout=timeout):
                    raise ObjectPoolTimeoutException("Timeout waiting for object from pool")
                obj = self._available.pop()
            try:
                yield obj
            finally:
                # return the object to the pool
                self._available.append(obj)
                self._condition.notify()


# Create shared object pools
vval_object_pool = ObjectPool(Validator, initial_pool_size=8, max_pool_size=10)
g2t_object_pool = ObjectPool(Validator, initial_pool_size=6, max_pool_size=10)
simple_variant_formatter_pool = ObjectPool(lambda: simpleVariantFormatter, initial_pool_size=8, max_pool_size=10)

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
