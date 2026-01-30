"""
Daily Job Feeds Aggregator
Provides links to latest MLE job postings from legitimate job platforms
"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
from urllib.parse import quote


class JobFeedsAggregator:
    """Aggregates job feeds from various legitimate job platforms."""
    
    def __init__(self):
        self.cache_file = Path(__file__).parent / "job_feeds_cache.json"
        
        # Job search URLs for MLE positions - these are legitimate search links
        self.job_platforms = {
            "linkedin": {
                "name": "LinkedIn Jobs",
                "icon": "💼",
                "base_url": "https://www.linkedin.com/jobs/search/",
                "mle_search": "https://www.linkedin.com/jobs/search/?keywords=machine%20learning%20engineer&f_TPR=r86400",  # Last 24 hours
                "filters": {
                    "last_24h": "&f_TPR=r86400",
                    "last_week": "&f_TPR=r604800",
                    "remote": "&f_WT=2"
                }
            },
            "indeed": {
                "name": "Indeed",
                "icon": "🔍",
                "base_url": "https://www.indeed.com/jobs",
                "mle_search": "https://www.indeed.com/jobs?q=machine+learning+engineer&fromage=1",  # Last day
                "filters": {
                    "last_24h": "&fromage=1",
                    "last_week": "&fromage=7",
                    "remote": "&remotejob=032b3046-06a3-4876-8dfd-474eb5e7ed11"
                }
            },
            "glassdoor": {
                "name": "Glassdoor",
                "icon": "🚪",
                "base_url": "https://www.glassdoor.com/Job/",
                "mle_search": "https://www.glassdoor.com/Job/machine-learning-engineer-jobs-SRCH_KO0,25.htm?fromAge=1",
                "filters": {}
            },
            "levels_fyi": {
                "name": "levels.fyi Jobs",
                "icon": "📊",
                "base_url": "https://www.levels.fyi/jobs",
                "mle_search": "https://www.levels.fyi/jobs?title=Machine%20Learning%20Engineer",
                "filters": {}
            },
            "wellfound": {
                "name": "Wellfound (AngelList)",
                "icon": "🚀",
                "base_url": "https://wellfound.com/",
                "mle_search": "https://wellfound.com/role/machine-learning-engineer",
                "filters": {}
            },
            "ycombinator": {
                "name": "Y Combinator",
                "icon": "🌟",
                "base_url": "https://www.workatastartup.com/",
                "mle_search": "https://www.workatastartup.com/jobs?q=machine%20learning",
                "filters": {}
            },
            "builtin": {
                "name": "Built In",
                "icon": "🏗️",
                "base_url": "https://builtin.com/",
                "mle_search": "https://builtin.com/jobs?search=machine%20learning%20engineer",
                "filters": {}
            },
            "ai_jobs": {
                "name": "AI Jobs",
                "icon": "🤖",
                "base_url": "https://aijobs.net/",
                "mle_search": "https://aijobs.net/",
                "filters": {}
            },
            "huggingface": {
                "name": "Hugging Face Jobs",
                "icon": "🤗",
                "base_url": "https://huggingface.co/jobs",
                "mle_search": "https://apply.workable.com/huggingface/",
                "filters": {}
            }
        }
        
        # Company-specific career pages with MLE search
        self.company_job_links = {
            "google": {
                "name": "Google",
                "url": "https://careers.google.com/jobs/results/?q=machine%20learning",
                "icon": "🔴"
            },
            "meta": {
                "name": "Meta",
                "url": "https://www.metacareers.com/jobs?q=machine%20learning%20engineer",
                "icon": "🔵"
            },
            "amazon": {
                "name": "Amazon",
                "url": "https://www.amazon.jobs/en/search?base_query=machine+learning+engineer",
                "icon": "🟠"
            },
            "microsoft": {
                "name": "Microsoft",
                "url": "https://careers.microsoft.com/v2/global/en/search?q=machine%20learning",
                "icon": "🟢"
            },
            "apple": {
                "name": "Apple",
                "url": "https://jobs.apple.com/en-us/search?search=machine%20learning",
                "icon": "⚫"
            },
            "openai": {
                "name": "OpenAI",
                "url": "https://openai.com/careers/search?q=",
                "icon": "⬛"
            },
            "anthropic": {
                "name": "Anthropic",
                "url": "https://www.anthropic.com/careers#open-roles",
                "icon": "🟤"
            },
            "nvidia": {
                "name": "NVIDIA",
                "url": "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite?q=machine%20learning",
                "icon": "🟩"
            },
            "netflix": {
                "name": "Netflix",
                "url": "https://jobs.netflix.com/search?q=machine%20learning",
                "icon": "🔴"
            },
            "bytedance": {
                "name": "ByteDance/TikTok",
                "url": "https://jobs.bytedance.com/en/position?keywords=machine%20learning",
                "icon": "⬜"
            },
            "stripe": {
                "name": "Stripe",
                "url": "https://stripe.com/jobs/search?q=machine+learning",
                "icon": "🟣"
            },
            "uber": {
                "name": "Uber",
                "url": "https://www.uber.com/us/en/careers/list/?query=machine%20learning",
                "icon": "⚪"
            },
            "airbnb": {
                "name": "Airbnb",
                "url": "https://careers.airbnb.com/positions/?query=machine%20learning",
                "icon": "🔴"
            },
            "spotify": {
                "name": "Spotify",
                "url": "https://www.lifeatspotify.com/jobs?query=machine%20learning",
                "icon": "🟢"
            },
            "databricks": {
                "name": "Databricks",
                "url": "https://www.databricks.com/company/careers/open-positions?department=Engineering",
                "icon": "🟥"
            }
        }
        
        # Specialized job search queries
        self.specialized_searches = {
            "llm_engineer": {
                "name": "LLM Engineer",
                "linkedin": "https://www.linkedin.com/jobs/search/?keywords=LLM%20engineer&f_TPR=r86400",
                "indeed": "https://www.indeed.com/jobs?q=LLM+engineer&fromage=1"
            },
            "ml_infra": {
                "name": "ML Infrastructure",
                "linkedin": "https://www.linkedin.com/jobs/search/?keywords=ML%20infrastructure%20engineer&f_TPR=r86400",
                "indeed": "https://www.indeed.com/jobs?q=ML+infrastructure+engineer&fromage=1"
            },
            "recommendation": {
                "name": "Recommendation Systems",
                "linkedin": "https://www.linkedin.com/jobs/search/?keywords=recommendation%20systems%20engineer&f_TPR=r86400",
                "indeed": "https://www.indeed.com/jobs?q=recommendation+system+engineer&fromage=1"
            },
            "nlp_engineer": {
                "name": "NLP Engineer",
                "linkedin": "https://www.linkedin.com/jobs/search/?keywords=NLP%20engineer&f_TPR=r86400",
                "indeed": "https://www.indeed.com/jobs?q=NLP+engineer&fromage=1"
            },
            "cv_engineer": {
                "name": "Computer Vision",
                "linkedin": "https://www.linkedin.com/jobs/search/?keywords=computer%20vision%20engineer&f_TPR=r86400",
                "indeed": "https://www.indeed.com/jobs?q=computer+vision+engineer&fromage=1"
            },
            "mlops": {
                "name": "MLOps Engineer",
                "linkedin": "https://www.linkedin.com/jobs/search/?keywords=MLOps%20engineer&f_TPR=r86400",
                "indeed": "https://www.indeed.com/jobs?q=MLOps+engineer&fromage=1"
            },
            "research_scientist": {
                "name": "Research Scientist",
                "linkedin": "https://www.linkedin.com/jobs/search/?keywords=research%20scientist%20machine%20learning&f_TPR=r86400",
                "indeed": "https://www.indeed.com/jobs?q=research+scientist+machine+learning&fromage=1"
            },
            "applied_scientist": {
                "name": "Applied Scientist",
                "linkedin": "https://www.linkedin.com/jobs/search/?keywords=applied%20scientist&f_TPR=r86400",
                "indeed": "https://www.indeed.com/jobs?q=applied+scientist&fromage=1"
            }
        }
    
    def get_daily_job_links(self) -> Dict:
        """Get all job links for today."""
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "platforms": self.job_platforms,
            "companies": self.company_job_links,
            "specialized": self.specialized_searches
        }
    
    def get_platform_links(self) -> Dict[str, Dict]:
        """Get job platform links."""
        return self.job_platforms
    
    def get_company_links(self) -> Dict[str, Dict]:
        """Get company career page links."""
        return self.company_job_links
    
    def get_specialized_searches(self) -> Dict[str, Dict]:
        """Get specialized job searches."""
        return self.specialized_searches
    
    def build_custom_search_url(self, platform: str, keywords: str, location: str = "", remote: bool = False) -> str:
        """Build a custom job search URL."""
        keywords_encoded = quote(keywords)
        location_encoded = quote(location) if location else ""
        
        if platform == "linkedin":
            url = f"https://www.linkedin.com/jobs/search/?keywords={keywords_encoded}"
            if location:
                url += f"&location={location_encoded}"
            if remote:
                url += "&f_WT=2"
            url += "&f_TPR=r86400"  # Last 24 hours
            return url
        
        elif platform == "indeed":
            url = f"https://www.indeed.com/jobs?q={keywords_encoded}&fromage=1"
            if location:
                url += f"&l={location_encoded}"
            if remote:
                url += "&remotejob=032b3046-06a3-4876-8dfd-474eb5e7ed11"
            return url
        
        elif platform == "glassdoor":
            return f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={keywords_encoded}"
        
        return ""


# Global instance
job_feeds = JobFeedsAggregator()


def get_daily_jobs() -> Dict:
    """Get daily job links."""
    return job_feeds.get_daily_job_links()


def get_custom_search(keywords: str, platform: str = "linkedin", location: str = "", remote: bool = False) -> str:
    """Get custom job search URL."""
    return job_feeds.build_custom_search_url(platform, keywords, location, remote)
