import threading
import VariantValidator
import VariantFormatter.simpleVariantFormatter


class ObjectPool:
    def __init__(self, pool_size=10):
        self.pool_size = pool_size
        self.objects = [VariantValidator.Validator() for _ in range(pool_size)]
        self.lock = threading.Lock()

    def get_object(self):
        with self.lock:
            while not self.objects:
                # Wait until an object becomes available
                self.lock.release()
                self.lock.acquire()
            return self.objects.pop()

    def return_object(self, obj):
        with self.lock:
            self.objects.append(obj)


class SimpleVariantFormatterPool:
    def __init__(self, pool_size=10):
        self.pool_size = pool_size
        self.pool = [VariantFormatter.simpleVariantFormatter for _ in range(pool_size)]
        self.lock = threading.Lock()

    def get(self):
        with self.lock:
            while not self.pool:
                self.lock.release()
                self.lock.acquire()
            return self.pool.pop()

    def return_object(self, obj):
        with self.lock:
            self.pool.append(obj)


# Create a shared object pools
vval_object_pool = ObjectPool(pool_size=2)
simple_variant_formatter_pool = SimpleVariantFormatterPool(pool_size=2)

# <LICENSE>
# Copyright (C) 2016-2023 VariantValidator Contributors
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


