"""
Job Listings Aggregator
Scrapes and aggregates MLE job postings from major tech companies
Uses Gemini for intelligent classification and resume matching
"""
import json
import os
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


class JobListing:
    """Represents a single job listing."""
    
    def __init__(self, title: str, company: str, location: str, url: str,
                 level: str = "", requirements: List[str] = None,
                 description: str = "", posted_date: str = "",
                 salary_range: str = "", remote: bool = False):
        self.id = f"{company}_{title}_{datetime.now().strftime('%Y%m%d')}"
        self.title = title
        self.company = company
        self.location = location
        self.url = url
        self.level = level
        self.requirements = requirements or []
        self.description = description
        self.posted_date = posted_date
        self.salary_range = salary_range
        self.remote = remote
        self.categories = []  # Will be filled by Gemini
        self.skills_required = []  # Will be filled by Gemini
        self.match_score = 0.0  # For resume matching
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "url": self.url,
            "level": self.level,
            "requirements": self.requirements,
            "description": self.description,
            "posted_date": self.posted_date,
            "salary_range": self.salary_range,
            "remote": self.remote,
            "categories": self.categories,
            "skills_required": self.skills_required,
            "match_score": self.match_score
        }


class GeminiClassifier:
    """Uses Gemini API to classify jobs and match with resumes."""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    
    def classify_job(self, job: Dict) -> Dict:
        """Classify a job posting using Gemini."""
        if not self.api_key:
            return self._default_classification(job)
        
        prompt = f"""Analyze this job posting and extract structured information.

Job Title: {job.get('title', '')}
Company: {job.get('company', '')}
Description: {job.get('description', '')[:1000]}

Return a JSON object with:
1. "level": one of ["Entry", "Mid", "Senior", "Staff", "Principal"]
2. "categories": list of relevant categories from ["ML Infrastructure", "NLP/LLM", "Computer Vision", "Recommendation Systems", "Search/Ranking", "MLOps", "Research", "Applied ML", "Data Science"]
3. "skills_required": list of specific technical skills mentioned
4. "experience_years": estimated years of experience required (number)
5. "focus_areas": list of main technical focus areas

Return ONLY the JSON, no other text."""

        try:
            response = requests.post(
                f"{self.base_url}?key={self.api_key}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.1}
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                text = result["candidates"][0]["content"]["parts"][0]["text"]
                # Clean and parse JSON
                text = text.strip()
                if text.startswith("```"):
                    text = text.split("```")[1]
                    if text.startswith("json"):
                        text = text[4:]
                return json.loads(text)
        except Exception as e:
            print(f"Gemini classification error: {e}")
        
        return self._default_classification(job)
    
    def _default_classification(self, job: Dict) -> Dict:
        """Default classification when Gemini is unavailable."""
        title = job.get("title", "").lower()
        
        categories = []
        if "llm" in title or "nlp" in title or "language" in title:
            categories.append("NLP/LLM")
        if "infra" in title or "platform" in title:
            categories.append("ML Infrastructure")
        if "recommend" in title:
            categories.append("Recommendation Systems")
        if "vision" in title or "cv" in title:
            categories.append("Computer Vision")
        if "search" in title or "rank" in title:
            categories.append("Search/Ranking")
        if "research" in title:
            categories.append("Research")
        if not categories:
            categories.append("Applied ML")
        
        level = "Mid"
        if "senior" in title or "sr" in title:
            level = "Senior"
        elif "staff" in title or "principal" in title:
            level = "Staff"
        elif "entry" in title or "junior" in title or "new grad" in title:
            level = "Entry"
        
        return {
            "level": level,
            "categories": categories,
            "skills_required": ["Python", "Machine Learning", "Deep Learning"],
            "experience_years": 3,
            "focus_areas": categories
        }
    
    def match_resume_to_job(self, resume_text: str, job: Dict) -> float:
        """Calculate match score between a resume and job posting."""
        if not self.api_key:
            return self._simple_match(resume_text, job)
        
        prompt = f"""Compare this resume with the job posting and calculate a match score.

RESUME:
{resume_text[:2000]}

JOB POSTING:
Title: {job.get('title', '')}
Company: {job.get('company', '')}
Requirements: {', '.join(job.get('requirements', []))}
Description: {job.get('description', '')[:1000]}

Return a JSON object with:
1. "match_score": a number from 0 to 100 indicating how well the resume matches
2. "matching_skills": list of skills that match
3. "missing_skills": list of required skills missing from resume
4. "recommendation": brief recommendation for the candidate

Return ONLY the JSON."""

        try:
            response = requests.post(
                f"{self.base_url}?key={self.api_key}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.1}
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                text = result["candidates"][0]["content"]["parts"][0]["text"]
                text = text.strip()
                if text.startswith("```"):
                    text = text.split("```")[1]
                    if text.startswith("json"):
                        text = text[4:]
                data = json.loads(text)
                return data.get("match_score", 50) / 100
        except Exception as e:
            print(f"Gemini matching error: {e}")
        
        return self._simple_match(resume_text, job)
    
    def _simple_match(self, resume_text: str, job: Dict) -> float:
        """Simple keyword-based matching when Gemini is unavailable."""
        resume_lower = resume_text.lower()
        score = 0.0
        
        # Check for skill matches
        skills = job.get("skills_required", []) + job.get("requirements", [])
        matches = 0
        for skill in skills:
            if skill.lower() in resume_lower:
                matches += 1
        
        if skills:
            score = matches / len(skills)
        
        # Bonus for company mention
        if job.get("company", "").lower() in resume_lower:
            score += 0.1
        
        return min(score, 1.0)


class JobAggregator:
    """Aggregates job listings from various sources."""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent / "data"
        self.jobs_file = self.data_dir / "job_listings.json"
        self.classifier = GeminiClassifier()
        self._ensure_data_file()
        
        # Company career page URLs
        self.company_urls = {
            "google": {
                "name": "Google",
                "careers_url": "https://careers.google.com/jobs/results/?q=machine%20learning",
                "levels_url": "https://www.levels.fyi/companies/google/salaries/software-engineer"
            },
            "meta": {
                "name": "Meta",
                "careers_url": "https://www.metacareers.com/jobs?q=machine%20learning%20engineer",
                "levels_url": "https://www.levels.fyi/companies/facebook/salaries/software-engineer"
            },
            "amazon": {
                "name": "Amazon",
                "careers_url": "https://www.amazon.jobs/en/search?base_query=machine+learning",
                "levels_url": "https://www.levels.fyi/companies/amazon/salaries/software-engineer"
            },
            "microsoft": {
                "name": "Microsoft",
                "careers_url": "https://careers.microsoft.com/professionals/us/en/search-results?keywords=machine%20learning",
                "levels_url": "https://www.levels.fyi/companies/microsoft/salaries/software-engineer"
            },
            "openai": {
                "name": "OpenAI",
                "careers_url": "https://openai.com/careers/search?q=",
                "levels_url": "https://www.levels.fyi/companies/openai/salaries"
            },
            "anthropic": {
                "name": "Anthropic",
                "careers_url": "https://www.anthropic.com/careers",
                "levels_url": "https://www.levels.fyi/companies/anthropic/salaries"
            },
            "bytedance": {
                "name": "ByteDance",
                "careers_url": "https://jobs.bytedance.com/en/position?keywords=machine%20learning",
                "levels_url": "https://www.levels.fyi/companies/bytedance/salaries"
            },
            "netflix": {
                "name": "Netflix",
                "careers_url": "https://jobs.netflix.com/search?q=machine%20learning",
                "levels_url": "https://www.levels.fyi/companies/netflix/salaries"
            },
            "apple": {
                "name": "Apple",
                "careers_url": "https://jobs.apple.com/en-us/search?search=machine%20learning",
                "levels_url": "https://www.levels.fyi/companies/apple/salaries"
            },
            "nvidia": {
                "name": "NVIDIA",
                "careers_url": "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite?q=machine%20learning",
                "levels_url": "https://www.levels.fyi/companies/nvidia/salaries"
            }
        }
    
    def _ensure_data_file(self):
        """Ensure the data directory and file exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if not self.jobs_file.exists():
            self._save_jobs({"jobs": [], "last_updated": "", "metadata": {}})
    
    def _save_jobs(self, data: Dict):
        """Save jobs to JSON file."""
        with open(self.jobs_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _load_jobs(self) -> Dict:
        """Load jobs from JSON file."""
        if self.jobs_file.exists():
            with open(self.jobs_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"jobs": [], "last_updated": "", "metadata": {}}
    
    def get_sample_jobs(self) -> List[Dict]:
        """
        Generate DEMO job listings for illustration purposes only.
        These are NOT real job postings - users should visit official career pages.
        """
        # NOTE: These are FICTIONAL examples to demonstrate the matching feature
        # Real job data should be obtained from official company career pages
        sample_jobs = [
            {
                "title": "[DEMO] ML Engineer Example",
                "company": "Demo Company",
                "location": "示例地点",
                "url": "#",
                "level": "Mid",
                "description": "这是一个演示职位，用于展示匹配功能。请访问公司官方招聘页面查看真实职位。",
                "requirements": ["Python", "TensorFlow/PyTorch", "ML/DL"],
                "salary_range": "请参考 levels.fyi",
                "remote": False,
                "posted_date": "DEMO",
                "is_demo": True
            }
        ]
        
        return sample_jobs
    
    def add_jobs(self, jobs: List[Dict]):
        """Add jobs to the database."""
        data = self._load_jobs()
        existing_ids = {j.get("id") for j in data["jobs"]}
        
        for job in jobs:
            if job.get("id") not in existing_ids:
                data["jobs"].append(job)
        
        data["last_updated"] = datetime.now().isoformat()
        self._save_jobs(data)
    
    def get_jobs(self, filters: Dict = None) -> List[Dict]:
        """Get jobs with optional filtering."""
        data = self._load_jobs()
        jobs = data.get("jobs", [])
        
        if not jobs:
            # Return sample jobs if empty
            jobs = self.get_sample_jobs()
            self.add_jobs(jobs)
        
        if not filters:
            return jobs
        
        # Apply filters
        filtered = jobs
        
        if filters.get("company"):
            filtered = [j for j in filtered if j.get("company") == filters["company"]]
        
        if filters.get("category"):
            filtered = [j for j in filtered if filters["category"] in j.get("categories", [])]
        
        if filters.get("level"):
            filtered = [j for j in filtered if filters["level"] in j.get("level", "")]
        
        if filters.get("remote"):
            filtered = [j for j in filtered if j.get("remote")]
        
        return filtered
    
    def match_resume(self, resume_text: str) -> List[Dict]:
        """Match a resume to all jobs and return sorted by match score."""
        jobs = self.get_jobs()
        
        for job in jobs:
            job["match_score"] = self.classifier.match_resume_to_job(resume_text, job)
        
        # Sort by match score descending
        return sorted(jobs, key=lambda x: x.get("match_score", 0), reverse=True)
    
    def get_company_info(self, company_id: str) -> Dict:
        """Get company career information."""
        return self.company_urls.get(company_id, {})
    
    def get_all_companies(self) -> Dict:
        """Get all company information."""
        return self.company_urls


# Initialize aggregator
job_aggregator = JobAggregator()


def get_matching_jobs(resume_text: str, top_k: int = 10) -> List[Dict]:
    """Get top matching jobs for a resume."""
    matched = job_aggregator.match_resume(resume_text)
    return matched[:top_k]


def get_jobs_by_category(category: str) -> List[Dict]:
    """Get jobs by category."""
    return job_aggregator.get_jobs({"category": category})


def get_jobs_by_company(company: str) -> List[Dict]:
    """Get jobs by company."""
    return job_aggregator.get_jobs({"company": company})
