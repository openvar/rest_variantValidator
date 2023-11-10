import threading
from VariantValidator import Validator
from VariantFormatter import simpleVariantFormatter

class ObjectPool:
    def __init__(self, object_type, pool_size=10):
        self.pool_size = pool_size
        self.objects = [object_type() for _ in range(pool_size)]
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
        self.pool = [simpleVariantFormatter for _ in range(pool_size)]
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

# Create shared object pools
vval_object_pool = ObjectPool(Validator, pool_size=2)
g2t_object_pool = ObjectPool(Validator, pool_size=2)
simple_variant_formatter_pool = SimpleVariantFormatterPool(pool_size=2)
