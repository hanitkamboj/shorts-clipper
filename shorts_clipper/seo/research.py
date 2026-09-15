from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json
import time
import logging

log = logging.getLogger(__name__)

@dataclass
class ResearchCache:
    query: str
    locale: str
    results: dict
    timestamp: float
    ttl_seconds: int = 3600
    
    @property
    def is_expired(self) -> bool:
        return time.time() > self.timestamp + self.ttl_seconds
    
    def to_dict(self) -> dict:
        return {
            'query': self.query,
            'locale': self.locale,
            'results': self.results,
            'timestamp': self.timestamp,
            'ttl_seconds': self.ttl_seconds
        }
        
    @classmethod
    def from_dict(cls, data: dict) -> ResearchCache:
        return cls(**data)

class ResearchAgent:
    def __init__(self, ai_provider=None, cache_dir: Path = Path('.cache/research')):
        self._provider = ai_provider
        self._cache_dir = cache_dir
        self._cache_dir.mkdir(parents=True, exist_ok=True)
    
    def research(self, query: str, locale: str = 'en') -> dict:
        """Research current context for a topic."""
        cache = self._load_cache(query, locale)
        if cache and not cache.is_expired:
            log.info(f"Using cached research for query: {query}")
            return cache.results
            
        # Mock research gathering
        results = {
            'trending_keywords': [query, f"{query} shorts", f"best {query}"],
            'competitor_analysis': 'High volume, medium competition',
            'suggested_angles': ['Educational', 'Entertaining']
        }
        
        new_cache = ResearchCache(
            query=query,
            locale=locale,
            results=results,
            timestamp=time.time()
        )
        self._save_cache(new_cache)
        return results
    
    def _get_cache_path(self, query: str, locale: str) -> Path:
        safe_query = "".join(c if c.isalnum() else "_" for c in query.lower())
        return self._cache_dir / f"{locale}_{safe_query}.json"
        
    def _load_cache(self, query: str, locale: str) -> ResearchCache | None:
        path = self._get_cache_path(query, locale)
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return ResearchCache.from_dict(data)
            except Exception as e:
                log.warning(f"Failed to load research cache: {e}")
        return None
        
    def _save_cache(self, cache: ResearchCache) -> None:
        path = self._get_cache_path(cache.query, cache.locale)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(cache.to_dict(), f, indent=2)
        except Exception as e:
            log.warning(f"Failed to save research cache: {e}")
