"""
Interview Experience Scraper
Scrapes interview questions and experiences from various sources
"""
import os
import json
import re
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

# Load environment variables
# scraper is in data/scraper/, so parent.parent.parent gets to project root
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


@dataclass
class InterviewQuestion:
    """Represents an interview question or experience."""
    id: str
    company: str
    role: str  # SDE, MLE, PM, DS
    level: str  # L3-L7, etc.
    round_type: str  # phone, onsite, behavioral, system_design
    question: str
    answer_hints: str = ""
    difficulty: str = "medium"  # easy, medium, hard
    source: str = ""
    source_url: str = ""
    date: str = ""
    upvotes: int = 0
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if not self.date:
            self.date = datetime.now().strftime("%Y-%m-%d")


class InterviewScraper:
    """Base class for interview scrapers."""
    
    def __init__(self):
        # scraper is in data/scraper/, so parent is data/, parent.parent is project root
        self.data_dir = Path(__file__).parent.parent  # This is data/
        self.questions_file = self.data_dir / "interview_questions.json"
        self._ensure_data_file()
    
    def _ensure_data_file(self):
        """Create questions file if it doesn't exist."""
        if not self.questions_file.exists():
            with open(self.questions_file, "w", encoding="utf-8") as f:
                json.dump({
                    "questions": [],
                    "last_updated": datetime.now().isoformat(),
                    "sources": []
                }, f, ensure_ascii=False, indent=2)
    
    def load_questions(self) -> Dict:
        """Load existing questions from file."""
        with open(self.questions_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def save_questions(self, data: Dict):
        """Save questions to file."""
        data["last_updated"] = datetime.now().isoformat()
        with open(self.questions_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add_questions(self, questions: List[InterviewQuestion]):
        """Add new questions to the database."""
        data = self.load_questions()
        existing_ids = {q["id"] for q in data["questions"]}
        
        new_count = 0
        for q in questions:
            if q.id not in existing_ids:
                data["questions"].append(asdict(q))
                new_count += 1
        
        self.save_questions(data)
        return new_count
    
    def get_questions_by_company(self, company: str) -> List[Dict]:
        """Get all questions for a specific company."""
        data = self.load_questions()
        return [q for q in data["questions"] if q["company"].lower() == company.lower()]
    
    def get_questions_by_role(self, role: str) -> List[Dict]:
        """Get all questions for a specific role."""
        data = self.load_questions()
        return [q for q in data["questions"] if q["role"].upper() == role.upper()]


class LeetCodeScraper(InterviewScraper):
    """
    Scrapes interview experiences from LeetCode Discuss.
    Uses the public GraphQL API.
    """
    
    GRAPHQL_URL = "https://leetcode.com/graphql"
    
    COMPANY_TAGS = {
        "google": "google",
        "meta": "facebook",
        "amazon": "amazon",
        "microsoft": "microsoft",
        "apple": "apple",
        "netflix": "netflix",
        "bytedance": "bytedance",
        "tiktok": "tiktok",
        "openai": "openai"
    }
    
    def __init__(self):
        super().__init__()
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json"
        })
    
    def search_discussions(self, company: str, limit: int = 20) -> List[Dict]:
        """
        Search LeetCode discussions for interview experiences.
        """
        company_tag = self.COMPANY_TAGS.get(company.lower(), company.lower())
        
        query = """
        query discussTopics($orderBy: TopicSortingOption, $query: String, $skip: Int, $first: Int, $tags: [String!]) {
            discussTopics(orderBy: $orderBy, query: $query, skip: $skip, first: $first, tags: $tags) {
                edges {
                    node {
                        id
                        title
                        viewCount
                        post {
                            content
                            creationDate
                            voteCount
                        }
                        tags {
                            name
                            slug
                        }
                    }
                }
            }
        }
        """
        
        variables = {
            "orderBy": "hot",
            "query": f"{company} interview",
            "skip": 0,
            "first": limit,
            "tags": ["interview-experience"]
        }
        
        try:
            response = self.session.post(
                self.GRAPHQL_URL,
                json={"query": query, "variables": variables},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("data", {}).get("discussTopics", {}).get("edges", [])
            else:
                print(f"LeetCode API returned {response.status_code}")
                return []
        except Exception as e:
            print(f"Error fetching from LeetCode: {e}")
            return []
    
    def parse_discussions(self, discussions: List[Dict], company: str) -> List[InterviewQuestion]:
        """Parse LeetCode discussions into InterviewQuestion objects."""
        questions = []
        
        for edge in discussions:
            node = edge.get("node", {})
            post = node.get("post", {})
            
            # Extract question from title and content
            title = node.get("title", "")
            content = post.get("content", "")
            
            # Determine role from tags
            tags = [t.get("slug", "") for t in node.get("tags", [])]
            role = self._detect_role(title + " " + content)
            round_type = self._detect_round_type(title + " " + content)
            
            question = InterviewQuestion(
                id=f"lc_{node.get('id', '')}",
                company=company,
                role=role,
                level="",
                round_type=round_type,
                question=title,
                answer_hints=content[:500] if content else "",
                source="LeetCode Discuss",
                source_url=f"https://leetcode.com/discuss/interview-experience/{node.get('id', '')}",
                date=post.get("creationDate", "")[:10] if post.get("creationDate") else "",
                upvotes=post.get("voteCount", 0),
                tags=tags
            )
            questions.append(question)
        
        return questions
    
    def _detect_role(self, text: str) -> str:
        """Detect role from text content."""
        text_lower = text.lower()
        if any(x in text_lower for x in ["machine learning", "ml engineer", "mle", "data scientist"]):
            return "MLE"
        elif any(x in text_lower for x in ["product manager", "pm", "apm"]):
            return "PM"
        elif any(x in text_lower for x in ["data science", "data analyst", "analytics"]):
            return "DS"
        else:
            return "SDE"
    
    def _detect_round_type(self, text: str) -> str:
        """Detect interview round type from text."""
        text_lower = text.lower()
        if any(x in text_lower for x in ["phone", "screen", "oa", "online assessment"]):
            return "phone_screen"
        elif any(x in text_lower for x in ["system design", "design round"]):
            return "system_design"
        elif any(x in text_lower for x in ["behavioral", "bq", "leadership"]):
            return "behavioral"
        elif any(x in text_lower for x in ["onsite", "virtual onsite", "loop"]):
            return "onsite"
        else:
            return "coding"
    
    def scrape_company(self, company: str, limit: int = 20) -> int:
        """
        Scrape interview experiences for a company.
        Returns number of new questions added.
        """
        print(f"Scraping LeetCode for {company} interviews...")
        discussions = self.search_discussions(company, limit)
        
        if not discussions:
            print(f"No discussions found for {company}")
            return 0
        
        questions = self.parse_discussions(discussions, company)
        new_count = self.add_questions(questions)
        print(f"Added {new_count} new questions for {company}")
        return new_count


class GeminiInterviewGenerator:
    """
    Uses Gemini AI to generate interview questions based on company patterns.
    This is useful when scraping is limited or blocked.
    """
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        self.scraper = InterviewScraper()
    
    def generate_questions(self, company: str, role: str, count: int = 5) -> List[InterviewQuestion]:
        """Generate interview questions using Gemini AI."""
        if not self.api_key:
            print("GEMINI_API_KEY not configured")
            return []
        
        prompt = f"""Generate {count} realistic interview questions for {role} position at {company}.

Format each question as JSON with these fields:
- question: The interview question
- round_type: One of [phone_screen, coding, system_design, behavioral, ml_deep_dive]
- difficulty: One of [easy, medium, hard]
- tags: List of relevant tags
- answer_hints: Brief hints for answering (2-3 sentences)

Return a JSON array of questions. Only return the JSON, no other text."""

        try:
            response = requests.post(
                f"{self.base_url}?key={self.api_key}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}]}]
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                
                # Extract JSON from response
                json_match = re.search(r'\[.*\]', text, re.DOTALL)
                if json_match:
                    questions_data = json.loads(json_match.group())
                    
                    questions = []
                    for i, q in enumerate(questions_data):
                        question = InterviewQuestion(
                            id=f"gemini_{company}_{role}_{datetime.now().strftime('%Y%m%d')}_{i}",
                            company=company,
                            role=role,
                            level="",
                            round_type=q.get("round_type", "coding"),
                            question=q.get("question", ""),
                            answer_hints=q.get("answer_hints", ""),
                            difficulty=q.get("difficulty", "medium"),
                            source="Gemini AI Generated",
                            tags=q.get("tags", [])
                        )
                        questions.append(question)
                    
                    return questions
            else:
                print(f"Gemini API error: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error generating questions: {e}")
            return []
    
    def generate_and_save(self, company: str, role: str, count: int = 5) -> int:
        """Generate questions and save to database."""
        questions = self.generate_questions(company, role, count)
        if questions:
            new_count = self.scraper.add_questions(questions)
            print(f"Generated and saved {new_count} questions for {company} {role}")
            return new_count
        return 0


def scrape_all_companies(companies: List[str] = None, limit_per_company: int = 10):
    """
    Scrape interview experiences for multiple companies.
    """
    if companies is None:
        companies = ["google", "meta", "amazon", "microsoft", "apple"]
    
    scraper = LeetCodeScraper()
    total_new = 0
    
    for company in companies:
        try:
            new_count = scraper.scrape_company(company, limit_per_company)
            total_new += new_count
        except Exception as e:
            print(f"Error scraping {company}: {e}")
    
    print(f"\nTotal new questions added: {total_new}")
    return total_new


def generate_with_ai(companies: List[str] = None, roles: List[str] = None, count_per: int = 5):
    """
    Generate interview questions using AI for multiple companies and roles.
    """
    import time
    
    if companies is None:
        companies = ["Google", "Meta", "Amazon", "Microsoft"]
    if roles is None:
        roles = ["SDE", "MLE"]
    
    generator = GeminiInterviewGenerator()
    total_new = 0
    
    for company in companies:
        for role in roles:
            try:
                new_count = generator.generate_and_save(company, role, count_per)
                total_new += new_count
                # Rate limiting - wait 5 seconds between requests
                time.sleep(5)
            except Exception as e:
                print(f"Error generating for {company} {role}: {e}")
    
    print(f"\nTotal questions generated: {total_new}")
    return total_new


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Scrape interview questions")
    parser.add_argument("--mode", choices=["scrape", "generate", "both"], default="both",
                        help="Mode: scrape from web, generate with AI, or both")
    parser.add_argument("--companies", nargs="+", default=None,
                        help="Companies to scrape/generate for")
    parser.add_argument("--roles", nargs="+", default=["SDE", "MLE"],
                        help="Roles to generate for (AI mode only)")
    parser.add_argument("--limit", type=int, default=10,
                        help="Limit per company")
    
    args = parser.parse_args()
    
    if args.mode in ["scrape", "both"]:
        print("=== Scraping from web sources ===")
        scrape_all_companies(args.companies, args.limit)
    
    if args.mode in ["generate", "both"]:
        print("\n=== Generating with AI ===")
        generate_with_ai(args.companies, args.roles, args.limit)
