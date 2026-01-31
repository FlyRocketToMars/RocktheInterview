"""
Question bank aggregator - combines multiple question sources
"""
import json
from pathlib import Path
from typing import List, Dict
import random


class QuestionBank:
    """Manages and serves interview questions from multiple sources."""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent
        self.questions = []
        self.load_all_questions()
    
    def load_all_questions(self):
        """Load questions from all JSON files."""
        self.questions = []
        
        # Load main questions file
        main_file = self.data_dir / "interview_questions.json"
        if main_file.exists():
            with open(main_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.questions.extend(data.get("questions", []))
        
        # Load expanded questions
        expanded_file = self.data_dir / "questions_expanded.json"
        if expanded_file.exists():
            with open(expanded_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.questions.extend(data.get("questions", []))
        
        # Load LLM-focused questions
        llm_file = self.data_dir / "questions_llm.json"
        if llm_file.exists():
            with open(llm_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.questions.extend(data.get("questions", []))
        
        # Deduplicate by ID
        seen_ids = set()
        unique_questions = []
        for q in self.questions:
            if q.get("id") not in seen_ids:
                seen_ids.add(q.get("id"))
                unique_questions.append(q)
        
        self.questions = unique_questions
        print(f"Loaded {len(self.questions)} questions")
    
    def get_all(self) -> List[Dict]:
        """Get all questions."""
        return self.questions
    
    def get_by_company(self, company: str) -> List[Dict]:
        """Get questions by company."""
        return [q for q in self.questions if q.get("company", "").lower() == company.lower()]
    
    def get_by_round(self, round_type: str) -> List[Dict]:
        """Get questions by round type."""
        return [q for q in self.questions if q.get("round") == round_type]
    
    def get_by_domain(self, domain: str) -> List[Dict]:
        """Get questions by domain."""
        return [q for q in self.questions if q.get("domain") == domain]
    
    def get_by_difficulty(self, difficulty: str) -> List[Dict]:
        """Get questions by difficulty."""
        return [q for q in self.questions if q.get("difficulty") == difficulty]
    
    def get_random(self, n: int = 1, filters: Dict = None) -> List[Dict]:
        """Get random questions with optional filters."""
        questions = self.questions
        
        if filters:
            if filters.get("company"):
                questions = [q for q in questions if q.get("company", "").lower() == filters["company"].lower()]
            if filters.get("round"):
                questions = [q for q in questions if q.get("round") == filters["round"]]
            if filters.get("domain"):
                questions = [q for q in questions if q.get("domain") == filters["domain"]]
            if filters.get("difficulty"):
                questions = [q for q in questions if q.get("difficulty") == filters["difficulty"]]
        
        return random.sample(questions, min(n, len(questions)))
    
    def get_daily_practice(self, user_level: str = "L5/E5") -> List[Dict]:
        """Get a balanced daily practice set."""
        practice = []
        
        # One from each category
        rounds = ["ml_theory", "ml_system_design", "behavioral", "ml_coding"]
        
        for round_type in rounds:
            available = self.get_by_round(round_type)
            if available:
                practice.extend(random.sample(available, min(1, len(available))))
        
        return practice
    
    def get_stats(self) -> Dict:
        """Get question bank statistics."""
        companies = {}
        rounds = {}
        domains = {}
        difficulties = {}
        
        for q in self.questions:
            # Count by company
            company = q.get("company", "Unknown")
            companies[company] = companies.get(company, 0) + 1
            
            # Count by round
            round_type = q.get("round", "Unknown")
            rounds[round_type] = rounds.get(round_type, 0) + 1
            
            # Count by domain
            domain = q.get("domain", "Unknown")
            domains[domain] = domains.get(domain, 0) + 1
            
            # Count by difficulty
            difficulty = q.get("difficulty", "Unknown")
            difficulties[difficulty] = difficulties.get(difficulty, 0) + 1
        
        return {
            "total": len(self.questions),
            "by_company": dict(sorted(companies.items(), key=lambda x: -x[1])),
            "by_round": rounds,
            "by_domain": domains,
            "by_difficulty": difficulties
        }


# Global instance
question_bank = QuestionBank()


# Helper functions
def get_questions(filters: Dict = None) -> List[Dict]:
    """Get questions with optional filters."""
    if not filters:
        return question_bank.get_all()
    
    questions = question_bank.get_all()
    if filters.get("company"):
        questions = [q for q in questions if q.get("company", "").lower() == filters["company"].lower()]
    if filters.get("round"):
        questions = [q for q in questions if q.get("round") == filters["round"]]
    if filters.get("domain"):
        questions = [q for q in questions if q.get("domain") == filters["domain"]]
    if filters.get("difficulty"):
        questions = [q for q in questions if q.get("difficulty") == filters["difficulty"]]
    
    return questions


def get_random_question(filters: Dict = None) -> Dict:
    """Get a random question."""
    questions = question_bank.get_random(1, filters)
    return questions[0] if questions else None


def get_daily_questions() -> List[Dict]:
    """Get daily practice questions."""
    return question_bank.get_daily_practice()


def get_question_stats() -> Dict:
    """Get question bank statistics."""
    return question_bank.get_stats()
