"""
User Gamification System
Points, badges, levels, and achievements for user engagement
Supports Supabase for persistent storage with JSON fallback
"""
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Try to import Supabase client
try:
    from data.supabase_client import user_store, is_supabase_configured
    HAS_SUPABASE = True
except ImportError:
    HAS_SUPABASE = False


class UserGamification:
    """User points, badges, and achievements system."""
    
    # Point values for different actions
    POINTS = {
        "ask_question": 5,
        "answer_question": 10,
        "answer_accepted": 25,
        "receive_upvote": 2,
        "give_upvote": 1,
        "daily_login": 5,
        "streak_bonus": 10,  # Per day of streak
        "first_answer": 20,
        "first_question": 15,
        "complete_profile": 10,
    }
    
    # Level thresholds
    LEVELS = [
        (0, "🌱 新手村民", "刚刚开始面试之旅"),
        (50, "📚 学习者", "积极学习中"),
        (150, "💪 实践者", "开始贡献内容"),
        (300, "🎯 挑战者", "准备充分"),
        (500, "⭐ 高手", "面试达人"),
        (800, "🏆 专家", "社区贡献者"),
        (1200, "👑 大师", "面试导师"),
        (2000, "🔥 传奇", "社区领袖"),
    ]
    
    # Badges with conditions
    BADGES = {
        # Contribution badges
        "first_answer": {
            "name": "🎤 首次发言",
            "description": "提交第一个回答",
            "icon": "🎤",
            "condition": lambda u: u.get("total_answers", 0) >= 1
        },
        "helpful_10": {
            "name": "🤝 乐于助人",
            "description": "回答被采纳10次",
            "icon": "🤝",
            "condition": lambda u: u.get("answers_accepted", 0) >= 10
        },
        "prolific_writer": {
            "name": "✍️ 笔耕不辍",
            "description": "提交50个回答",
            "icon": "✍️",
            "condition": lambda u: u.get("total_answers", 0) >= 50
        },
        
        # Streak badges
        "streak_7": {
            "name": "🔥 坚持一周",
            "description": "连续登录7天",
            "icon": "🔥",
            "condition": lambda u: u.get("max_streak", 0) >= 7
        },
        "streak_30": {
            "name": "💎 坚持一月",
            "description": "连续登录30天",
            "icon": "💎",
            "condition": lambda u: u.get("max_streak", 0) >= 30
        },
        
        # Voting badges
        "upvotes_100": {
            "name": "👍 百人认可",
            "description": "收到100个赞",
            "icon": "👍",
            "condition": lambda u: u.get("total_upvotes_received", 0) >= 100
        },
        
        # Question badges
        "curious_mind": {
            "name": "🤔 好奇宝宝",
            "description": "提问10个问题",
            "icon": "🤔",
            "condition": lambda u: u.get("total_questions", 0) >= 10
        },
        
        # Topic badges
        "ml_expert": {
            "name": "🧠 ML专家",
            "description": "ML理论回答被采纳5次",
            "icon": "🧠",
            "condition": lambda u: u.get("ml_answers_accepted", 0) >= 5
        },
        "system_design_master": {
            "name": "🏗️ 架构大师",
            "description": "系统设计回答被采纳5次",
            "icon": "🏗️",
            "condition": lambda u: u.get("sd_answers_accepted", 0) >= 5
        },
        
        # Special badges
        "early_adopter": {
            "name": "🌟 早期用户",
            "description": "早期加入的用户",
            "icon": "🌟",
            "condition": lambda u: True  # Manually awarded
        },
        "top_contributor": {
            "name": "🏆 顶级贡献者",
            "description": "本月贡献榜第一",
            "icon": "🏆",
            "condition": lambda u: u.get("monthly_rank", 999) == 1
        },
    }
    
    def __init__(self):
        self.data_file = Path(__file__).parent / "users_gamification.json"
        self.template_file = Path(__file__).parent / "users_gamification.json.template"
        
        # Check if Supabase is available
        self.use_supabase = HAS_SUPABASE and is_supabase_configured()
        
        if not self.use_supabase:
            self._ensure_data_file()
    
    def _ensure_data_file(self):
        """Initialize data file from template if it doesn't exist."""
        if not self.data_file.exists():
            if self.template_file.exists():
                import shutil
                shutil.copy(self.template_file, self.data_file)
            else:
                self._save_data({"users": {}, "leaderboard": []})
    
    def _load_data(self) -> Dict:
        """Load data from Supabase or JSON file."""
        if self.use_supabase:
            users = user_store.get_all_users()
            return {"users": {u["user_id"]: u for u in users}, "leaderboard": []}
        
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"users": {}, "leaderboard": []}
    
    def _save_data(self, data: Dict):
        """Save data to JSON file (Supabase saves directly in methods)."""
        if not self.use_supabase:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _save_user_to_supabase(self, user: Dict):
        """Save or update user in Supabase."""
        if self.use_supabase:
            existing = user_store.get_user(user["user_id"])
            if existing:
                user_store.update_user(user["user_id"], user)
            else:
                user_store.create_user(user)
    
    def _get_user_id(self, username: str) -> str:
        """Generate consistent user ID from username."""
        return hashlib.md5(username.lower().encode()).hexdigest()[:12]
    
    def get_or_create_user(self, username: str) -> Dict:
        """Get or create a user profile."""
        user_id = self._get_user_id(username)
        
        # Try Supabase first
        if self.use_supabase:
            existing = user_store.get_user(user_id)
            if existing:
                return existing
        
        # Fallback to JSON or create new
        data = self._load_data()
        
        if user_id not in data["users"]:
            new_user = {
                "username": username,
                "user_id": user_id,
                "points": 0,
                "level": 0,
                "badges": [],
                "total_answers": 0,
                "total_questions": 0,
                "answers_accepted": 0,
                "total_upvotes_received": 0,
                "total_upvotes_given": 0,
                "current_streak": 0,
                "max_streak": 0,
                "last_login": None,
                "joined_at": datetime.now().isoformat(),
                "ml_answers_accepted": 0,
                "sd_answers_accepted": 0,
            }
            data["users"][user_id] = new_user
            self._save_data(data)
            self._save_user_to_supabase(new_user)
        
        return data["users"][user_id]
    
    def add_points(self, username: str, action: str, multiplier: int = 1) -> int:
        """Add points for an action."""
        data = self._load_data()
        user_id = self._get_user_id(username)
        
        if user_id not in data["users"]:
            self.get_or_create_user(username)
            data = self._load_data()
        
        points = self.POINTS.get(action, 0) * multiplier
        data["users"][user_id]["points"] += points
        
        # Update level
        data["users"][user_id]["level"] = self._calculate_level(data["users"][user_id]["points"])
        
        self._save_data(data)
        return points
    
    def _calculate_level(self, points: int) -> int:
        """Calculate user level based on points."""
        level = 0
        for threshold, _, _ in self.LEVELS:
            if points >= threshold:
                level += 1
        return min(level, len(self.LEVELS))
    
    def get_level_info(self, points: int) -> tuple:
        """Get level name and description."""
        level_idx = self._calculate_level(points) - 1
        if level_idx < 0:
            level_idx = 0
        return self.LEVELS[level_idx]
    
    def record_login(self, username: str) -> Dict:
        """Record user login and update streak."""
        data = self._load_data()
        user_id = self._get_user_id(username)
        
        if user_id not in data["users"]:
            self.get_or_create_user(username)
            data = self._load_data()
        
        user = data["users"][user_id]
        today = datetime.now().date().isoformat()
        last_login = user.get("last_login")
        
        if last_login != today:
            # Check streak
            if last_login:
                last_date = datetime.fromisoformat(last_login).date()
                if (datetime.now().date() - last_date).days == 1:
                    user["current_streak"] += 1
                    if user["current_streak"] > user["max_streak"]:
                        user["max_streak"] = user["current_streak"]
                elif (datetime.now().date() - last_date).days > 1:
                    user["current_streak"] = 1
            else:
                user["current_streak"] = 1
            
            user["last_login"] = today
            
            # Daily login bonus
            points = self.POINTS["daily_login"]
            if user["current_streak"] > 1:
                points += self.POINTS["streak_bonus"] * min(user["current_streak"], 7)
            user["points"] += points
            
            self._save_data(data)
            return {"streak": user["current_streak"], "points": points}
        
        return {"streak": user["current_streak"], "points": 0}
    
    def increment_stat(self, username: str, stat: str, amount: int = 1):
        """Increment a user statistic."""
        data = self._load_data()
        user_id = self._get_user_id(username)
        
        if user_id in data["users"]:
            data["users"][user_id][stat] = data["users"][user_id].get(stat, 0) + amount
            self._save_data(data)
    
    def check_and_award_badges(self, username: str) -> List[str]:
        """Check and award any new badges the user has earned."""
        data = self._load_data()
        user_id = self._get_user_id(username)
        
        if user_id not in data["users"]:
            return []
        
        user = data["users"][user_id]
        new_badges = []
        
        for badge_id, badge_info in self.BADGES.items():
            if badge_id not in user.get("badges", []):
                if badge_info["condition"](user):
                    user["badges"].append(badge_id)
                    new_badges.append(badge_info["name"])
        
        if new_badges:
            self._save_data(data)
        
        return new_badges
    
    def get_user_profile(self, username: str) -> Dict:
        """Get full user profile with computed fields."""
        user = self.get_or_create_user(username)
        level_info = self.get_level_info(user["points"])
        
        # Calculate progress to next level
        current_level = self._calculate_level(user["points"])
        if current_level < len(self.LEVELS):
            next_threshold = self.LEVELS[current_level][0]
            prev_threshold = self.LEVELS[current_level - 1][0] if current_level > 0 else 0
            progress = (user["points"] - prev_threshold) / (next_threshold - prev_threshold) if next_threshold > prev_threshold else 1
        else:
            progress = 1.0
        
        return {
            **user,
            "level_name": level_info[1],
            "level_description": level_info[2],
            "progress_to_next_level": progress,
            "badge_details": [self.BADGES[b] for b in user.get("badges", []) if b in self.BADGES]
        }
    
    def get_leaderboard(self, limit: int = 20) -> List[Dict]:
        """Get top users by points."""
        data = self._load_data()
        users = list(data.get("users", {}).values())
        users = sorted(users, key=lambda x: x.get("points", 0), reverse=True)
        
        # Add rank
        for i, user in enumerate(users[:limit]):
            user["rank"] = i + 1
        
        return users[:limit]
    
    def get_user_rank(self, username: str) -> int:
        """Get user's rank on leaderboard."""
        leaderboard = self.get_leaderboard(limit=1000)
        user_id = self._get_user_id(username)
        
        for i, user in enumerate(leaderboard):
            if user.get("user_id") == user_id:
                return i + 1
        return len(leaderboard) + 1


# Global instance
gamification = UserGamification()


# Helper functions
def award_points(username: str, action: str, multiplier: int = 1) -> int:
    """Award points for an action."""
    return gamification.add_points(username, action, multiplier)


def get_profile(username: str) -> Dict:
    """Get user profile."""
    return gamification.get_user_profile(username)


def record_daily_login(username: str) -> Dict:
    """Record daily login."""
    return gamification.record_login(username)


def get_leaderboard(limit: int = 20) -> List[Dict]:
    """Get leaderboard."""
    return gamification.get_leaderboard(limit)


def check_badges(username: str) -> List[str]:
    """Check for new badges."""
    return gamification.check_and_award_badges(username)
