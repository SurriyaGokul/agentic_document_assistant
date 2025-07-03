import time
import threading
from collections import OrderedDict
from typing import Dict, Any

class InMemorySharedMemory:
    def __init__(self, max_size=1000, ttl_seconds=3600):
        self.max_size = max_size
        self.ttl = ttl_seconds
        self.storage = OrderedDict()
        self.lock = threading.Lock()
        self.hits = 0
        self.misses = 0

    def save(self, thread_id: str, data: Dict[str, Any]):
        with self.lock:
            timestamp = time.time()
            entry = {
                "timestamp": timestamp,
                **data
            }
            self.storage[thread_id] = entry
            self.storage.move_to_end(thread_id)

            # LRU eviction
            if len(self.storage) > self.max_size:
                self.storage.popitem(last=False)

    def get(self, thread_id: str) -> Any:
        with self.lock:
            entry = self.storage.get(thread_id)
            if not entry:
                self.misses += 1
                return None
            # TTL check
            if time.time() - entry["timestamp"] > self.ttl:
                self.storage.pop(thread_id, None)
                self.misses += 1
                return None
            self.hits += 1
            self.storage.move_to_end(thread_id)
            return entry

    def stats(self):
        return {"hits": self.hits, "misses": self.misses}
