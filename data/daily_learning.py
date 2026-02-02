"""
Smart Daily Learning Engine
Generates personalized daily study tasks based on user profile and goals
"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import random
import hashlib


class DailyLearningEngine:
    """Generates smart, personalized daily learning plans."""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent
        self.user_daily_file = self.data_dir / "user_daily_plans.json"
        self._ensure_data_file()
        
        # Load question bank
        try:
            from data.question_bank import QuestionBank
            self.question_bank = QuestionBank()
        except:
            self.question_bank = None
    
    def _ensure_data_file(self):
        if not self.user_daily_file.exists():
            self._save_data({"users": {}})
    
    def _load_data(self) -> Dict:
        try:
            with open(self.user_daily_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"users": {}}
    
    def _save_data(self, data: Dict):
        with open(self.user_daily_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def setup_user_profile(self, user_id: str, profile: Dict) -> bool:
        """Setup or update user learning profile."""
        data = self._load_data()
        
        data["users"][user_id] = {
            "profile": {
                "target_company": profile.get("target_company", "Google"),
                "target_role": profile.get("target_role", "MLE"),
                "target_level": profile.get("target_level", "L5"),
                "interview_date": profile.get("interview_date", ""),
                "daily_hours": profile.get("daily_hours", 2),
                "weak_areas": profile.get("weak_areas", ["LLM", "System Design"]),
                "strong_areas": profile.get("strong_areas", []),
                "preferred_style": profile.get("preferred_style", "balanced"),
                "setup_at": datetime.now().isoformat()
            },
            "progress": {
                "completed_questions": [],
                "completed_topics": [],
                "streak_days": 0,
                "last_study_date": None,
                "total_study_minutes": 0
            },
            "daily_plans": {}
        }
        
        self._save_data(data)
        return True
    
    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user's learning profile."""
        data = self._load_data()
        return data["users"].get(user_id)
    
    def generate_daily_plan(self, user_id: str, date: str = None) -> Dict:
        """Generate a personalized daily learning plan."""
        
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        data = self._load_data()
        user_data = data["users"].get(user_id)
        
        if not user_data:
            return self._generate_default_plan(date)
        
        profile = user_data["profile"]
        progress = user_data["progress"]
        
        # Check if plan already exists for today
        if date in user_data.get("daily_plans", {}):
            return user_data["daily_plans"][date]
        
        # Calculate days until interview
        days_left = self._calculate_days_left(profile.get("interview_date", ""))
        
        # Generate personalized plan
        plan = self._create_smart_plan(profile, progress, days_left, date)
        
        # Save the plan
        if "daily_plans" not in user_data:
            user_data["daily_plans"] = {}
        user_data["daily_plans"][date] = plan
        self._save_data(data)
        
        return plan
    
    def _calculate_days_left(self, interview_date: str) -> int:
        """Calculate days until interview."""
        if not interview_date:
            return 60  # Default assumption
        
        try:
            target = datetime.strptime(interview_date, "%Y-%m-%d")
            today = datetime.now()
            return max(0, (target - today).days)
        except:
            return 60
    
    def _create_smart_plan(self, profile: Dict, progress: Dict, days_left: int, date: str) -> Dict:
        """Create a smart, balanced daily plan."""
        
        daily_hours = profile.get("daily_hours", 2)
        total_minutes = daily_hours * 60
        
        target_company = profile.get("target_company", "Google")
        target_role = profile.get("target_role", "MLE")
        weak_areas = profile.get("weak_areas", [])
        
        # Determine phase based on days left
        if days_left > 30:
            phase = "foundation"
            phase_name = "🏗️ 基础夯实期"
            focus = "广度优先，打好基础"
        elif days_left > 14:
            phase = "intensive"
            phase_name = "🔥 强化冲刺期"
            focus = "深度练习，查漏补缺"
        elif days_left > 3:
            phase = "review"
            phase_name = "📝 复习巩固期"
            focus = "回顾重点，保持状态"
        else:
            phase = "final"
            phase_name = "🎯 最后准备"
            focus = "放松心态，轻松复习"
        
        # Time allocation based on phase
        if phase == "foundation":
            time_split = {"theory": 0.3, "coding": 0.3, "system_design": 0.25, "behavioral": 0.15}
        elif phase == "intensive":
            time_split = {"theory": 0.2, "coding": 0.35, "system_design": 0.3, "behavioral": 0.15}
        elif phase == "review":
            time_split = {"theory": 0.25, "coding": 0.25, "system_design": 0.3, "behavioral": 0.2}
        else:
            time_split = {"theory": 0.2, "coding": 0.2, "system_design": 0.3, "behavioral": 0.3}
        
        # Priority boost for weak areas
        for area in weak_areas:
            area_key = self._map_area_to_key(area)
            if area_key in time_split:
                time_split[area_key] = min(0.4, time_split[area_key] * 1.3)
        
        # Normalize
        total = sum(time_split.values())
        time_split = {k: v/total for k, v in time_split.items()}
        
        # Generate tasks
        tasks = []
        task_id = 1
        
        # Morning: Theory/Concepts (best for learning)
        theory_mins = int(total_minutes * time_split["theory"])
        if theory_mins >= 15:
            tasks.append({
                "id": task_id,
                "type": "theory",
                "icon": "📚",
                "title": self._get_theory_topic(weak_areas, progress, target_role),
                "description": "阅读理解，做笔记",
                "duration_min": theory_mins,
                "time_slot": "早上 9:00",
                "priority": "high" if "theory" in [self._map_area_to_key(a) for a in weak_areas] else "medium",
                "resources": self._get_theory_resources(weak_areas),
                "completed": False
            })
            task_id += 1
        
        # Mid-morning: Coding Practice
        coding_mins = int(total_minutes * time_split["coding"])
        if coding_mins >= 20:
            coding_questions = self._get_coding_questions(target_company, progress, 2)
            tasks.append({
                "id": task_id,
                "type": "coding",
                "icon": "💻",
                "title": "算法题练习",
                "description": f"完成 {len(coding_questions)} 道题",
                "duration_min": coding_mins,
                "time_slot": "上午 10:30",
                "priority": "high",
                "questions": coding_questions,
                "completed": False
            })
            task_id += 1
        
        # Afternoon: System Design
        sd_mins = int(total_minutes * time_split["system_design"])
        if sd_mins >= 25:
            sd_topic = self._get_system_design_topic(target_company, progress)
            tasks.append({
                "id": task_id,
                "type": "system_design",
                "icon": "🏗️",
                "title": f"系统设计: {sd_topic}",
                "description": "画图 + 写文档 + 自己讲一遍",
                "duration_min": sd_mins,
                "time_slot": "下午 2:00",
                "priority": "high",
                "topic": sd_topic,
                "steps": [
                    "明确需求 (5min)",
                    "设计核心架构 (15min)",
                    "深入一个组件 (10min)",
                    "讨论 trade-offs (5min)"
                ],
                "completed": False
            })
            task_id += 1
        
        # Evening: Behavioral + Review
        bq_mins = int(total_minutes * time_split["behavioral"])
        if bq_mins >= 15:
            bq_question = self._get_behavioral_question(target_company, progress)
            tasks.append({
                "id": task_id,
                "type": "behavioral",
                "icon": "🗣️",
                "title": "Behavioral 准备",
                "description": "用 STAR 方法准备一个故事",
                "duration_min": bq_mins,
                "time_slot": "晚上 8:00",
                "priority": "medium",
                "question": bq_question,
                "tips": [
                    "Situation: 什么背景？",
                    "Task: 你的任务是什么？",
                    "Action: 你做了什么？",
                    "Result: 结果如何？学到什么？"
                ],
                "completed": False
            })
            task_id += 1
        
        # Bonus: Quick review task
        tasks.append({
            "id": task_id,
            "type": "review",
            "icon": "✨",
            "title": "今日回顾",
            "description": "用自己的话总结今天学到的3个要点",
            "duration_min": 10,
            "time_slot": "睡前",
            "priority": "low",
            "prompts": [
                "今天学到最重要的一点是...",
                "我还不太确定的是...",
                "明天我要...",
            ],
            "completed": False
        })
        
        return {
            "date": date,
            "phase": phase,
            "phase_name": phase_name,
            "focus": focus,
            "days_left": days_left,
            "target_company": target_company,
            "total_minutes": total_minutes,
            "tasks": tasks,
            "motivation": self._get_daily_motivation(days_left, phase),
            "generated_at": datetime.now().isoformat()
        }
    
    def _map_area_to_key(self, area: str) -> str:
        """Map weak area to time split key."""
        area_lower = area.lower()
        if any(x in area_lower for x in ["llm", "ml", "theory", "算法"]):
            return "theory"
        elif any(x in area_lower for x in ["coding", "编程", "leetcode"]):
            return "coding"
        elif any(x in area_lower for x in ["system", "系统", "设计"]):
            return "system_design"
        elif any(x in area_lower for x in ["behavioral", "bq", "行为"]):
            return "behavioral"
        return "theory"
    
    def _get_theory_topic(self, weak_areas: List[str], progress: Dict, role: str) -> str:
        """Get a theory topic to study."""
        topics = {
            "LLM": [
                "Transformer 架构详解",
                "Attention 机制原理",
                "LoRA/QLoRA 微调",
                "RAG 系统设计",
                "Prompt Engineering 技巧",
                "LLM 推理优化 (KV Cache)",
                "RLHF 和对齐技术"
            ],
            "ML": [
                "Bias-Variance Tradeoff",
                "正则化 L1 vs L2",
                "评估指标选择",
                "梯度下降优化器",
                "过拟合诊断与处理",
                "特征工程最佳实践"
            ],
            "System Design": [
                "推荐系统架构",
                "搜索排序系统",
                "实时特征系统",
                "模型服务架构",
                "A/B 测试平台"
            ]
        }
        
        # Prioritize weak areas
        for area in weak_areas:
            if area in topics:
                completed = progress.get("completed_topics", [])
                available = [t for t in topics[area] if t not in completed]
                if available:
                    return random.choice(available)
        
        # Default
        all_topics = [t for topics_list in topics.values() for t in topics_list]
        return random.choice(all_topics)
    
    def _get_theory_resources(self, weak_areas: List[str]) -> List[Dict]:
        """Get resources for theory study."""
        resources = []
        
        if "LLM" in weak_areas or not weak_areas:
            resources.append({
                "name": "Attention Is All You Need",
                "type": "paper",
                "url": "https://arxiv.org/abs/1706.03762"
            })
        
        resources.append({
            "name": "ML Interview 知识点总结",
            "type": "notes",
            "url": "#"  # Internal link
        })
        
        return resources[:3]
    
    def _get_coding_questions(self, company: str, progress: Dict, count: int) -> List[Dict]:
        """Get coding questions for practice."""
        completed = progress.get("completed_questions", [])
        
        # Sample questions (in real app, pull from question bank)
        questions = [
            {"id": "q1", "title": "两数之和", "difficulty": "Easy", "topic": "Array", "source": "LeetCode 1"},
            {"id": "q2", "title": "合并K个排序链表", "difficulty": "Hard", "topic": "Heap", "source": "LeetCode 23"},
            {"id": "q3", "title": "LRU Cache", "difficulty": "Medium", "topic": "Design", "source": "LeetCode 146"},
            {"id": "q4", "title": "二叉树层序遍历", "difficulty": "Medium", "topic": "Tree", "source": "LeetCode 102"},
            {"id": "q5", "title": "最长递增子序列", "difficulty": "Medium", "topic": "DP", "source": "LeetCode 300"},
            {"id": "q6", "title": "实现 Trie", "difficulty": "Medium", "topic": "Trie", "source": "LeetCode 208"},
        ]
        
        available = [q for q in questions if q["id"] not in completed]
        if len(available) < count:
            available = questions  # Reset if all done
        
        return random.sample(available, min(count, len(available)))
    
    def _get_system_design_topic(self, company: str, progress: Dict) -> str:
        """Get a system design topic."""
        company_topics = {
            "Google": ["搜索排序系统", "YouTube 推荐", "Google Maps 路径规划", "Gmail 垃圾邮件检测"],
            "Meta": ["Facebook Feed 排序", "Instagram Explore", "广告 CTR 预估", "内容审核系统"],
            "Amazon": ["商品推荐系统", "搜索相关性", "欺诈检测", "Prime Video 推荐"],
            "TikTok": ["短视频推荐", "实时内容审核", "直播推荐", "音乐推荐"],
            "OpenAI": ["LLM Serving 系统", "RAG 知识问答", "内容安全检测", "模型评估平台"],
            "Snap": ["AR 滤镜推荐", "Stories 排序", "好友推荐", "广告系统"],
            "Netflix": ["视频推荐系统", "内容个性化", "A/B 测试平台", "带宽优化"],
        }
        
        topics = company_topics.get(company, company_topics["Google"])
        completed = progress.get("completed_topics", [])
        available = [t for t in topics if t not in completed]
        
        return random.choice(available) if available else random.choice(topics)
    
    def _get_behavioral_question(self, company: str, progress: Dict) -> str:
        """Get a behavioral question."""
        questions = [
            "Tell me about a project you led and the impact you made.",
            "Describe a time when you had a conflict with a teammate.",
            "Tell me about a time you failed and what you learned.",
            "How do you handle ambiguity in a project?",
            "Describe a situation where you had to make a difficult decision.",
            "Tell me about a time you went above and beyond.",
            "How do you prioritize when you have multiple deadlines?",
            "Describe a time you had to convince others of your idea.",
        ]
        
        return random.choice(questions)
    
    def _get_daily_motivation(self, days_left: int, phase: str) -> str:
        """Get daily motivation message."""
        messages = {
            "foundation": [
                "🌱 每天进步一点点，面试时你会感谢现在的自己！",
                "💪 基础打得越牢，面试越从容！",
                "📚 今天的积累，是明天的底气！"
            ],
            "intensive": [
                "🔥 冲刺阶段，保持专注！你已经很棒了！",
                "⚡ 高强度练习 = 面试时的条件反射！",
                "🎯 每解决一道难题，就离 offer 更近一步！"
            ],
            "review": [
                "📝 复习不是重复，是更深的理解！",
                "✨ 相信自己的准备，你已经很强了！",
                "🧘 保持节奏，稳中求进！"
            ],
            "final": [
                "🎉 准备已经足够，相信自己！",
                "😌 放松心态，正常发挥就是超常发挥！",
                "🌟 你已经是最好的自己了，加油！"
            ]
        }
        
        phase_messages = messages.get(phase, messages["foundation"])
        return random.choice(phase_messages)
    
    def _generate_default_plan(self, date: str) -> Dict:
        """Generate a default plan for new users."""
        return {
            "date": date,
            "phase": "setup",
            "phase_name": "📋 设置你的目标",
            "focus": "先设置你的面试目标",
            "days_left": None,
            "target_company": None,
            "total_minutes": 120,
            "tasks": [
                {
                    "id": 1,
                    "type": "setup",
                    "icon": "🎯",
                    "title": "设置学习目标",
                    "description": "告诉系统你的目标公司、面试日期",
                    "duration_min": 10,
                    "time_slot": "现在",
                    "priority": "high",
                    "completed": False
                }
            ],
            "motivation": "🚀 设置好目标，开始你的面试准备之旅！",
            "generated_at": datetime.now().isoformat()
        }
    
    def complete_task(self, user_id: str, date: str, task_id: int) -> bool:
        """Mark a task as completed."""
        data = self._load_data()
        
        if user_id not in data["users"]:
            return False
        
        user_data = data["users"][user_id]
        
        if date not in user_data.get("daily_plans", {}):
            return False
        
        for task in user_data["daily_plans"][date]["tasks"]:
            if task["id"] == task_id:
                task["completed"] = True
                task["completed_at"] = datetime.now().isoformat()
                
                # Update progress
                user_data["progress"]["total_study_minutes"] = (
                    user_data["progress"].get("total_study_minutes", 0) + 
                    task.get("duration_min", 0)
                )
                
                # Track completed items
                if task["type"] == "coding":
                    for q in task.get("questions", []):
                        if q["id"] not in user_data["progress"]["completed_questions"]:
                            user_data["progress"]["completed_questions"].append(q["id"])
                elif task["type"] == "system_design":
                    topic = task.get("topic", "")
                    if topic and topic not in user_data["progress"]["completed_topics"]:
                        user_data["progress"]["completed_topics"].append(topic)
                
                self._save_data(data)
                return True
        
        return False
    
    def get_weekly_summary(self, user_id: str) -> Dict:
        """Get weekly learning summary."""
        data = self._load_data()
        user_data = data["users"].get(user_id, {})
        progress = user_data.get("progress", {})
        
        return {
            "total_questions": len(progress.get("completed_questions", [])),
            "total_topics": len(progress.get("completed_topics", [])),
            "total_minutes": progress.get("total_study_minutes", 0),
            "streak_days": progress.get("streak_days", 0)
        }


# Global instance
daily_learning = DailyLearningEngine()
