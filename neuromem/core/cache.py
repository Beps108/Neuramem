"""
NeuraMem LRU Cache with Msgpack Serialization
Provides efficient memory caching with binary serialization.
"""
import msgpack
import hashlib
from collections import OrderedDict
from typing import Any, Optional, Dict, List, Tuple
from datetime import datetime, timedelta
import threading


class LRUCache:
    """Thread-safe LRU Cache with msgpack serialization."""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: Optional[int] = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: OrderedDict[str, Tuple[Any, datetime]] = OrderedDict()
        self._lock = threading.RLock()
        
    def _serialize(self, data: Any) -> bytes:
        """Serialize data using msgpack."""
        return msgpack.packb(data, use_bin_type=True)
    
    def _deserialize(self, data: bytes) -> Any:
        """Deserialize data using msgpack."""
        return msgpack.unpackb(data, raw=False)
    
    def _is_expired(self, timestamp: datetime) -> bool:
        """Check if a cache entry has expired."""
        if self.ttl_seconds is None:
            return False
        return datetime.now() > timestamp + timedelta(seconds=self.ttl_seconds)
    
    def get(self, key: str) -> Optional[Any]:
        """Get an item from the cache."""
        with self._lock:
            if key not in self._cache:
                return None
            
            data, timestamp = self._cache[key]
            
            if self._is_expired(timestamp):
                del self._cache[key]
                return None
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            return data
    
    def set(self, key: str, value: Any) -> None:
        """Set an item in the cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
            
            # Evict oldest if at capacity
            while len(self._cache) >= self.max_size:
                self._cache.popitem(last=False)
            
            self._cache[key] = (value, datetime.now())
    
    def delete(self, key: str) -> bool:
        """Delete an item from the cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all items from the cache."""
        with self._lock:
            self._cache.clear()
    
    def keys(self) -> List[str]:
        """Get all non-expired keys."""
        with self._lock:
            now = datetime.now()
            valid_keys = []
            for key, (_, timestamp) in list(self._cache.items()):
                if not (self.ttl_seconds and now > timestamp + timedelta(seconds=self.ttl_seconds)):
                    valid_keys.append(key)
            return valid_keys
    
    def size(self) -> int:
        """Get current cache size."""
        with self._lock:
            return len(self._cache)
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "ttl_seconds": self.ttl_seconds,
                "utilization": len(self._cache) / self.max_size if self.max_size > 0 else 0
            }


class MsgpackUtils:
    """Utility functions for msgpack operations."""
    
    @staticmethod
    def hash_key(data: Any) -> str:
        """Create a hash key from data."""
        serialized = msgpack.packb(data, use_bin_type=True, sort_keys=True)
        return hashlib.sha256(serialized).hexdigest()
    
    @staticmethod
    def compress(data: Any) -> bytes:
        """Compress data using msgpack."""
        return msgpack.packb(data, use_bin_type=True, strict_types=True)
    
    @staticmethod
    def decompress(data: bytes) -> Any:
        """Decompress msgpack data."""
        return msgpack.unpackb(data, raw=False, strict_map_key=False)
    
    @staticmethod
    def save_to_file(data: Any, filepath: str) -> None:
        """Save data to a file using msgpack."""
        with open(filepath, 'wb') as f:
            packed = msgpack.packb(data, use_bin_type=True)
            f.write(packed)
    
    @staticmethod
    def load_from_file(filepath: str) -> Any:
        """Load data from a msgpack file."""
        with open(filepath, 'rb') as f:
            return msgpack.unpackb(f.read(), raw=False)


# Global cache instance
_default_cache: Optional[LRUCache] = None


def get_cache(max_size: int = 1000, ttl_seconds: Optional[int] = 3600) -> LRUCache:
    """Get or create the default cache instance."""
    global _default_cache
    if _default_cache is None:
        _default_cache = LRUCache(max_size=max_size, ttl_seconds=ttl_seconds)
    return _default_cache


if __name__ == "__main__":
    cache = get_cache(max_size=5, ttl_seconds=10)
    
    # Test caching
    cache.set("key1", {"data": "value1", "count": 42})
    cache.set("key2", [1, 2, 3, 4, 5])
    
    print(f"Retrieved: {cache.get('key1')}")
    print(f"Cache size: {cache.size()}")
    print(f"Stats: {cache.stats()}")
    
    # Test msgpack utils
    test_data = {"nested": {"key": "value"}, "list": [1, 2, 3]}
    hashed = MsgpackUtils.hash_key(test_data)
    print(f"Hash: {hashed[:16]}...")
