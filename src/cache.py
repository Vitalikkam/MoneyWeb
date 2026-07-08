"""
Redis cache client for the app.
"""

import json
import streamlit as st
import hashlib
import sys

# Try to import Redis, but fallback gracefully
try:
    from upstash_redis import Redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("⚠️ upstash_redis not installed. Cache disabled.")

class CacheClient:
    def __init__(self):
        self.enabled = False
        self.redis = None
        
        if not REDIS_AVAILABLE:
            print("⚠️ Redis cache disabled (library not installed)")
            return
        
        try:
            # Try both possible secret names
            url = st.secrets.get("UPSTASH_REDIS_REST_URL", None)
            if not url:
                url = st.secrets.get("UPSTASH_URL", None)
            
            token = st.secrets.get("UPSTASH_REDIS_REST_TOKEN", None)
            if not token:
                token = st.secrets.get("UPSTASH_TOKEN", None)
            
            if url and token:
                self.redis = Redis(url=url, token=token)
                self.enabled = True
                print(f"✅ Redis cache enabled: {url}")
            else:
                print(f"⚠️ Redis cache disabled (missing credentials)")
                print(f"   URL: {'found' if url else 'missing'}")
                print(f"   Token: {'found' if token else 'missing'}")
        except Exception as e:
            print(f"⚠️ Redis cache disabled: {e}")
    
    def _get_key(self, query):
        """Generate a cache key from the query."""
        return f"food:{hashlib.md5(query.lower().strip().encode()).hexdigest()}"
    
    def get_food(self, query):
        """Get cached food data for a query."""
        if not self.enabled or not self.redis:
            return None
        
        try:
            key = self._get_key(query)
            data = self.redis.get(key)
            if data:
                print(f"✅ Cache hit: {query}")
                return json.loads(data)
            else:
                print(f"❌ Cache miss: {query}")
                return None
        except Exception as e:
            print(f"⚠️ Cache get error: {e}")
            return None
    
    def set_food(self, query, data, ttl=604800):
        """
        Cache food data for a query.
        TTL = 7 days (604800 seconds)
        """
        if not self.enabled or not self.redis:
            return
        
        try:
            key = self._get_key(query)
            self.redis.setex(key, ttl, json.dumps(data))
            print(f"✅ Cached: {query} (TTL: {ttl}s)")
        except Exception as e:
            print(f"⚠️ Cache set error: {e}")
    
    def clear(self):
        """Clear all cache (use with caution)."""
        if not self.enabled or not self.redis:
            return
        
        try:
            print("⚠️ Cache clear not implemented for safety")
        except Exception as e:
            print(f"⚠️ Cache clear error: {e}")
    
    def get_stats(self):
        """Get cache statistics (optional)."""
        if not self.enabled:
            return {"enabled": False}
        
        try:
            return {"enabled": True, "status": "healthy"}
        except Exception as e:
            return {"enabled": True, "status": "error", "error": str(e)}

# Singleton instance
_cache = None

def get_cache():
    """Get or create the cache client."""
    global _cache
    if _cache is None:
        _cache = CacheClient()
    return _cache