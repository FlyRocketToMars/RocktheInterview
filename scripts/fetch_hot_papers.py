"""
Script to fetch hot papers from arXiv, HuggingFace Daily Papers, Papers With Code,
and save them into data/hot_papers.json for the app to display.
Designed to run as a GitHub Action daily.
"""
import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path

OUTPUT_FILE = Path(__file__).parent.parent / "data" / "hot_papers.json"

# ============ arXiv ============
ARXIV_CATEGORIES = {
    "cs.LG": "Machine Learning",
    "cs.CL": "NLP / Computation and Language",
    "cs.CV": "Computer Vision",
    "cs.AI": "Artificial Intelligence",
    "cs.IR": "Information Retrieval / RecSys",
    "stat.ML": "Statistical ML",
}

def fetch_arxiv(category, max_results=30):
    """Fetch latest papers from arXiv API."""
    url = f"http://export.arxiv.org/api/query?search_query=cat:{category}&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code != 200:
            return []
        root = ET.fromstring(resp.text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        papers = []
        for entry in root.findall("atom:entry", ns):
            title = entry.find("atom:title", ns).text.strip().replace("\n", " ")
            abstract = entry.find("atom:summary", ns).text.strip()[:500]
            link = entry.find("atom:id", ns).text.strip()
            published = entry.find("atom:published", ns).text[:10]
            authors = [a.find("atom:name", ns).text for a in entry.findall("atom:author", ns)][:5]
            papers.append({
                "title": title,
                "url": link,
                "abstract": abstract,
                "authors": authors,
                "published": published,
                "source": "arXiv",
                "category": ARXIV_CATEGORIES.get(category, category),
                "arxiv_category": category,
            })
        return papers
    except Exception as e:
        print(f"  [ERROR] arXiv {category}: {e}")
        return []

# ============ HuggingFace Daily Papers ============
def fetch_huggingface_daily():
    """Fetch daily papers from Hugging Face."""
    try:
        resp = requests.get("https://huggingface.co/api/daily_papers", timeout=15)
        if resp.status_code != 200:
            return []
        data = resp.json()
        papers = []
        for item in data[:30]:
            paper = item.get("paper", {})
            papers.append({
                "title": paper.get("title", ""),
                "url": f"https://huggingface.co/papers/{paper.get('id', '')}",
                "abstract": paper.get("summary", "")[:500],
                "authors": [a.get("name", "") for a in paper.get("authors", [])][:5],
                "published": paper.get("publishedAt", "")[:10],
                "source": "HuggingFace Daily",
                "category": "AI/ML (Trending)",
                "upvotes": item.get("paper", {}).get("upvotes", 0),
            })
        return papers
    except Exception as e:
        print(f"  [ERROR] HuggingFace: {e}")
        return []

# ============ Papers With Code (trending) ============
def fetch_papers_with_code(limit=30):
    """Fetch trending papers from Papers With Code."""
    try:
        resp = requests.get(f"https://paperswithcode.com/api/v1/papers/?ordering=-proceeding&items_per_page={limit}", timeout=15)
        if resp.status_code != 200:
            return []
        data = resp.json()
        papers = []
        for item in data.get("results", [])[:limit]:
            papers.append({
                "title": item.get("title", ""),
                "url": item.get("url_abs", item.get("paper_url", "")),
                "abstract": item.get("abstract", "")[:500],
                "authors": item.get("authors", [])[:5],
                "published": item.get("published", "")[:10],
                "source": "Papers With Code",
                "category": "ML (With Code)",
            })
        return papers
    except Exception as e:
        print(f"  [ERROR] Papers With Code: {e}")
        return []

# ============ Main ============
def main():
    print(f"{'='*60}")
    print(f"Hot Papers Fetcher - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")
    
    all_papers = []
    
    # 1. arXiv - all key categories
    for cat, name in ARXIV_CATEGORIES.items():
        print(f"[arXiv] Fetching {name} ({cat})...")
        papers = fetch_arxiv(cat, max_results=20)
        all_papers.extend(papers)
        print(f"  Got {len(papers)} papers")
    
    # 2. HuggingFace Daily (the best source for trending)
    print(f"[HuggingFace] Fetching daily papers...")
    hf_papers = fetch_huggingface_daily()
    all_papers.extend(hf_papers)
    print(f"  Got {len(hf_papers)} papers")
    
    # 3. Papers With Code
    print(f"[PapersWithCode] Fetching trending...")
    pwc_papers = fetch_papers_with_code(limit=20)
    all_papers.extend(pwc_papers)
    print(f"  Got {len(pwc_papers)} papers")
    
    # Dedup by title (case-insensitive)
    seen = set()
    deduped = []
    for p in all_papers:
        key = p["title"].lower().strip()
        if key not in seen and len(key) > 5:
            seen.add(key)
            deduped.append(p)
    
    # Load existing and merge
    if OUTPUT_FILE.exists():
        existing = json.load(open(OUTPUT_FILE, encoding="utf-8"))
        existing_titles = set(p["title"].lower().strip() for p in existing.get("top_papers", []))
        new_count = 0
        for p in deduped:
            if p["title"].lower().strip() not in existing_titles:
                existing["top_papers"].insert(0, p)
                new_count += 1
        existing["last_updated"] = datetime.now().isoformat()
        existing["total"] = len(existing["top_papers"])
        data = existing
    else:
        data = {
            "top_papers": deduped,
            "last_updated": datetime.now().isoformat(),
            "total": len(deduped)
        }
        new_count = len(deduped)
    
    # Keep max 500 papers (trim oldest)
    data["top_papers"] = data["top_papers"][:500]
    data["total"] = len(data["top_papers"])
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"Added {new_count} new papers. Total: {data['total']}")
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
