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

# Try to import knowledge evolver for dynamic questions
try:
    from data.knowledge_evolver import knowledge_evolver
    HAS_EVOLVER = True
except ImportError:
    HAS_EVOLVER = False

try:
    from data.supabase_client import learning_store, is_supabase_configured
    HAS_SUPABASE = True
except ImportError:
    HAS_SUPABASE = False

class DailyLearningEngine:
    """Generates smart, personalized daily learning plans with dynamic evolution."""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent
        self.user_daily_file = self.data_dir / "user_daily_plans.json"
        self.use_supabase = HAS_SUPABASE and is_supabase_configured()
        
        if not self.use_supabase:
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
        if not self.use_supabase:
            try:
                with open(self.user_daily_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {"users": {}}
        return {"users": {}}
    
    def _save_data(self, data: Dict):
        if not self.use_supabase:
            with open(self.user_daily_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

    def _get_user_data(self, user_id: str) -> Optional[Dict]:
        if self.use_supabase:
            return learning_store.get_daily_profile(user_id)
        data = self._load_data()
        return data["users"].get(user_id)

    def _save_user_data(self, user_id: str, user_data: Dict):
        if self.use_supabase:
            learning_store.save_daily_profile(
                user_id,
                user_data.get("profile", {}),
                user_data.get("progress", {}),
                user_data.get("daily_plans", {})
            )
        else:
            data = self._load_data()
            if "users" not in data:
                data["users"] = {}
            data["users"][user_id] = user_data
            self._save_data(data)
    
    def setup_user_profile(self, user_id: str, profile: Dict) -> bool:
        """Setup or update user learning profile."""
        user_data = {
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
        self._save_user_data(user_id, user_data)
        return True
    
    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user's learning profile."""
        user_data = self._get_user_data(user_id)
        return {"profile": user_data["profile"], "progress": user_data["progress"]} if user_data else None
    
    def generate_daily_plan(self, user_id: str, date: str = None) -> Dict:
        """Generate a personalized daily learning plan."""
        
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        user_data = self._get_user_data(user_id)
        
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
        self._save_user_data(user_id, user_data)
        
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
        """Get a theory/fundamentals topic to study."""
        topics = {
            "ML": [
                # ML Foundations
                "Bias-Variance Tradeoff (偏差-方差权衡)",
                "Regularization: L1 vs L2 (正则化)",
                "Gradient Descent Variants (SGD, Adam, RMSprop)",
                "Activation Functions (ReLU, Gelu, Swish)",
                "Batch Normalization & Layer Normalization",
                "Evaluation Metrics (AUC, ROC, F1, Precision/Recall)",
                "Loss Functions (Cross Entropy, Hinge, Huber)",
                "Decision Trees & Random Forests (原理与推导)",
                "XGBoost/LightGBM (核心原理与区别)",
                "K-Means vs GMM (聚类算法)",
                "PCA & t-SNE (降维技术)",
                "SVM (Kernel Trick, Margins)",
                "Naive Bayes (朴素贝叶斯)",
                "Logistic Regression (推导与优缺点)"
            ],
            "DL": [
                # Deep Learning
                "Backpropagation (反向传播推导)",
                "CNN Architectures (ResNet, EfficientNet)",
                "RNN/LSTM/GRU (原理与Vanishing Gradient)",
                "Dropout & Implementation",
                "Weight Initialization (Xavier, He)",
                "Optimizers (Momentum, AdamW)"
            ],
            "LLM": [
                # GenAI & LLM
                "Transformer Architecture (Encoder/Decoder)",
                "Self-Attention Mechanism (Q, K, V计算)",
                "Positional Encoding (RoPE, ALiBi)",
                "LLM Training: Pre-training vs Fine-tuning",
                "PEFT: LoRA, QLoRA, Prefix Tuning",
                "RLHF: PPO, DPO",
                "Inference Optimization (KV Cache, PagedAttention)",
                "RAG Systems (Retrieval, Vector DBs)",
                "Prompt Engineering (CoT, ToT)",
                "Scaling Laws (Chinchilla)"
            ]
        }
        
        # Determine focus based on weak areas
        candidates = []
        if "ML" in weak_areas or "theory" in [self._map_area_to_key(a) for a in weak_areas]:
            candidates.extend(topics["ML"])
        
        # Always include some ML basics if specifically requested or early phase
        candidates.extend(topics["ML"]) 
        
        if "LLM" in weak_areas:
            candidates.extend(topics["LLM"])
        else:
            candidates.extend(topics["DL"]) # Add DL basics generally
            
        # Filter completed
        completed = progress.get("completed_topics", [])
        available = [t for t in candidates if t not in completed]
        
        return random.choice(available) if available else random.choice(candidates)

    def _get_system_design_topic(self, company: str, progress: Dict) -> str:
        """Get a system design topic."""
        # Core ML System Design Topics
        core_topics = [
            "Recommendation System (推荐系统通用架构)",
            "Search Ranking System (搜索排序)",
            "Personalized News Feed (信息流)",
            "Ad Click Prediction (CTR 预估)",
            "Video Recommendation (YouTube/TikTok类)",
            "Image Search System (以图搜图)",
            "Near-line/Real-time Updates (实时更新)",
            "Feature Store Design (特征平台)",
            "Model Monitoring & Training Pipeline (MLOps)",
            "LLM RAG System Design (企业级知识库)"
        ]
        
        company_specific = {
            "Google": ["YouTube Recommendation", "Google Search Ranking", "Google Photos Search", "Translate System"],
            "Meta": ["News Feed Ranking", "Instagram Explore", "Ads Ranking", "Friend Recommendation"],
            "Amazon": ["Product Recommendation", "People Also Bought", "Supply Chain Demand Forecasting"],
            "TikTok": ["Short Video Recommendation", "Live Streaming Rec", "Content Moderation System"],
            "Uber": ["ETA Prediction", "Surge Pricing", "Driver-Rider Matching", "UberEats Ranking"],
            "Netflix": ["Movie Recommendation", "Homepage Personalization", "Artwork Personalization"],
            "LinkedIn": ["Job Recommendation", "People You May Know", "Feed Ranking"],
        }
        
        # Mix core topics with company specific ones
        topics = core_topics + company_specific.get(company, [])
        
        completed = progress.get("completed_topics", [])
        available = [t for t in topics if t not in completed]
        
        return random.choice(available) if available else random.choice(topics)

    def _create_smart_plan(self, profile: Dict, progress: Dict, days_left: int, date: str) -> Dict:
        """Create a smart, balanced daily plan."""
        
        # ... (keep existing logic) ...
        daily_hours = profile.get("daily_hours", 2)
        total_minutes = daily_hours * 60
        
        target_company = profile.get("target_company", "Google")
        weak_areas = profile.get("weak_areas", [])
        
        tasks = []
        task_id = 1
        
        # 1. ML Fundamentals (Always included now)
        theory_mins = 30
        tasks.append({
            "id": task_id,
            "type": "theory",
            "icon": "🧠", # Brain icon for theory
            "title": self._get_theory_topic(weak_areas, progress, profile.get("target_role", "MLE")),
            "description": "复习核心概念、公式推导与优缺点",
            "duration_min": theory_mins,
            "time_slot": "上午 9:00",
            "priority": "high",
            "completed": False
        })
        task_id += 1
        
        # 2. Coding Practice
        coding_mins = 45 
        coding_questions = self._get_coding_questions(target_company, progress, 2)
        tasks.append({
            "id": task_id,
            "type": "coding",
            "icon": "💻",
            "title": "算法题练习",
            "description": f"完成 {len(coding_questions)} 道题 (重点：数据结构)",
            "duration_min": coding_mins,
            "time_slot": "上午 10:00",
            "priority": "high",
            "questions": coding_questions,
            "completed": False
        })
        task_id += 1

        # 2.5: Inject Dynamic/Trending Question if available (Evolution Mechanism)
        if HAS_EVOLVER:
            try:
                trending_questions = knowledge_evolver.get_latest_questions(limit=3)
                # Filter out seen questions
                seen_ids = progress.get("completed_questions", []) + progress.get("completed_topics", [])
                new_trending = [q for q in trending_questions if q.get("source") not in seen_ids]
                
                if new_trending:
                    trend_q = new_trending[0]
                    tasks.append({
                        "id": task_id,
                        "type": "trending",
                        "icon": "🔥",
                        "title": f"技术前沿: {trend_q.get('topic', 'New Tech')}",
                        "description": f"源自最新论文/博客: {trend_q.get('title')}",
                        "duration_min": 15,
                        "time_slot": "午休后",
                        "priority": "medium",
                        "content": trend_q,  # Store full content
                        "completed": False
                    })
                    task_id += 1
            except Exception as e:
                pass # Fail silently on dynamic fetch

        
        # 3. ML System Design (Always included for MLE)
        sd_mins = 45
        sd_topic = self._get_system_design_topic(target_company, progress)
        tasks.append({
            "id": task_id,
            "type": "system_design",
            "icon": "🏗️",
            "title": f"ML系统设计: {sd_topic}",
            "description": "设计数据流、模型选择、在线/离线架构",
            "duration_min": sd_mins,
            "time_slot": "下午 2:00",
            "priority": "high",
            "topic": sd_topic,
            "steps": [
                "1. 需求分析 (Metrics, Constraints)",
                "2. 数据工程 (Data, Features, Labels)",
                "3. 模型设计 (Model Selection, Loss)",
                "4. 系统架构 (Training, Serving, Pipeline)",
                "5. 扩展性与优化 (Scaling, Failure Handling)"
            ],
            "completed": False
        })
        task_id += 1
        
        # 4. Behavioral / Review / Optional
        if total_minutes > (theory_mins + coding_mins + sd_mins):
            remaining = total_minutes - (theory_mins + coding_mins + sd_mins)
            if remaining >= 15:
                tasks.append({
                    "id": task_id,
                    "type": "review",
                    "icon": "📝",
                    "title": "今日回顾 & 笔记",
                    "description": "总结今天的知识点，记录到笔记中",
                    "duration_min": remaining,
                    "time_slot": "下午/晚上",
                    "priority": "medium",
                    "prompts": ["今天掌握的一个新公式/概念", "系统设计中的一个Trade-off"],
                    "completed": False
                })

        return {
            "date": date,
            "phase": "custom", # Simplified for now
            "phase_name": "🔥 全面提升",
            "focus": "ML基础 + 算法 + 系统设计",
            "days_left": days_left,
            "target_company": target_company,
            "total_minutes": total_minutes,
            "tasks": tasks,
            "motivation": self._get_daily_motivation(days_left, "intensive"),
            "generated_at": datetime.now().isoformat()
        }

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
        user_data = self._get_user_data(user_id)
        
        if not user_data:
            return False
        
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
                if task["type"] == "coding" and "questions" in task:
                    for q in task.get("questions", []):
                        if q["id"] not in user_data["progress"]["completed_questions"]:
                            user_data["progress"]["completed_questions"].append(q["id"])
                elif task["type"] == "system_design":
                    topic = task.get("topic", "")
                    if topic and topic not in user_data["progress"]["completed_topics"]:
                        user_data["progress"]["completed_topics"].append(topic)
                elif task["type"] == "theory":
                    # Also track theory topics
                    title = task.get("title", "")
                    if title and title not in user_data["progress"]["completed_topics"]:
                         user_data["progress"]["completed_topics"].append(title)
                
                self._save_user_data(user_id, user_data)
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
