"""
User Experience & Story Bank Data Module
Stores user's personal experiences, project stories, behavioral answers, etc.
Supports Supabase with local JSON fallback.
"""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    from data.supabase_client import get_supabase_client, is_supabase_configured
    HAS_SUPABASE = True
except ImportError:
    HAS_SUPABASE = False

LOCAL_FILE = Path(__file__).parent / "user_stories.json"

# STAR Method categories and behavioral themes
STORY_CATEGORIES = {
    "project": "🏗️ 项目经历 (Project)",
    "leadership": "👑 领导力 (Leadership)",
    "conflict": "⚡ 冲突解决 (Conflict Resolution)",
    "failure": "💥 失败/挫折 (Failure & Learning)",
    "achievement": "🏆 成就/亮点 (Achievement)",
    "teamwork": "🤝 团队合作 (Teamwork)",
    "innovation": "💡 创新/改进 (Innovation)",
    "deadline": "⏰ 时间压力 (Deadline/Pressure)",
    "ambiguity": "🌫️ 模糊/不确定 (Ambiguity)",
    "customer": "🎯 客户导向 (Customer Focus)",
    "technical_depth": "🔬 技术深度 (Technical Depth)",
    "other": "📁 其他 (Other)",
}

COMMON_BQ_QUESTIONS = [
    "Tell me about a time you had to deal with a difficult teammate",
    "Describe a project you're most proud of",
    "Tell me about a time you failed and what you learned",
    "How do you handle ambiguity?",
    "Tell me about a time you had to make a decision with incomplete data",
    "Describe a time you went above and beyond",
    "Tell me about a time you disagreed with your manager",
    "How do you prioritize when you have multiple tasks?",
    "Tell me about a time you had to learn something quickly",
    "Describe a situation where you had to influence without authority",
    "Tell me about a technical challenge you solved",
    "How do you handle tight deadlines?",
    "Describe a time you improved a process or system",
    "Tell me about your experience working with cross-functional teams",
    "What's the most impactful project you've worked on and why?",
]


class UserStoryBank:
    """Manage user's personal experience stories for interview prep."""
    
    def __init__(self):
        self.use_supabase = HAS_SUPABASE and is_supabase_configured()
        if self.use_supabase:
            self.client = get_supabase_client()
        self._ensure_local_file()
    
    def _ensure_local_file(self):
        if not LOCAL_FILE.exists():
            LOCAL_FILE.write_text('{}', encoding='utf-8')
    
    def _load_local(self) -> Dict:
        try:
            return json.loads(LOCAL_FILE.read_text(encoding='utf-8'))
        except:
            return {}
    
    def _save_local(self, data: Dict):
        LOCAL_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    
    def add_story(self, user_id: str, story: Dict) -> str:
        """Add a new story/experience."""
        story_id = str(uuid.uuid4())[:12]
        entry = {
            "id": story_id,
            "user_id": user_id,
            "title": story.get("title", ""),
            "category": story.get("category", "other"),
            "company": story.get("company", ""),
            "role": story.get("role", ""),
            "situation": story.get("situation", ""),
            "task": story.get("task", ""),
            "action": story.get("action", ""),
            "result": story.get("result", ""),
            "metrics": story.get("metrics", ""),  # quantifiable results
            "tags": story.get("tags", []),
            "applicable_questions": story.get("applicable_questions", []),
            "notes": story.get("notes", ""),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        
        if self.use_supabase:
            try:
                self.client.table("user_stories").insert(entry).execute()
                return story_id
            except Exception as e:
                print(f"Supabase insert story failed: {e}")
        
        # Local fallback
        data = self._load_local()
        user_stories = data.get(user_id, [])
        user_stories.append(entry)
        data[user_id] = user_stories
        self._save_local(data)
        return story_id
    
    def get_all_stories(self, user_id: str) -> List[Dict]:
        """Get all stories for a user."""
        if self.use_supabase:
            try:
                result = self.client.table("user_stories").select("*").eq(
                    "user_id", user_id
                ).order("updated_at", desc=True).execute()
                return result.data or []
            except Exception as e:
                print(f"Supabase get stories failed: {e}")
        
        data = self._load_local()
        return data.get(user_id, [])
    
    def get_stories_by_category(self, user_id: str, category: str) -> List[Dict]:
        """Get stories filtered by category."""
        all_stories = self.get_all_stories(user_id)
        if category == "all":
            return all_stories
        return [s for s in all_stories if s.get("category") == category]
    
    def update_story(self, user_id: str, story_id: str, updates: Dict):
        """Update an existing story."""
        updates["updated_at"] = datetime.now().isoformat()
        
        if self.use_supabase:
            try:
                self.client.table("user_stories").update(updates).eq(
                    "id", story_id
                ).eq("user_id", user_id).execute()
                return
            except Exception as e:
                print(f"Supabase update story failed: {e}")
        
        data = self._load_local()
        user_stories = data.get(user_id, [])
        for story in user_stories:
            if story.get("id") == story_id:
                story.update(updates)
                break
        data[user_id] = user_stories
        self._save_local(data)
    
    def delete_story(self, user_id: str, story_id: str):
        """Delete a story."""
        if self.use_supabase:
            try:
                self.client.table("user_stories").delete().eq(
                    "id", story_id
                ).eq("user_id", user_id).execute()
                return
            except Exception as e:
                print(f"Supabase delete story failed: {e}")
        
        data = self._load_local()
        user_stories = data.get(user_id, [])
        data[user_id] = [s for s in user_stories if s.get("id") != story_id]
        self._save_local(data)
    
    def get_stats(self, user_id: str) -> Dict:
        """Get stats about user's story bank."""
        stories = self.get_all_stories(user_id)
        cats = {}
        for s in stories:
            c = s.get("category", "other")
            cats[c] = cats.get(c, 0) + 1
        return {
            "total": len(stories),
            "categories": cats,
            "companies": list(set(s.get("company", "") for s in stories if s.get("company"))),
        }


# Global instance
user_story_bank = UserStoryBank()
