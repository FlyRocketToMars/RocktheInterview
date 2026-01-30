"""
Latest Papers Fetcher
Fetches latest ML/AI papers from arXiv, Papers With Code, and Semantic Scholar
"""
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import xml.etree.ElementTree as ET


class ArxivFetcher:
    """Fetch latest papers from arXiv API."""
    
    BASE_URL = "http://export.arxiv.org/api/query"
    
    # Categories relevant to MLE
    CATEGORIES = {
        "cs.LG": "Machine Learning",
        "cs.CL": "NLP/Computation and Language",
        "cs.CV": "Computer Vision",
        "cs.AI": "Artificial Intelligence",
        "cs.IR": "Information Retrieval",
        "stat.ML": "Statistical ML"
    }
    
    def fetch_latest(self, category: str = "cs.LG", max_results: int = 20) -> List[Dict]:
        """Fetch latest papers from a category."""
        try:
            params = {
                "search_query": f"cat:{category}",
                "sortBy": "submittedDate",
                "sortOrder": "descending",
                "max_results": max_results
            }
            
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            
            if response.status_code == 200:
                return self._parse_arxiv_response(response.text)
        except Exception as e:
            print(f"arXiv fetch error: {e}")
        
        return []
    
    def _parse_arxiv_response(self, xml_text: str) -> List[Dict]:
        """Parse arXiv API XML response."""
        papers = []
        
        try:
            root = ET.fromstring(xml_text)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            
            for entry in root.findall("atom:entry", ns):
                title = entry.find("atom:title", ns)
                summary = entry.find("atom:summary", ns)
                published = entry.find("atom:published", ns)
                link = entry.find("atom:id", ns)
                
                # Get authors
                authors = []
                for author in entry.findall("atom:author", ns):
                    name = author.find("atom:name", ns)
                    if name is not None:
                        authors.append(name.text)
                
                # Get categories
                categories = []
                for cat in entry.findall("atom:category", ns):
                    term = cat.get("term")
                    if term:
                        categories.append(term)
                
                paper = {
                    "title": title.text.strip().replace("\n", " ") if title is not None else "",
                    "abstract": summary.text.strip()[:500] if summary is not None else "",
                    "url": link.text if link is not None else "",
                    "published": published.text[:10] if published is not None else "",
                    "authors": authors[:5],  # Limit to first 5 authors
                    "categories": categories,
                    "source": "arXiv"
                }
                papers.append(paper)
        except Exception as e:
            print(f"arXiv parse error: {e}")
        
        return papers
    
    def fetch_hot_topics(self) -> Dict[str, List[Dict]]:
        """Fetch latest papers for all relevant categories."""
        results = {}
        
        for cat_id, cat_name in self.CATEGORIES.items():
            papers = self.fetch_latest(cat_id, max_results=10)
            if papers:
                results[cat_name] = papers
        
        return results


class PapersWithCodeFetcher:
    """Fetch trending papers from Papers With Code."""
    
    BASE_URL = "https://paperswithcode.com/api/v1"
    
    def fetch_trending(self, limit: int = 20) -> List[Dict]:
        """Fetch trending papers."""
        try:
            # Papers With Code API for trending papers
            response = requests.get(
                f"{self.BASE_URL}/papers/",
                params={"ordering": "-proceeding", "items_per_page": limit},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                papers = []
                
                for item in data.get("results", [])[:limit]:
                    paper = {
                        "title": item.get("title", ""),
                        "abstract": item.get("abstract", "")[:500],
                        "url": f"https://paperswithcode.com{item.get('url_abs', '')}",
                        "arxiv_id": item.get("arxiv_id", ""),
                        "published": item.get("published", ""),
                        "source": "Papers With Code"
                    }
                    papers.append(paper)
                
                return papers
        except Exception as e:
            print(f"Papers With Code fetch error: {e}")
        
        return []


class HuggingFaceDailyPapers:
    """Fetch daily papers from Hugging Face."""
    
    BASE_URL = "https://huggingface.co/api/daily_papers"
    
    def fetch_daily(self) -> List[Dict]:
        """Fetch today's papers from Hugging Face."""
        try:
            response = requests.get(self.BASE_URL, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                papers = []
                
                for item in data:
                    paper = {
                        "title": item.get("title", ""),
                        "abstract": item.get("summary", "")[:500],
                        "url": f"https://huggingface.co/papers/{item.get('paper', {}).get('id', '')}",
                        "upvotes": item.get("paper", {}).get("upvotes", 0),
                        "published": datetime.now().strftime("%Y-%m-%d"),
                        "source": "Hugging Face Daily"
                    }
                    papers.append(paper)
                
                return papers
        except Exception as e:
            print(f"Hugging Face fetch error: {e}")
        
        return []


class LatestPapersAggregator:
    """Aggregates papers from multiple sources."""
    
    def __init__(self):
        self.arxiv = ArxivFetcher()
        self.pwc = PapersWithCodeFetcher()
        self.hf = HuggingFaceDailyPapers()
        self.cache_file = Path(__file__).parent / "latest_papers_cache.json"
        self.cache_duration = timedelta(hours=6)  # Refresh every 6 hours
    
    def _load_cache(self) -> Optional[Dict]:
        """Load cached papers if still valid."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    cache = json.load(f)
                
                cached_time = datetime.fromisoformat(cache.get("timestamp", "2000-01-01"))
                if datetime.now() - cached_time < self.cache_duration:
                    return cache.get("data")
            except Exception:
                pass
        return None
    
    def _save_cache(self, data: Dict):
        """Save papers to cache."""
        try:
            cache = {
                "timestamp": datetime.now().isoformat(),
                "data": data
            }
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Cache save error: {e}")
    
    def get_latest_papers(self, force_refresh: bool = False) -> Dict:
        """Get latest papers from all sources."""
        
        # Check cache first
        if not force_refresh:
            cached = self._load_cache()
            if cached:
                return cached
        
        # Fetch from all sources
        result = {
            "last_updated": datetime.now().isoformat(),
            "sources": {
                "arxiv": {},
                "huggingface": [],
                "papers_with_code": []
            }
        }
        
        # arXiv - by category
        print("Fetching from arXiv...")
        result["sources"]["arxiv"] = self.arxiv.fetch_hot_topics()
        
        # Hugging Face Daily Papers
        print("Fetching from Hugging Face...")
        result["sources"]["huggingface"] = self.hf.fetch_daily()
        
        # Papers With Code
        print("Fetching from Papers With Code...")
        result["sources"]["papers_with_code"] = self.pwc.fetch_trending()
        
        # Save to cache
        self._save_cache(result)
        
        return result
    
    def get_hot_papers_summary(self) -> Dict:
        """Get a summary of hot papers for display."""
        data = self.get_latest_papers()
        
        summary = {
            "last_updated": data.get("last_updated", ""),
            "total_papers": 0,
            "by_category": {},
            "top_papers": []
        }
        
        # Count papers by category
        arxiv_data = data.get("sources", {}).get("arxiv", {})
        for cat_name, papers in arxiv_data.items():
            summary["by_category"][cat_name] = len(papers)
            summary["total_papers"] += len(papers)
            
            # Add top 3 from each category
            for paper in papers[:3]:
                paper["category"] = cat_name
                summary["top_papers"].append(paper)
        
        # Add Hugging Face daily papers
        hf_papers = data.get("sources", {}).get("huggingface", [])
        summary["by_category"]["Hugging Face Daily"] = len(hf_papers)
        summary["total_papers"] += len(hf_papers)
        
        # Sort by date
        summary["top_papers"] = sorted(
            summary["top_papers"],
            key=lambda x: x.get("published", ""),
            reverse=True
        )[:20]
        
        return summary


# Global instance
papers_aggregator = LatestPapersAggregator()


def get_latest_ml_papers() -> Dict:
    """Get latest ML papers."""
    return papers_aggregator.get_latest_papers()


def get_hot_papers() -> Dict:
    """Get hot papers summary."""
    return papers_aggregator.get_hot_papers_summary()


def refresh_papers() -> Dict:
    """Force refresh papers."""
    return papers_aggregator.get_latest_papers(force_refresh=True)
