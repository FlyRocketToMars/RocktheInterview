"""
AI Coach Engine - Intelligent Interview Prep Assistant
Analyzes user progress and generates personalized daily plans
"""
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import random

class AICoach:
    """
    AI Coach that acts as your personal interview prep mentor.
    Analyzes your strengths/weaknesses and creates focused daily plans.
    """
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        
    def generate_daily_briefing(self, user_id: str, user_profile: Dict) -> Dict:
        """
        Generate AI-powered daily briefing.
        
        Returns:
            {
                "greeting": str,
                "days_left": int,
                "focus_today": str,
                "ai_insight": str,
                "new_content_alert": str,
                "motivation": str
            }
        """
        # Calculate days to interview
        interview_date_str = user_profile.get("interview_date")
        if interview_date_str:
            interview_date = datetime.fromisoformat(interview_date_str)
            days_left = (interview_date - datetime.now()).days
        else:
            days_left = None
        
        # Analyze progress to determine focus
        progress = self._analyze_progress(user_id, user_profile)
        focus_area = self._determine_focus_area(progress)
        
        # Generate insight
        insight = self._generate_insight(progress, user_profile)
        
        # Check for new content
        new_content = self._check_new_content()
        
        # Motivational message
        motivation = self._get_motivation(progress)
        
        # Time-based greeting
        hour = datetime.now().hour
        if hour < 12:
            greeting = "Good morning, Interview Warrior! 👋"
        elif hour < 18:
            greeting = "Good afternoon! Let's crush it! 💪"
        else:
            greeting = "Good evening! Time to level up! 🌙"
        
        return {
            "greeting": greeting,
            "days_left": days_left,
            "target_company": user_profile.get("target_company", "your dream company"),
            "target_role": user_profile.get("target_role", "MLE"),
            "focus_today": focus_area,
            "ai_insight": insight,
            "new_content_alert": new_content,
            "motivation": motivation
        }
    
    def generate_daily_missions(self, user_id: str, user_profile: Dict) -> List[Dict]:
        """
        Generate 3 focused missions for today.
        
        Strategy:
        1. One from weakest area (theory/coding/system design)
        2. One from target company's focus
        3. One trending/new topic
        """
        import time
        from data.learning_planner import learning_planner
        
        # 1. First check if user has an active, formal study plan
        plan_data = learning_planner.get_user_plan(user_id)
        if plan_data and plan_data.get("status") == "active":
            # Sync missions from the study plan to keep both tabs consistent!
            today_tasks = learning_planner.get_today_tasks(user_id)
            missions = []
            
            for idx, task in enumerate(today_tasks.get("tasks", [])):
                focus = task.get("topic", "")
                
                # Convert plan task into mission format
                mission = {
                    "id": f"plan_{task['type']}_{idx}",
                    "type": "coding" if task['type'] == "coding" else "reading" if task['type'] == "theory" else "trending",
                    "title": f"[{task['name']}] {focus}",
                    "description": task.get("suggested_activity", ""),
                    "duration": f"{task.get('duration_minutes', 0)} min",
                    "priority": "high",
                    "icon": task.get("icon", "📝"),
                    "completed": False
                }
                
                # Expand details based on type
                if task['type'] == "coding":
                    mission["content"] = {"question": f"Focus on {focus}", "focus": "Time Complexity and Edge Cases"}
                elif task['type'] == "theory":
                    mission["content"] = {"topic": f"Read about {focus}"}
                elif task['type'] in ["system_design", "mock_interview"]:
                    mission["content"] = {"title": focus, "description": task.get("suggested_activity", "Practice and record yourself.")}
                
                missions.append(mission)
            
            return missions
        
        # 2. Add unstructured daily generated missions as fallback
        missions = []
        
        # Analyze what user needs most
        progress = self._analyze_progress(user_id, user_profile)
        weak_areas = user_profile.get("weak_areas", [])
        target_company = user_profile.get("target_company", "Google")
        
        # Mission 1: Address weakest area
        weakest = self._get_weakest_area(progress)
        if weakest == "ml_theory":
            missions.append(self._generate_theory_mission(weak_areas))
        elif weakest == "system_design":
            missions.append(self._generate_system_design_mission(target_company))
        else:
            missions.append(self._generate_coding_mission())
        
        time.sleep(0.001)  # Ensure unique timestamps
        
        # Mission 2: Company-specific
        missions.append(self._generate_company_mission(target_company))
        
        time.sleep(0.001)
        
        # Mission 3: Trending or new content
        missions.append(self._generate_trending_mission())
        
        # Assign unique IDs based on timestamp
        for idx, mission in enumerate(missions):
            mission['id'] = f"{int(time.time() * 1000)}_{idx}"
        
        return missions[:3]  # Ensure max 3 missions
    
    def _analyze_progress(self, user_id: str, user_profile: Dict) -> Dict:
        """Analyze user's progress across all areas."""
        # TODO: Load from actual user data
        # For now, return mock data
        return {
            "coding": {
                "completed": 45,
                "total": 75,
                "percentage": 60,
                "recent_performance": "good"
            },
            "system_design": {
                "completed": 12,
                "total": 30,
                "percentage": 40,
                "recent_performance": "needs_improvement"
            },
            "ml_theory": {
                "completed": 28,
                "total": 35,
                "percentage": 80,
                "recent_performance": "excellent"
            },
            "streak_days": 7,
            "total_study_hours": 42
        }
    
    def _determine_focus_area(self, progress: Dict) -> str:
        """Determine what to focus on today based on progress."""
        # Find area with lowest percentage
        areas = {
            "Coding": progress["coding"]["percentage"],
            "System Design": progress["system_design"]["percentage"],
            "ML Theory": progress["ml_theory"]["percentage"]
        }
        
        # Sort by percentage
        sorted_areas = sorted(areas.items(), key=lambda x: x[1])
        
        # Focus on weakest + second weakest
        return f"{sorted_areas[0][0]} + {sorted_areas[1][0]}"
    
    def _get_weakest_area(self, progress: Dict) -> str:
        """Get the weakest area that needs attention."""
        areas = {
            "coding": progress["coding"]["percentage"],
            "system_design": progress["system_design"]["percentage"],
            "ml_theory": progress["ml_theory"]["percentage"]
        }
        
        return min(areas, key=areas.get)
    
    def _generate_insight(self, progress: Dict, user_profile: Dict) -> str:
        """Generate AI insight based on progress."""
        coding_pct = progress["coding"]["percentage"]
        sd_pct = progress["system_design"]["percentage"]
        theory_pct = progress["ml_theory"]["percentage"]
        
        insights = []
        
        if coding_pct >= 70:
            insights.append(f"💪 Coding is your strength ({coding_pct}%)")
        else:
            insights.append(f"⚠️ Coding needs more practice ({coding_pct}%)")
        
        if sd_pct < 50:
            insights.append(f"🎯 System Design is your top priority ({sd_pct}%)")
        
        if theory_pct >= 80:
            insights.append(f"🧠 ML Theory is solid ({theory_pct}%)")
        
        if progress["streak_days"] >= 7:
            insights.append(f"🔥 Amazing {progress['streak_days']}-day streak!")
        
        return " | ".join(insights)
    
    def _check_new_content(self) -> Optional[str]:
        """Check for new content from blogs/papers."""
        try:
            # Check dynamic question bank
            bank_file = self.data_dir / "dynamic_question_bank.json"
            if bank_file.exists():
                with open(bank_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Get latest question
                all_questions = []
                for category in data.get("questions", {}).values():
                    all_questions.extend(category)
                
                if all_questions:
                    # Sort by added_at
                    all_questions.sort(key=lambda x: x.get("added_at", ""), reverse=True)
                    latest = all_questions[0]
                    
                    source = latest.get("source", "").split(" - ")[0]
                    title = latest.get("title", "New content")
                    
                    return f"🔥 New from {source}: {title}"
        except:
            pass
        
        return None
    
    def _get_motivation(self, progress: Dict) -> str:
        """Get motivational message."""
        streak = progress["streak_days"]
        
        if streak >= 7:
            return f"🔥 {streak}-day streak! You're unstoppable!"
        elif streak >= 3:
            return f"💪 {streak} days in a row! Keep the momentum!"
        else:
            return "🚀 Let's build that streak! Start today!"
    
    def _generate_theory_mission(self, weak_areas: List[str]) -> Dict:
        """Generate ML theory mission."""
        topics = [
            ("Bias-Variance Tradeoff", "fundamentals"),
            ("Regularization (L1 vs L2)", "fundamentals"),
            ("Gradient Descent Variants", "fundamentals"),
            ("Evaluation Metrics (AUC, F1)", "fundamentals"),
            ("Loss Functions", "fundamentals"),
            ("Backpropagation", "deep_learning"),
            ("Attention Mechanism", "deep_learning")
        ]
        
        topic, domain = random.choice(topics)
        
        return {
            "id": 1,
            "type": "theory",
            "icon": "🧠",
            "title": f"ML Theory: {topic}",
            "description": "Understand the math, draw diagrams, explain tradeoffs",
            "duration": "30 min",
            "priority": "high",
            "completed": False,
            "link": f"https://www.google.com/search?q={topic.replace(' ', '+')}+machine+learning+interview",
            "link_label": "📚 去题库复习"
        }
    
    def _generate_system_design_mission(self, company: str) -> Dict:
        """Generate system design mission."""
        systems = {
            "Google": [("YouTube Recommendation", "youtube+recommendation+system+design"), ("Google Search Ranking", "google+search+ranking+system+design"), ("Gmail Spam Detection", "gmail+spam+detection+ML+system")],
            "Meta": [("News Feed Ranking", "facebook+news+feed+ranking+system+design"), ("Instagram Explore", "instagram+explore+recommendation"), ("Ads CTR Prediction", "ads+ctr+prediction+system+design")],
            "Netflix": [("Movie Recommendation", "netflix+recommendation+system+design"), ("Content Personalization", "netflix+personalization")],
            "Amazon": [("Product Recommendation", "amazon+product+recommendation+system"), ("Search Relevance", "amazon+search+relevance+ranking")],
            "OpenAI": [("LLM Serving System", "llm+serving+system+design+vllm"), ("RAG System", "rag+retrieval+augmented+generation+system+design")]
        }
        
        company_systems = systems.get(company, systems["Google"])
        system, search_q = random.choice(company_systems)
        
        return {
            "id": 2,
            "type": "system_design",
            "icon": "🏗️",
            "title": f"System Design: {system}",
            "description": "Design end-to-end: data → model → serving → scaling",
            "duration": "45 min",
            "priority": "high",
            "completed": False,
            "link": f"https://www.google.com/search?q={search_q}",
            "link_label": "📝 查看设计框架"
        }
    
    def _generate_coding_mission(self) -> Dict:
        """Generate coding mission."""
        problems = [
            {"name": "LRU Cache", "number": 146, "topic": "Design"},
            {"name": "Merge K Sorted Lists", "number": 23, "topic": "Heap"},
            {"name": "Binary Tree Level Order", "number": 102, "topic": "Tree"},
            {"name": "Longest Increasing Subsequence", "number": 300, "topic": "DP"},
            {"name": "Two Sum", "number": 1, "topic": "Hash Table"},
            {"name": "Median of Two Sorted Arrays", "number": 4, "topic": "Binary Search"},
            {"name": "Valid Parentheses", "number": 20, "topic": "Stack"},
            {"name": "Trapping Rain Water", "number": 42, "topic": "Two Pointers"},
        ]
        
        problem = random.choice(problems)
        
        return {
            "id": 3,
            "type": "coding",
            "icon": "💻",
            "title": f"Coding: LeetCode {problem['number']} - {problem['name']}",
            "description": f"Focus on {problem['topic']} patterns and edge cases",
            "duration": "30 min",
            "priority": "medium",
            "completed": False,
            "link": f"https://leetcode.com/problems/{problem['name'].lower().replace(' ', '-')}/",
            "link_label": "💻 去 LeetCode 做题"
        }
    
    def _generate_company_mission(self, company: str) -> Dict:
        """Generate company-specific mission."""
        # Reuse system design for now
        return self._generate_system_design_mission(company)
    
    def _generate_trending_mission(self) -> Dict:
        """Generate mission based on trending topics."""
        try:
            # Try to get from dynamic question bank
            bank_file = self.data_dir / "dynamic_question_bank.json"
            if bank_file.exists():
                with open(bank_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                all_questions = []
                for category in data.get("questions", {}).values():
                    all_questions.extend(category)
                
                if all_questions:
                    q = random.choice(all_questions)
                    return {
                        "id": 3,
                        "type": "trending",
                        "icon": "🔥",
                        "title": f"Trending: {q.get('topic', 'New Tech')}",
                        "description": q.get('title', ''),
                        "duration": "20 min",
                        "priority": "medium",
                        "completed": False,
                        "content": q
                    }
        except:
            pass
        
        # Fallback to coding
        return self._generate_coding_mission()


# Global instance
ai_coach = AICoach()
