"""
Smart Learning Planner
Generates personalized daily study plans based on user goals and progress
"""
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import random


class LearningPlanner:
    """Generates and manages personalized learning plans."""
    
    # Study templates based on target role and timeline
    STUDY_TEMPLATES = {
        "mle_8week": {
            "name": "MLE 8周冲刺计划",
            "duration_weeks": 8,
            "target_role": "MLE",
            "phases": [
                {
                    "week": [1, 2],
                    "name": "基础巩固",
                    "focus": ["ml-fundamentals", "coding"],
                    "daily_tasks": {
                        "theory": 60,  # minutes
                        "coding": 45,
                        "system_design": 0,
                        "mock_interview": 0
                    },
                    "topics": [
                        "线性回归、逻辑回归原理",
                        "决策树、随机森林、XGBoost",
                        "SVM 原理与核函数",
                        "聚类算法 (K-Means, DBSCAN)",
                        "降维 (PCA, t-SNE)",
                        "评估指标 (Precision, Recall, F1, AUC)",
                        "交叉验证与模型选择",
                        "特征工程基础"
                    ]
                },
                {
                    "week": [3, 4],
                    "name": "深度学习核心",
                    "focus": ["deep-learning", "nlp", "cv"],
                    "daily_tasks": {
                        "theory": 45,
                        "coding": 45,
                        "system_design": 30,
                        "mock_interview": 0
                    },
                    "topics": [
                        "神经网络基础 (前向/反向传播)",
                        "CNN 架构 (ResNet, VGG)",
                        "RNN/LSTM/GRU",
                        "Transformer & Attention",
                        "BERT, GPT 原理",
                        "优化器 (SGD, Adam, AdaGrad)",
                        "正则化 (Dropout, BatchNorm)",
                        "迁移学习"
                    ]
                },
                {
                    "week": [5, 6],
                    "name": "系统设计专项",
                    "focus": ["system-design", "mlops"],
                    "daily_tasks": {
                        "theory": 30,
                        "coding": 30,
                        "system_design": 60,
                        "mock_interview": 30
                    },
                    "topics": [
                        "推荐系统设计 (YouTube, TikTok)",
                        "搜索排序系统",
                        "广告系统架构",
                        "RAG 系统设计",
                        "实时特征系统",
                        "模型服务架构",
                        "A/B 测试设计",
                        "数据管道设计"
                    ]
                },
                {
                    "week": [7, 8],
                    "name": "冲刺模拟",
                    "focus": ["mock-interview", "review"],
                    "daily_tasks": {
                        "theory": 20,
                        "coding": 30,
                        "system_design": 30,
                        "mock_interview": 60
                    },
                    "topics": [
                        "全流程模拟面试",
                        "行为面试准备",
                        "弱项查漏补缺",
                        "高频题目复习",
                        "公司特定准备",
                        "简历 Story 梳理"
                    ]
                }
            ]
        },
        "mle_4week": {
            "name": "MLE 4周速成计划",
            "duration_weeks": 4,
            "target_role": "MLE",
            "phases": [
                {
                    "week": [1],
                    "name": "ML 基础速览",
                    "focus": ["ml-fundamentals"],
                    "daily_tasks": {
                        "theory": 60,
                        "coding": 60,
                        "system_design": 0,
                        "mock_interview": 0
                    },
                    "topics": [
                        "经典 ML 算法快速复习",
                        "深度学习核心概念",
                        "常见面试题型"
                    ]
                },
                {
                    "week": [2],
                    "name": "深度学习 & NLP",
                    "focus": ["deep-learning", "nlp"],
                    "daily_tasks": {
                        "theory": 45,
                        "coding": 45,
                        "system_design": 30,
                        "mock_interview": 0
                    },
                    "topics": [
                        "Transformer 深入",
                        "LLM 相关问题",
                        "RAG/Fine-tuning"
                    ]
                },
                {
                    "week": [3],
                    "name": "系统设计集训",
                    "focus": ["system-design"],
                    "daily_tasks": {
                        "theory": 30,
                        "coding": 30,
                        "system_design": 60,
                        "mock_interview": 30
                    },
                    "topics": [
                        "推荐/搜索/广告系统",
                        "MLOps 核心问题",
                        "案例分析"
                    ]
                },
                {
                    "week": [4],
                    "name": "模拟冲刺",
                    "focus": ["mock-interview"],
                    "daily_tasks": {
                        "theory": 20,
                        "coding": 30,
                        "system_design": 30,
                        "mock_interview": 60
                    },
                    "topics": [
                        "全真模拟",
                        "弱项补强",
                        "行为面试"
                    ]
                }
            ]
        },
        "sde_12week_neetcode": {
            "name": "SDE Neetcode 250 狂飙计划",
            "duration_weeks": 12,
            "target_role": "SDE",
            "phases": [
                {
                    "week": [1, 2, 3, 4],
                    "name": "数据结构与基础算法",
                    "focus": ["coding"],
                    "daily_tasks": {
                        "theory": 20,
                        "coding": 90,
                        "system_design": 0,
                        "mock_interview": 0
                    },
                    "topics": [
                        "Arrays & Hashing",
                        "Two Pointers",
                        "Sliding Window",
                        "Stack",
                        "Binary Search",
                        "Linked List"
                    ]
                },
                {
                    "week": [5, 6, 7, 8],
                    "name": "进阶结构与树图",
                    "focus": ["coding"],
                    "daily_tasks": {
                        "theory": 20,
                        "coding": 90,
                        "system_design": 0,
                        "mock_interview": 10
                    },
                    "topics": [
                        "Trees & Tries",
                        "Heap / Priority Queue",
                        "Backtracking",
                        "Graphs",
                        "Advanced Graphs"
                    ]
                },
                {
                    "week": [9, 10, 11, 12],
                    "name": "动态规划与系统设计",
                    "focus": ["coding", "system-design"],
                    "daily_tasks": {
                        "theory": 0,
                        "coding": 90,
                        "system_design": 45,
                        "mock_interview": 30
                    },
                    "topics": [
                        "1D Dynamic Programming",
                        "2D Dynamic Programming",
                        "Greedy",
                        "Math & Geometry",
                        "Bit Manipulation",
                        "System Design Primer"
                    ]
                }
            ]
        }
    }
    
    # Daily task types with activities
    TASK_TYPES = {
        "theory": {
            "name": "理论学习",
            "icon": "📚",
            "activities": [
                "阅读博客文章",
                "观看教程视频",
                "复习知识点笔记",
                "阅读论文摘要"
            ]
        },
        "coding": {
            "name": "编程练习",
            "icon": "💻",
            "activities": [
                "Neetcode 面试原题",
                "LeetCode 每日一题",
                "ML 算法实现",
                "Bug Debugging 练习"
            ]
        },
        "system_design": {
            "name": "系统设计",
            "icon": "🏗️",
            "activities": [
                "设计题练习",
                "阅读系统设计案例",
                "画架构图",
                "准备 Clarifying Questions"
            ]
        },
        "mock_interview": {
            "name": "模拟面试",
            "icon": "🎤",
            "activities": [
                "自我模拟答题",
                "录音回放改进",
                "与朋友模拟",
                "AI 模拟面试"
            ]
        }
    }
    
    def __init__(self):
        self.plans_file = Path(__file__).parent / "user_study_plans.json"
        self._ensure_file()
    
    def _ensure_file(self):
        if not self.plans_file.exists():
            self.plans_file.write_text('{"plans": {}}', encoding='utf-8')
    
    def _load_plans(self) -> Dict:
        try:
            with open(self.plans_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"plans": {}}
    
    def _save_plans(self, data: Dict):
        with open(self.plans_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def create_plan(self, user_id: str, template_id: str, 
                    start_date: Optional[datetime] = None,
                    daily_hours: float = 2.0) -> Dict:
        """Create a new study plan for a user."""
        if template_id not in self.STUDY_TEMPLATES:
            raise ValueError(f"Unknown template: {template_id}")
        
        template = self.STUDY_TEMPLATES[template_id]
        start = start_date or datetime.now()
        
        plan = {
            "id": f"{user_id}_{template_id}_{start.strftime('%Y%m%d')}",
            "user_id": user_id,
            "template_id": template_id,
            "template_name": template["name"],
            "start_date": start.isoformat(),
            "end_date": (start + timedelta(weeks=template["duration_weeks"])).isoformat(),
            "daily_hours": daily_hours,
            "current_week": 1,
            "current_day": 1,
            "completed_days": 0,
            "total_days": template["duration_weeks"] * 7,
            "phases": template["phases"],
            "daily_logs": {},
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        # Save to file
        data = self._load_plans()
        data["plans"][user_id] = plan
        self._save_plans(data)
        
        return plan
    
    def get_user_plan(self, user_id: str) -> Optional[Dict]:
        """Get user's current study plan."""
        data = self._load_plans()
        return data["plans"].get(user_id)
    
    def get_today_tasks(self, user_id: str) -> Dict:
        """Generate today's study tasks based on the plan."""
        plan = self.get_user_plan(user_id)
        
        if not plan or plan.get("status") != "active":
            return self._get_default_tasks()
        
        # Calculate current phase
        start_date = datetime.fromisoformat(plan["start_date"])
        days_elapsed = (datetime.now() - start_date).days
        current_week = min(days_elapsed // 7 + 1, len(plan["phases"]))
        
        # Find current phase
        current_phase = None
        for phase in plan["phases"]:
            if current_week in phase["week"]:
                current_phase = phase
                break
        
        if not current_phase:
            current_phase = plan["phases"][-1]
        
        # Generate tasks
        tasks = []
        daily_tasks = current_phase["daily_tasks"]
        topics = current_phase["topics"]
        
        for task_type, minutes in daily_tasks.items():
            if minutes > 0:
                task_info = self.TASK_TYPES.get(task_type, {})
                activities = task_info.get("activities", [])
                
                tasks.append({
                    "type": task_type,
                    "name": task_info.get("name", task_type),
                    "icon": task_info.get("icon", "📝"),
                    "duration_minutes": minutes,
                    "suggested_activity": random.choice(activities) if activities else "",
                    "topic": random.choice(topics) if topics else "",
                    "completed": False
                })
        
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "week": current_week,
            "phase_name": current_phase["name"],
            "focus_areas": current_phase["focus"],
            "tasks": tasks,
            "total_minutes": sum(daily_tasks.values()),
            "motivational_quote": self._get_daily_quote()
        }
    
    def _get_default_tasks(self) -> Dict:
        """Return default tasks for users without a plan."""
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "week": 0,
            "phase_name": "自由学习",
            "focus_areas": ["general"],
            "tasks": [
                {
                    "type": "theory",
                    "name": "理论学习",
                    "icon": "📚",
                    "duration_minutes": 30,
                    "suggested_activity": "阅读一篇技术博客",
                    "topic": "今日推荐",
                    "completed": False
                },
                {
                    "type": "coding",
                    "name": "编程练习",
                    "icon": "💻",
                    "duration_minutes": 30,
                    "suggested_activity": "完成一道 LeetCode 题",
                    "topic": "数据结构",
                    "completed": False
                }
            ],
            "total_minutes": 60,
            "motivational_quote": self._get_daily_quote()
        }
    
    def _get_daily_quote(self) -> str:
        """Get a motivational quote for the day."""
        quotes = [
            "每一次面试都是成长的机会 💪",
            "今天的努力，明天的 Offer 🎯",
            "坚持就是胜利，加油！🔥",
            "面试官也是人，放轻松 😊",
            "你比你想象的更优秀 ⭐",
            "一步一个脚印，稳扎稳打 🚀",
            "失败是成功之母，继续前进 💎",
            "准备充分，自信应对 🏆"
        ]
        # Use date as seed for consistent daily quote
        day_seed = int(datetime.now().strftime("%Y%m%d"))
        random.seed(day_seed)
        quote = random.choice(quotes)
        random.seed()  # Reset seed
        return quote
    
    def complete_task(self, user_id: str, task_type: str) -> bool:
        """Mark a task as completed."""
        plan = self.get_user_plan(user_id)
        if not plan:
            return False
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Initialize daily log if needed
        if today not in plan.get("daily_logs", {}):
            plan["daily_logs"][today] = {"completed_tasks": [], "total_minutes": 0}
        
        # Add completed task
        if task_type not in plan["daily_logs"][today]["completed_tasks"]:
            plan["daily_logs"][today]["completed_tasks"].append(task_type)
            
            # Update stats
            plan["completed_days"] = len(plan["daily_logs"])
        
        # Save
        data = self._load_plans()
        data["plans"][user_id] = plan
        self._save_plans(data)
        
        return True
    
    def get_progress(self, user_id: str) -> Dict:
        """Get user's study progress."""
        plan = self.get_user_plan(user_id)
        
        if not plan:
            return {
                "has_plan": False,
                "progress_percent": 0,
                "streak_days": 0
            }
        
        total_days = plan.get("total_days", 1)
        completed_days = plan.get("completed_days", 0)
        
        # Calculate streak
        streak = 0
        today = datetime.now().date()
        for i in range(30):  # Check last 30 days
            check_date = (today - timedelta(days=i)).isoformat()
            if check_date in plan.get("daily_logs", {}):
                streak += 1
            else:
                break
        
        return {
            "has_plan": True,
            "plan_name": plan.get("template_name", ""),
            "progress_percent": min(100, int(completed_days / total_days * 100)),
            "completed_days": completed_days,
            "total_days": total_days,
            "streak_days": streak,
            "current_week": plan.get("current_week", 1)
        }
    
    def get_available_templates(self) -> List[Dict]:
        """Get list of available study plan templates."""
        templates = []
        for tid, template in self.STUDY_TEMPLATES.items():
            templates.append({
                "id": tid,
                "name": template["name"],
                "duration_weeks": template["duration_weeks"],
                "target_role": template["target_role"],
                "description": f"{template['duration_weeks']}周计划，适合 {template['target_role']} 面试准备"
            })
        return templates


# Global instance
learning_planner = LearningPlanner()


# Helper functions
def create_study_plan(user_id: str, template_id: str) -> Dict:
    return learning_planner.create_plan(user_id, template_id)

def get_today_study_tasks(user_id: str) -> Dict:
    return learning_planner.get_today_tasks(user_id)

def get_study_progress(user_id: str) -> Dict:
    return learning_planner.get_progress(user_id)

def mark_task_complete(user_id: str, task_type: str) -> bool:
    return learning_planner.complete_task(user_id, task_type)

def get_plan_templates() -> List[Dict]:
    return learning_planner.get_available_templates()
