"""
User Progress Manager - Persistent storage for user progress
Tracks completed tasks, study hours, streaks, and performance metrics
"""
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import hashlib


class UserProgressManager:
    """Manages user progress data with persistent storage."""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.progress_file = self.data_dir / "user_progress.json"
        self._ensure_file()
    
    def _ensure_file(self):
        """Ensure progress file exists."""
        if not self.progress_file.exists():
            self._save_data({})
    
    def _load_data(self) -> Dict:
        """Load all user progress data."""
        try:
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_data(self, data: Dict):
        """Save all user progress data."""
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _get_user_id(self, email: str) -> str:
        """Generate consistent user ID from email."""
        return hashlib.md5(email.encode()).hexdigest()[:16]
    
    def get_user_progress(self, email: str) -> Dict:
        """Get progress for a specific user."""
        data = self._load_data()
        user_id = self._get_user_id(email)
        
        if user_id not in data:
            # Initialize new user
            data[user_id] = self._create_default_progress(email)
            self._save_data(data)
        
        return data[user_id]
    
    def _create_default_progress(self, email: str) -> Dict:
        """Create default progress structure for new user."""
        return {
            "email": email,
            "created_at": datetime.now().isoformat(),
            "profile": {
                "target_company": "Google",
                "target_role": "MLE",
                "interview_date": None,
                "daily_hours": 3,
                "weak_areas": []
            },
            "stats": {
                "total_completed": 0,
                "total_hours": 0,
                "streak_days": 0,
                "last_activity": None,
                "coding_completed": 0,
                "system_design_completed": 0,
                "ml_theory_completed": 0,
                "behavioral_completed": 0
            },
            "daily_history": [],
            "completed_questions": [],
            "performance_by_topic": {}
        }
    
    def update_profile(self, email: str, profile_data: Dict):
        """Update user profile settings."""
        data = self._load_data()
        user_id = self._get_user_id(email)
        
        if user_id in data:
            data[user_id]["profile"].update(profile_data)
            self._save_data(data)
    
    def mark_task_complete(self, email: str, task_id: str, task_type: str, duration_min: int = 30):
        """Mark a task as completed and update stats."""
        data = self._load_data()
        user_id = self._get_user_id(email)
        
        if user_id not in data:
            data[user_id] = self._create_default_progress(email)
        
        user_data = data[user_id]
        today = datetime.now().date().isoformat()
        
        # Update stats
        user_data["stats"]["total_completed"] += 1
        user_data["stats"]["total_hours"] += duration_min / 60
        user_data["stats"]["last_activity"] = datetime.now().isoformat()
        
        # Update category-specific stats
        if task_type == "coding":
            user_data["stats"]["coding_completed"] += 1
        elif task_type == "system_design":
            user_data["stats"]["system_design_completed"] += 1
        elif task_type == "theory":
            user_data["stats"]["ml_theory_completed"] += 1
        elif task_type == "behavioral":
            user_data["stats"]["behavioral_completed"] += 1
        
        # Update daily history
        daily_entry = next((d for d in user_data["daily_history"] if d["date"] == today), None)
        if daily_entry:
            daily_entry["tasks_completed"] += 1
            daily_entry["minutes_studied"] += duration_min
        else:
            user_data["daily_history"].append({
                "date": today,
                "tasks_completed": 1,
                "minutes_studied": duration_min
            })
        
        # Update streak
        user_data["stats"]["streak_days"] = self._calculate_streak(user_data["daily_history"])
        
        # Add to completed questions
        user_data["completed_questions"].append({
            "task_id": task_id,
            "type": task_type,
            "completed_at": datetime.now().isoformat()
        })
        
        self._save_data(data)
    
    def _calculate_streak(self, daily_history: List[Dict]) -> int:
        """Calculate current streak days."""
        if not daily_history:
            return 0
        
        # Sort by date descending
        sorted_history = sorted(daily_history, key=lambda x: x["date"], reverse=True)
        
        streak = 0
        current_date = datetime.now().date()
        
        for entry in sorted_history:
            entry_date = datetime.fromisoformat(entry["date"]).date()
            
            if entry_date == current_date - timedelta(days=streak):
                streak += 1
            else:
                break
        
        return streak
    
    def get_progress_stats(self, email: str) -> Dict:
        """Get comprehensive progress statistics."""
        user_data = self.get_user_progress(email)
        stats = user_data["stats"]
        profile = user_data["profile"]
        
        # Calculate percentages
        total_target = 200  # Target total questions
        coding_target = 75
        sd_target = 30
        theory_target = 50
        
        # Calculate days to interview
        days_to_interview = None
        if profile.get("interview_date"):
            try:
                interview_date = datetime.fromisoformat(profile["interview_date"])
                days_to_interview = (interview_date.date() - datetime.now().date()).days
            except:
                pass
        
        # Get daily activity for last 30 days
        daily_questions = self._get_daily_activity(user_data["daily_history"], 30)
        
        return {
            "total_completed": stats["total_completed"],
            "this_week": self._get_week_count(user_data["daily_history"]),
            "total_hours": int(stats["total_hours"]),
            "hours_this_week": self._get_week_hours(user_data["daily_history"]),
            "streak_days": stats["streak_days"],
            "days_to_interview": days_to_interview,
            "readiness": min(100, int((stats["total_completed"] / total_target) * 100)),
            "overall_progress": min(100, int((stats["total_completed"] / total_target) * 100)),
            "coding_progress": min(100, int((stats["coding_completed"] / coding_target) * 100)),
            "system_design_progress": min(100, int((stats["system_design_completed"] / sd_target) * 100)),
            "ml_theory_progress": min(100, int((stats["ml_theory_completed"] / theory_target) * 100)),
            "behavioral_progress": min(100, int((stats.get("behavioral_completed", 0) / 20) * 100)),
            "llm_progress": 70,  # TODO: Track separately
            "total_prep_days": 90,  # TODO: Calculate from start date
            "daily_questions": daily_questions
        }
    
    def _get_week_count(self, daily_history: List[Dict]) -> int:
        """Get tasks completed in last 7 days."""
        week_ago = (datetime.now() - timedelta(days=7)).date().isoformat()
        return sum(d["tasks_completed"] for d in daily_history if d["date"] >= week_ago)
    
    def _get_week_hours(self, daily_history: List[Dict]) -> int:
        """Get hours studied in last 7 days."""
        week_ago = (datetime.now() - timedelta(days=7)).date().isoformat()
        minutes = sum(d["minutes_studied"] for d in daily_history if d["date"] >= week_ago)
        return int(minutes / 60)
    
    def _get_daily_activity(self, daily_history: List[Dict], days: int = 30) -> List[int]:
        """Get daily question count for last N days."""
        result = []
        for i in range(days - 1, -1, -1):
            date = (datetime.now() - timedelta(days=i)).date().isoformat()
            entry = next((d for d in daily_history if d["date"] == date), None)
            result.append(entry["tasks_completed"] if entry else 0)
        return result


# Global instance
progress_manager = UserProgressManager()
