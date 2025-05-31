import time
from typing import Dict, Any

class InMemorySharedMemory:
    def __init__(self):
        self.storage = {}

    def save(self, thread_id: str, data: Dict[str, Any]):
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        entry = {
            "timestamp": timestamp,
            **data
        }
        self.storage.setdefault(thread_id, []).append(entry)

    def get(self, thread_id: str) -> list:
        return self.storage.get(thread_id, [])
