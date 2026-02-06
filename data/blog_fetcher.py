"""
Blog Fetcher - Fetch technical blogs from various sources
Includes Alex Xu's System Design blog and other tech influencers
"""
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import feedparser
import time

class BlogFetcher:
    """Fetch and parse technical blogs from various sources."""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent
        self.cache_file = self.data_dir / "blog_cache.json"
        self.cache_duration = 3600 * 24  # 24 hours
        
        # Blog sources configuration
        self.sources = {
            "alex_xu": {
                "name": "Alex Xu - System Design",
                "url": "https://blog.bytebytego.com/",
                "rss": "https://blog.bytebytego.com/feed",
                "type": "system_design",
                "priority": "high"
            },
            "martin_fowler": {
                "name": "Martin Fowler",
                "url": "https://martinfowler.com/",
                "rss": "https://martinfowler.com/feed.atom",
                "type": "architecture",
                "priority": "high"
            },
            "netflix_tech": {
                "name": "Netflix Tech Blog",
                "url": "https://netflixtechblog.com/",
                "rss": "https://netflixtechblog.com/feed",
                "type": "ml_systems",
                "priority": "high"
            },
            "uber_eng": {
                "name": "Uber Engineering",
                "url": "https://www.uber.com/blog/engineering/",
                "rss": "https://www.uber.com/blog/engineering/rss/",
                "type": "ml_systems",
                "priority": "high"
            },
            "meta_ai": {
                "name": "Meta AI Blog",
                "url": "https://ai.meta.com/blog/",
                "type": "ml_research",
                "priority": "high"
            },
            "openai_blog": {
                "name": "OpenAI Blog",
                "url": "https://openai.com/blog/",
                "type": "llm",
                "priority": "high"
            },
            "google_ai": {
                "name": "Google AI Blog",
                "url": "https://ai.googleblog.com/",
                "rss": "https://ai.googleblog.com/feeds/posts/default",
                "type": "ml_research",
                "priority": "high"
            }
        }
    
    def fetch_from_rss(self, source_key: str) -> List[Dict]:
        """Fetch blog posts from RSS feed."""
        source = self.sources.get(source_key)
        if not source or "rss" not in source:
            return []
        
        try:
            feed = feedparser.parse(source["rss"])
            posts = []
            
            for entry in feed.entries[:10]:  # Get latest 10 posts
                post = {
                    "source": source_key,
                    "source_name": source["name"],
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "summary": entry.get("summary", "") or entry.get("description", ""),
                    "published": entry.get("published", ""),
                    "type": source["type"],
                    "priority": source["priority"],
                    "fetched_at": datetime.now().isoformat()
                }
                posts.append(post)
            
            return posts
        except Exception as e:
            print(f"Error fetching RSS for {source_key}: {e}")
            return []
    
    def fetch_alex_xu_posts(self) -> List[Dict]:
        """
        Fetch Alex Xu's System Design posts.
        These are high-value for ML System Design interviews.
        """
        posts = self.fetch_from_rss("alex_xu")
        
        # Add some curated Alex Xu topics if RSS fails
        if not posts:
            posts = [
                {
                    "source": "alex_xu",
                    "source_name": "Alex Xu - System Design",
                    "title": "Design YouTube",
                    "url": "https://blog.bytebytego.com/",
                    "summary": "How to design a video streaming platform like YouTube with focus on video upload, processing, CDN, and recommendation system.",
                    "type": "system_design",
                    "priority": "high",
                    "fetched_at": datetime.now().isoformat()
                },
                {
                    "source": "alex_xu",
                    "source_name": "Alex Xu - System Design",
                    "title": "Design a Rate Limiter",
                    "url": "https://blog.bytebytego.com/",
                    "summary": "Different algorithms for rate limiting: Token Bucket, Leaky Bucket, Fixed Window, Sliding Window.",
                    "type": "system_design",
                    "priority": "high",
                    "fetched_at": datetime.now().isoformat()
                },
                {
                    "source": "alex_xu",
                    "source_name": "Alex Xu - System Design",
                    "title": "Design a News Feed System",
                    "url": "https://blog.bytebytego.com/",
                    "summary": "How to design a personalized news feed like Facebook/Instagram with ranking, caching, and real-time updates.",
                    "type": "system_design",
                    "priority": "high",
                    "fetched_at": datetime.now().isoformat()
                }
            ]
        
        return posts
    
    def fetch_all_sources(self) -> Dict[str, List[Dict]]:
        """Fetch from all configured sources."""
        all_posts = {}
        
        for source_key in self.sources:
            print(f"Fetching from {source_key}...")
            if source_key == "alex_xu":
                posts = self.fetch_alex_xu_posts()
            else:
                posts = self.fetch_from_rss(source_key)
            
            if posts:
                all_posts[source_key] = posts
            
            # Rate limiting
            time.sleep(1)
        
        return all_posts
    
    def get_cached_posts(self) -> Optional[Dict]:
        """Get cached blog posts if still fresh."""
        if not self.cache_file.exists():
            return None
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache = json.load(f)
            
            cached_time = datetime.fromisoformat(cache.get("cached_at", ""))
            if (datetime.now() - cached_time).total_seconds() < self.cache_duration:
                return cache.get("posts", {})
        except:
            pass
        
        return None
    
    def save_cache(self, posts: Dict):
        """Save fetched posts to cache."""
        cache_data = {
            "cached_at": datetime.now().isoformat(),
            "posts": posts
        }
        
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    
    def get_latest_posts(self, force_refresh: bool = False) -> Dict[str, List[Dict]]:
        """Get latest blog posts (with caching)."""
        if not force_refresh:
            cached = self.get_cached_posts()
            if cached:
                return cached
        
        # Fetch fresh data
        posts = self.fetch_all_sources()
        self.save_cache(posts)
        return posts
    
    def get_posts_by_type(self, post_type: str) -> List[Dict]:
        """Get posts filtered by type (system_design, ml_research, llm, etc)."""
        all_posts = self.get_latest_posts()
        filtered = []
        
        for source_posts in all_posts.values():
            for post in source_posts:
                if post.get("type") == post_type:
                    filtered.append(post)
        
        return filtered


# Global instance
blog_fetcher = BlogFetcher()


if __name__ == "__main__":
    # Test fetching
    fetcher = BlogFetcher()
    print("Fetching Alex Xu posts...")
    alex_posts = fetcher.fetch_alex_xu_posts()
    for post in alex_posts:
        print(f"- {post['title']}")
    
    print("\nFetching all sources...")
    all_posts = fetcher.get_latest_posts(force_refresh=True)
    for source, posts in all_posts.items():
        print(f"\n{source}: {len(posts)} posts")
