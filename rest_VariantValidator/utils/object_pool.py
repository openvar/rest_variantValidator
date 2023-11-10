import threading
from VariantValidator import Validator
from VariantFormatter import simpleVariantFormatter

class ObjectPool:
    def __init__(self, object_type, pool_size=10):
        self.pool_size = pool_size
        self.objects = [object_type() for _ in range(pool_size)]
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)

    def get_object(self):
        with self.condition:
            while not self.objects:
                # Wait until an object becomes available
                self.condition.wait()
            return self.objects.pop()

    def return_object(self, obj):
        with self.condition:
            self.objects.append(obj)
            self.condition.notify()  # Notify waiting threads that an object is available

class SimpleVariantFormatterPool:
    def __init__(self, pool_size=10):
        self.pool_size = pool_size
        self.pool = [simpleVariantFormatter for _ in range(pool_size)]
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)

    def get(self):
        with self.condition:
            while not self.pool:
                # Wait until a formatter becomes available
                self.condition.wait()
            return self.pool.pop()

    def return_object(self, obj):
        with self.condition:
            self.pool.append(obj)
            self.condition.notify()  # Notify waiting threads that a formatter is available

# Create shared object pools
vval_object_pool = ObjectPool(Validator, pool_size=1)
g2t_object_pool = ObjectPool(Validator, pool_size=1)
simple_variant_formatter_pool = SimpleVariantFormatterPool(pool_size=1)

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
