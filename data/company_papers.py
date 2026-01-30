"""
Company Research Papers Fetcher
Fetches latest research papers from major tech companies via arXiv and research blogs
"""
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
import xml.etree.ElementTree as ET
from urllib.parse import quote


class CompanyPapersFetcher:
    """Fetches latest papers from major tech companies."""
    
    def __init__(self):
        self.cache_file = Path(__file__).parent / "company_papers_cache.json"
        self.cache_duration = timedelta(hours=12)
        
        # Company research pages and arXiv search terms
        self.companies = {
            "google": {
                "name": "Google / DeepMind",
                "icon": "🔴",
                "research_blog": "https://blog.research.google/",
                "arxiv_search": "Google OR DeepMind",
                "arxiv_affiliation": ["Google", "DeepMind", "Google Research", "Google Brain"],
                "publications_page": "https://research.google/pubs/",
                "github": "https://github.com/google-research"
            },
            "meta": {
                "name": "Meta AI",
                "icon": "🔵",
                "research_blog": "https://ai.meta.com/blog/",
                "arxiv_search": "Meta AI OR Facebook AI",
                "arxiv_affiliation": ["Meta", "Facebook", "FAIR", "Meta AI"],
                "publications_page": "https://ai.meta.com/research/publications/",
                "github": "https://github.com/facebookresearch"
            },
            "openai": {
                "name": "OpenAI",
                "icon": "⬛",
                "research_blog": "https://openai.com/research",
                "arxiv_search": "OpenAI",
                "arxiv_affiliation": ["OpenAI"],
                "publications_page": "https://openai.com/research",
                "github": "https://github.com/openai"
            },
            "anthropic": {
                "name": "Anthropic",
                "icon": "🟤",
                "research_blog": "https://www.anthropic.com/research",
                "arxiv_search": "Anthropic",
                "arxiv_affiliation": ["Anthropic"],
                "publications_page": "https://www.anthropic.com/research",
                "github": "https://github.com/anthropics"
            },
            "microsoft": {
                "name": "Microsoft Research",
                "icon": "🟢",
                "research_blog": "https://www.microsoft.com/en-us/research/blog/",
                "arxiv_search": "Microsoft Research",
                "arxiv_affiliation": ["Microsoft", "Microsoft Research"],
                "publications_page": "https://www.microsoft.com/en-us/research/publications/",
                "github": "https://github.com/microsoft"
            },
            "amazon": {
                "name": "Amazon Science",
                "icon": "🟠",
                "research_blog": "https://www.amazon.science/blog",
                "arxiv_search": "Amazon",
                "arxiv_affiliation": ["Amazon", "AWS", "Alexa AI"],
                "publications_page": "https://www.amazon.science/publications",
                "github": "https://github.com/amazon-science"
            },
            "nvidia": {
                "name": "NVIDIA Research",
                "icon": "🟩",
                "research_blog": "https://blogs.nvidia.com/blog/category/deep-learning/",
                "arxiv_search": "NVIDIA",
                "arxiv_affiliation": ["NVIDIA"],
                "publications_page": "https://research.nvidia.com/publications",
                "github": "https://github.com/NVlabs"
            },
            "apple": {
                "name": "Apple ML Research",
                "icon": "⚫",
                "research_blog": "https://machinelearning.apple.com/",
                "arxiv_search": "Apple",
                "arxiv_affiliation": ["Apple"],
                "publications_page": "https://machinelearning.apple.com/research",
                "github": "https://github.com/apple"
            },
            "bytedance": {
                "name": "ByteDance Research",
                "icon": "⬜",
                "research_blog": "https://www.bytedance.com/en/research",
                "arxiv_search": "ByteDance OR TikTok",
                "arxiv_affiliation": ["ByteDance", "TikTok"],
                "publications_page": "https://www.bytedance.com/en/research",
                "github": "https://github.com/bytedance"
            },
            "huggingface": {
                "name": "Hugging Face",
                "icon": "🤗",
                "research_blog": "https://huggingface.co/blog",
                "arxiv_search": "Hugging Face",
                "arxiv_affiliation": ["Hugging Face"],
                "publications_page": "https://huggingface.co/papers",
                "github": "https://github.com/huggingface"
            },
            # ========== 中国科技公司 ==========
            "alibaba": {
                "name": "阿里巴巴 / 达摩院",
                "icon": "🟧",
                "research_blog": "https://damo.alibaba.com/",
                "arxiv_search": "Alibaba OR DAMO Academy",
                "arxiv_affiliation": ["Alibaba", "DAMO Academy", "Aliyun", "Taobao"],
                "publications_page": "https://damo.alibaba.com/labs/",
                "github": "https://github.com/alibaba"
            },
            "tencent": {
                "name": "腾讯 AI Lab",
                "icon": "🟦",
                "research_blog": "https://ai.tencent.com/ailab/",
                "arxiv_search": "Tencent",
                "arxiv_affiliation": ["Tencent", "Tencent AI Lab", "WeChat"],
                "publications_page": "https://ai.tencent.com/ailab/zh/paper",
                "github": "https://github.com/Tencent"
            },
            "baidu": {
                "name": "百度研究院",
                "icon": "🔷",
                "research_blog": "https://research.baidu.com/",
                "arxiv_search": "Baidu",
                "arxiv_affiliation": ["Baidu", "Baidu Research"],
                "publications_page": "https://research.baidu.com/Research_Areas?id=55",
                "github": "https://github.com/PaddlePaddle"
            },
            "kuaishou": {
                "name": "快手",
                "icon": "📹",
                "research_blog": "https://www.kuaishou.com/en/about-us",
                "arxiv_search": "Kuaishou OR Kwai",
                "arxiv_affiliation": ["Kuaishou", "Kwai"],
                "publications_page": "https://www.kuaishou.com/",
                "github": "https://github.com/nicklhy"
            },
            "xiaohongshu": {
                "name": "小红书 (RED/Xiaohongshu)",
                "icon": "📕",
                "research_blog": "https://www.xiaohongshu.com/",
                "arxiv_search": "Xiaohongshu OR RED",
                "arxiv_affiliation": ["Xiaohongshu", "RED"],
                "publications_page": "https://www.xiaohongshu.com/",
                "github": "https://github.com/xiaohongshu"
            },
            "jd": {
                "name": "京东 AI 研究院",
                "icon": "🔴",
                "research_blog": "https://air.jd.com/",
                "arxiv_search": "JD.com OR JingDong",
                "arxiv_affiliation": ["JD.com", "JD", "JD AI"],
                "publications_page": "https://air.jd.com/",
                "github": "https://github.com/jd-opensource"
            },
            "meituan": {
                "name": "美团技术",
                "icon": "🟡",
                "research_blog": "https://tech.meituan.com/",
                "arxiv_search": "Meituan",
                "arxiv_affiliation": ["Meituan"],
                "publications_page": "https://tech.meituan.com/",
                "github": "https://github.com/Meituan"
            },
            "didi": {
                "name": "滴滴 AI Labs",
                "icon": "🟠",
                "research_blog": "https://www.didiglobal.com/science/ailabs",
                "arxiv_search": "DiDi OR Didi Chuxing",
                "arxiv_affiliation": ["DiDi", "Didi Chuxing", "DiDi AI Labs"],
                "publications_page": "https://www.didiglobal.com/science/ailabs",
                "github": "https://github.com/didi"
            },
            "pinduoduo": {
                "name": "拼多多",
                "icon": "🟥",
                "research_blog": "https://www.pinduoduo.com/",
                "arxiv_search": "Pinduoduo OR PDD",
                "arxiv_affiliation": ["Pinduoduo", "PDD"],
                "publications_page": "https://www.pinduoduo.com/",
                "github": "https://github.com/pdd-ai"
            },
            "douyin": {
                "name": "抖音/TikTok (字节跳动)",
                "icon": "🎵",
                "research_blog": "https://www.bytedance.com/en/research",
                "arxiv_search": "Douyin OR TikTok OR ByteDance",
                "arxiv_affiliation": ["Douyin", "TikTok", "ByteDance"],
                "publications_page": "https://www.bytedance.com/en/research",
                "github": "https://github.com/bytedance"
            },
            "netease": {
                "name": "网易伏羲 AI Lab",
                "icon": "🎮",
                "research_blog": "https://fuxi.163.com/",
                "arxiv_search": "NetEase OR Fuxi",
                "arxiv_affiliation": ["NetEase", "Fuxi AI Lab"],
                "publications_page": "https://fuxi.163.com/",
                "github": "https://github.com/netease"
            },
            "sensetime": {
                "name": "商汤科技",
                "icon": "👁️",
                "research_blog": "https://www.sensetime.com/en/research/",
                "arxiv_search": "SenseTime",
                "arxiv_affiliation": ["SenseTime"],
                "publications_page": "https://www.sensetime.com/en/research/",
                "github": "https://github.com/open-mmlab"
            }
        }
        
        # arXiv API base URL
        self.arxiv_api = "http://export.arxiv.org/api/query"
    
    def fetch_arxiv_by_affiliation(self, company_id: str, max_results: int = 10) -> List[Dict]:
        """Fetch papers from arXiv by company affiliation."""
        if company_id not in self.companies:
            return []
        
        company = self.companies[company_id]
        search_term = company.get("arxiv_search", company["name"])
        
        try:
            # Search arXiv for recent papers with company affiliation
            params = {
                "search_query": f"all:{search_term}",
                "sortBy": "submittedDate",
                "sortOrder": "descending",
                "max_results": max_results
            }
            
            response = requests.get(self.arxiv_api, params=params, timeout=30)
            
            if response.status_code == 200:
                return self._parse_arxiv_response(response.text, company_id)
        except Exception as e:
            print(f"arXiv fetch error for {company_id}: {e}")
        
        return []
    
    def _parse_arxiv_response(self, xml_text: str, company_id: str) -> List[Dict]:
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
                
                paper = {
                    "title": title.text.strip().replace("\n", " ") if title is not None else "",
                    "abstract": summary.text.strip()[:500] if summary is not None else "",
                    "url": link.text if link is not None else "",
                    "published": published.text[:10] if published is not None else "",
                    "authors": authors[:5],
                    "company": company_id,
                    "source": "arXiv"
                }
                papers.append(paper)
        except Exception as e:
            print(f"arXiv parse error: {e}")
        
        return papers
    
    def get_company_info(self, company_id: str) -> Dict:
        """Get company research information."""
        return self.companies.get(company_id, {})
    
    def get_all_companies(self) -> Dict[str, Dict]:
        """Get all company research info."""
        return self.companies
    
    def get_research_links(self) -> Dict[str, Dict]:
        """Get all company research blog and publication links."""
        links = {}
        for company_id, info in self.companies.items():
            links[company_id] = {
                "name": info["name"],
                "icon": info["icon"],
                "research_blog": info.get("research_blog", ""),
                "publications": info.get("publications_page", ""),
                "github": info.get("github", ""),
                "arxiv_search": f"https://arxiv.org/search/?searchtype=all&query={quote(info.get('arxiv_search', info['name']))}&source=header"
            }
        return links
    
    def _load_cache(self) -> Dict:
        """Load cached papers."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    cache = json.load(f)
                
                cached_time = datetime.fromisoformat(cache.get("timestamp", "2000-01-01"))
                if datetime.now() - cached_time < self.cache_duration:
                    return cache.get("data", {})
            except Exception:
                pass
        return {}
    
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
    
    def fetch_all_company_papers(self, force_refresh: bool = False) -> Dict:
        """Fetch papers from all companies."""
        
        # Check cache
        if not force_refresh:
            cached = self._load_cache()
            if cached:
                return cached
        
        result = {
            "last_updated": datetime.now().isoformat(),
            "companies": {}
        }
        
        for company_id in self.companies:
            print(f"Fetching papers for {company_id}...")
            papers = self.fetch_arxiv_by_affiliation(company_id, max_results=5)
            result["companies"][company_id] = papers
        
        # Save to cache
        self._save_cache(result)
        
        return result


# Global instance
company_papers = CompanyPapersFetcher()


def get_company_research_links() -> Dict:
    """Get all company research links."""
    return company_papers.get_research_links()


def fetch_company_papers(company_id: str) -> List[Dict]:
    """Fetch papers for a specific company."""
    return company_papers.fetch_arxiv_by_affiliation(company_id)


def fetch_all_papers(force_refresh: bool = False) -> Dict:
    """Fetch papers from all companies."""
    return company_papers.fetch_all_company_papers(force_refresh)
