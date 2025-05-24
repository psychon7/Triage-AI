import time
import random
import json
import os
from typing import Optional, Dict, Any
from langchain_community.tools import DuckDuckGoSearchRun

class CachedSearch:
    def __init__(self, cache_file="search_cache.json", max_retries=3, base_delay=2):
        self.cache_file = cache_file
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.search_tool = DuckDuckGoSearchRun()
        self.cache = self._load_cache()

    def _load_cache(self) -> Dict[str, Any]:
        """Load search cache from file if it exists"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading cache: {str(e)}")
                return {}
        return {}

    def _save_cache(self) -> None:
        """Save search cache to file"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f)
        except Exception as e:
            print(f"Error saving cache: {str(e)}")

    def search(self, query: str) -> str:
        """Search with caching and retry logic"""
        # Check cache first
        if query in self.cache:
            print(f"Cache hit for query: {query}")
            return self.cache[query]
        
        # If not in cache, perform search with retry logic
        for attempt in range(self.max_retries):
            try:
                print(f"Search attempt {attempt + 1} for query: {query}")
                result = self.search_tool.run(query)
                
                # Cache successful result
                if result:
                    self.cache[query] = result
                    self._save_cache()
                    return result
                
            except Exception as e:
                error_msg = str(e)
                print(f"Search attempt {attempt + 1} failed: {error_msg}")
                
                # Check if it's a rate limit issue
                if "ratelimit" in error_msg.lower() or "429" in error_msg or "202" in error_msg:
                    # Calculate delay with exponential backoff and jitter
                    delay = (self.base_delay * (2 ** attempt)) + (random.random() * 2)
                    print(f"Rate limit hit. Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                else:
                    # If it's not a rate limit issue, just pause briefly before retry
                    time.sleep(1)
        
        # If all retries failed, return a fallback message
        fallback_message = "I couldn't complete the web search due to rate limiting. Proceeding with the task based on my existing knowledge."
        return fallback_message

# Create singleton instance
cached_search = CachedSearch()
