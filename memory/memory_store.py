import time
import threading
from collections import OrderedDict
from typing import Dict, Any

class LRUCacheTTL:
    def __init__(self, max_size=1000, ttl_seconds=3600):
        self.max_size = max_size
        self.ttl = ttl_seconds
        self.storage = OrderedDict()
        self.lock = threading.Lock()
        self.hits = 0
        self.misses = 0

    def get(self, key: Any) -> Any:
        with self.lock:
            entry = self.storage.get(key)
            if not entry:
                self.misses += 1
                return None
            if time.time() - entry["timestamp"] > self.ttl:
                self.storage.pop(key, None)
                self.misses += 1
                return None
            self.hits += 1
            self.storage.move_to_end(key)
            return entry["value"]

    def put(self, key: Any, value: Any):
        with self.lock:
            timestamp = time.time()
            entry = {
                "timestamp": timestamp,
                "value": value
            }
            self.storage[key] = entry
            self.storage.move_to_end(key)
            if len(self.storage) > self.max_size:
                self.storage.popitem(last=False)

    def stats(self):
        return {"hits": self.hits, "misses": self.misses}
