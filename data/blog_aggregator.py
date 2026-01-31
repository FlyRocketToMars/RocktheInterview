"""
Blog Aggregator
Fetches and aggregates content from curated ML interview prep blogs
"""
import json
import feedparser
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import hashlib


class BlogAggregator:
    """Aggregates content from multiple ML/AI blogs via RSS feeds."""
    
    def __init__(self):
        self.sources_file = Path(__file__).parent / "blog_sources.json"
        self.cache_file = Path(__file__).parent / "blog_cache.json"
        self.cache_duration = timedelta(hours=6)  # Refresh every 6 hours
        self._load_sources()
    
    def _load_sources(self):
        """Load blog sources configuration."""
        try:
            with open(self.sources_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.sources = data.get("sources", [])
                self.categories = data.get("categories", {})
        except Exception as e:
            print(f"Error loading sources: {e}")
            self.sources = []
            self.categories = {}
    
    def _load_cache(self) -> Dict:
        """Load cached articles."""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except:
            pass
        return {"articles": [], "last_fetch": None}
    
    def _save_cache(self, data: Dict):
        """Save articles to cache."""
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def _should_refresh(self) -> bool:
        """Check if cache needs refresh."""
        cache = self._load_cache()
        last_fetch = cache.get("last_fetch")
        
        if not last_fetch:
            return True
        
        try:
            last_time = datetime.fromisoformat(last_fetch)
            return datetime.now() - last_time > self.cache_duration
        except:
            return True
    
    def _fetch_rss(self, source: Dict) -> List[Dict]:
        """Fetch articles from RSS feed."""
        articles = []
        rss_url = source.get("rss")
        
        if not rss_url:
            return articles
        
        try:
            feed = feedparser.parse(rss_url)
            
            for entry in feed.entries[:10]:  # Limit to 10 per source
                article = {
                    "id": hashlib.md5(entry.get("link", "").encode()).hexdigest()[:12],
                    "title": entry.get("title", "Untitled"),
                    "url": entry.get("link", ""),
                    "summary": self._clean_summary(entry.get("summary", "")),
                    "published": self._parse_date(entry),
                    "source_id": source.get("id"),
                    "source_name": source.get("name"),
                    "author": source.get("author"),
                    "topics": source.get("topics", [])
                }
                articles.append(article)
        except Exception as e:
            print(f"Error fetching RSS from {source.get('name')}: {e}")
        
        return articles
    
    def _clean_summary(self, summary: str) -> str:
        """Clean and truncate summary."""
        # Remove HTML tags (simple approach)
        import re
        clean = re.sub(r'<[^>]+>', '', summary)
        clean = clean.strip()
        
        # Truncate to 200 chars
        if len(clean) > 200:
            clean = clean[:200] + "..."
        
        return clean
    
    def _parse_date(self, entry) -> str:
        """Parse published date from RSS entry."""
        try:
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                dt = datetime(*entry.published_parsed[:6])
                return dt.isoformat()
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                dt = datetime(*entry.updated_parsed[:6])
                return dt.isoformat()
        except:
            pass
        return datetime.now().isoformat()
    
    def fetch_all(self, force_refresh: bool = False) -> List[Dict]:
        """Fetch articles from all sources."""
        if not force_refresh and not self._should_refresh():
            cache = self._load_cache()
            return cache.get("articles", [])
        
        all_articles = []
        
        for source in self.sources:
            if not source.get("active", True):
                continue
            
            articles = self._fetch_rss(source)
            all_articles.extend(articles)
        
        # Sort by date (newest first)
        all_articles.sort(key=lambda x: x.get("published", ""), reverse=True)
        
        # Save to cache
        cache_data = {
            "articles": all_articles,
            "last_fetch": datetime.now().isoformat()
        }
        self._save_cache(cache_data)
        
        return all_articles
    
    def get_by_topic(self, topic: str) -> List[Dict]:
        """Get articles filtered by topic."""
        articles = self.fetch_all()
        return [a for a in articles if topic in a.get("topics", [])]
    
    def get_by_source(self, source_id: str) -> List[Dict]:
        """Get articles from a specific source."""
        articles = self.fetch_all()
        return [a for a in articles if a.get("source_id") == source_id]
    
    def get_sources(self) -> List[Dict]:
        """Get all blog sources."""
        return self.sources
    
    def get_categories(self) -> Dict:
        """Get category mapping."""
        return self.categories


# Global instance
blog_aggregator = BlogAggregator()


def get_latest_articles(limit: int = 20) -> List[Dict]:
    """Get latest articles from all sources."""
    articles = blog_aggregator.fetch_all()
    return articles[:limit]


def get_articles_by_topic(topic: str, limit: int = 10) -> List[Dict]:
    """Get articles by topic."""
    articles = blog_aggregator.get_by_topic(topic)
    return articles[:limit]


def get_blog_sources() -> List[Dict]:
    """Get all blog sources."""
    return blog_aggregator.get_sources()
