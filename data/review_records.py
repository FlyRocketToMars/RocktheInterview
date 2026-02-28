import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
try:
    from data.supabase_client import learning_store, is_supabase_configured
    HAS_SUPABASE = True
except ImportError:
    HAS_SUPABASE = False

class ReviewRecords:
    """Manages user review history and spaced repetition data for questions."""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent
        self.records_file = self.data_dir / "review_records.json"
        self.use_supabase = HAS_SUPABASE and is_supabase_configured()
        if not self.use_supabase:
            self._ensure_file()
        
    def _ensure_file(self):
        if not self.records_file.exists():
            with open(self.records_file, "w", encoding="utf-8") as f:
                json.dump({"reviews": {}}, f, ensure_ascii=False)
                
    def _load_data(self) -> Dict:
        if not self.use_supabase:
            try:
                with open(self.records_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {"reviews": {}}
        return {"reviews": {}}
            
    def _save_data(self, data: Dict):
        if not self.use_supabase:
            with open(self.records_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
    def record_review(self, user_id: str, question_id: str, score: str, question_title: str) -> bool:
        """
        Record a review attempt.
        score can be: "easy", "medium", "hard"
        """
        if self.use_supabase:
            user_records = learning_store.get_review_records(user_id) or {}
            reviews = {user_id: user_records}
        else:
            data = self._load_data()
            reviews = data.get("reviews", {})
        
        if user_id not in reviews:
            reviews[user_id] = {}
            
        user_records = reviews[user_id]
        
        if question_id not in user_records:
            user_records[question_id] = {
                "question_title": question_title,
                "history": [],
                "mastery_score": 0,  # 0 to 100
                "next_review_date": None
            }
            
        record = user_records[question_id]
        now = datetime.now().isoformat()
        
        # Add to history
        record["history"].append({
            "timestamp": now,
            "score": score
        })
        
        # Simple mastery calculation
        if score == "easy":
            record["mastery_score"] = min(100, record["mastery_score"] + 30)
        elif score == "medium":
            record["mastery_score"] = min(100, record["mastery_score"] + 10)
        elif score == "hard":
            record["mastery_score"] = max(0, record["mastery_score"] - 20)
            
        # Ensure latest title
        record["question_title"] = question_title
        
        # Save back
        if self.use_supabase:
            learning_store.save_review_records(user_id, reviews[user_id])
        else:
            data["reviews"] = reviews
            self._save_data(data)
        return True
        
    def get_user_reviews(self, user_id: str) -> Dict:
        """Get all reviewed questions for a user."""
        if self.use_supabase:
            return learning_store.get_review_records(user_id) or {}
        data = self._load_data()
        return data.get("reviews", {}).get(user_id, {})

# Global instance
review_manager = ReviewRecords()

def record_question_review(user_id: str, question_id: str, score: str, title: str) -> bool:
    return review_manager.record_review(user_id, question_id, score, title)

def get_review_stats(user_id: str) -> Dict:
    reviews = review_manager.get_user_reviews(user_id)
    stats = {
        "total_reviewed": len(reviews),
        "mastered": sum(1 for r in reviews.values() if r["mastery_score"] >= 80),
        "needs_review": sum(1 for r in reviews.values() if r["mastery_score"] < 50),
        "details": reviews
    }
    return stats
