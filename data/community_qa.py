"""
Community Q&A System
Users can ask questions, AI provides initial answers, community votes and contributes
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import hashlib
import requests
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


class Question:
    """Represents a community question."""
    
    def __init__(self, title: str, content: str, author: str, 
                 category: str = "general", tags: List[str] = None):
        self.id = self._generate_id(title, author)
        self.title = title
        self.content = content
        self.author = author
        self.category = category
        self.tags = tags or []
        self.created_at = datetime.now().isoformat()
        self.views = 0
        self.upvotes = 0
        self.downvotes = 0
        self.answers = []
        self.ai_answer = None
        self.status = "open"  # open, answered, closed
    
    def _generate_id(self, title: str, author: str) -> str:
        """Generate unique ID for question."""
        content = f"{title}{author}{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "author": self.author,
            "category": self.category,
            "tags": self.tags,
            "created_at": self.created_at,
            "views": self.views,
            "upvotes": self.upvotes,
            "downvotes": self.downvotes,
            "answers": self.answers,
            "ai_answer": self.ai_answer,
            "status": self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Question':
        q = cls(
            title=data.get("title", ""),
            content=data.get("content", ""),
            author=data.get("author", "Anonymous"),
            category=data.get("category", "general"),
            tags=data.get("tags", [])
        )
        q.id = data.get("id", q.id)
        q.created_at = data.get("created_at", q.created_at)
        q.views = data.get("views", 0)
        q.upvotes = data.get("upvotes", 0)
        q.downvotes = data.get("downvotes", 0)
        q.answers = data.get("answers", [])
        q.ai_answer = data.get("ai_answer")
        q.status = data.get("status", "open")
        return q


class Answer:
    """Represents an answer to a question."""
    
    def __init__(self, content: str, author: str, is_ai: bool = False):
        self.id = hashlib.md5(f"{content}{author}{datetime.now()}".encode()).hexdigest()[:12]
        self.content = content
        self.author = author
        self.is_ai = is_ai
        self.created_at = datetime.now().isoformat()
        self.upvotes = 0
        self.downvotes = 0
        self.is_accepted = False
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "content": self.content,
            "author": self.author,
            "is_ai": self.is_ai,
            "created_at": self.created_at,
            "upvotes": self.upvotes,
            "downvotes": self.downvotes,
            "is_accepted": self.is_accepted
        }


class CommunityQA:
    """Community Q&A system with AI assistance."""
    
    CATEGORIES = {
        "coding": "💻 编程题",
        "system_design": "🏗️ 系统设计",
        "ml_theory": "🧠 ML 理论",
        "behavioral": "💬 行为面试",
        "resume": "📄 简历相关",
        "career": "🚀 职业发展",
        "salary": "💰 薪资谈判",
        "general": "❓ 其他"
    }
    
    def __init__(self):
        self.data_file = Path(__file__).parent / "community_qa.json"
        self.api_key = os.getenv("GEMINI_API_KEY")
        self._ensure_data_file()
    
    def _ensure_data_file(self):
        """Ensure data file exists."""
        if not self.data_file.exists():
            self._save_data({"questions": [], "stats": {"total_questions": 0, "total_answers": 0}})
    
    def _load_data(self) -> Dict:
        """Load data from file."""
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"questions": [], "stats": {"total_questions": 0, "total_answers": 0}}
    
    def _save_data(self, data: Dict):
        """Save data to file."""
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_ai_answer(self, question: str, category: str) -> str:
        """Get AI-generated answer using Gemini."""
        if not self.api_key:
            return self._get_fallback_answer(category)
        
        category_context = {
            "coding": "你是一个资深算法工程师，请用清晰的思路解答这个编程问题，包含时间复杂度分析。",
            "system_design": "你是一个资深系统架构师，请从高层设计到具体实现详细解答这个系统设计问题。",
            "ml_theory": "你是一个 ML 专家，请用通俗易懂的方式解释这个 ML 概念，并给出实际应用例子。",
            "behavioral": "你是一个面试教练，请用 STAR 方法帮助回答这个行为面试问题。",
            "resume": "你是一个简历专家，请给出专业的简历优化建议。",
            "career": "你是一个职业发展顾问，请给出实用的职业建议。",
            "salary": "你是一个薪资谈判专家，请给出策略性的建议。",
            "general": "你是一个全面的面试专家，请尽可能详细地回答这个问题。"
        }
        
        context = category_context.get(category, category_context["general"])
        
        prompt = f"""{context}

问题: {question}

请提供一个详细、结构化的回答。如果是技术问题，请包含代码示例。
回答应该对面试准备有实际帮助。使用中文回答。"""

        try:
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.api_key}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.7, "maxOutputTokens": 2000}
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            print(f"AI answer error: {e}")
        
        return self._get_fallback_answer(category)
    
    def _get_fallback_answer(self, category: str) -> str:
        """Fallback answer when AI is unavailable."""
        fallbacks = {
            "coding": "这是一个很好的编程问题！建议从以下方面思考：\n1. 理解问题的输入输出\n2. 考虑边界情况\n3. 先写暴力解法\n4. 优化时间/空间复杂度\n\n等待社区成员提供更详细的解答。",
            "system_design": "系统设计问题可以从以下角度思考：\n1. 需求分析\n2. 高层架构\n3. 数据模型\n4. API 设计\n5. 扩展性考虑\n\n等待社区成员分享经验。",
            "ml_theory": "ML 理论问题建议参考：\n1. 相关论文\n2. 教科书定义\n3. 实际应用场景\n\n等待 ML 专家提供解答。",
            "default": "感谢你的问题！AI 助手暂时无法回答，等待社区成员来帮助你。"
        }
        return fallbacks.get(category, fallbacks["default"])
    
    def create_question(self, title: str, content: str, author: str,
                       category: str = "general", tags: List[str] = None,
                       get_ai_answer: bool = True) -> Question:
        """Create a new question."""
        question = Question(title, content, author, category, tags)
        
        # Get AI answer first
        if get_ai_answer:
            ai_response = self.get_ai_answer(f"{title}\n\n{content}", category)
            question.ai_answer = {
                "id": "ai_answer",
                "content": ai_response,
                "author": "🤖 AI 助手",
                "is_ai": True,
                "created_at": datetime.now().isoformat(),
                "upvotes": 0,
                "downvotes": 0,
                "is_accepted": False
            }
        
        # Save to database
        data = self._load_data()
        data["questions"].append(question.to_dict())
        data["stats"]["total_questions"] += 1
        self._save_data(data)
        
        return question
    
    def add_answer(self, question_id: str, content: str, author: str) -> Optional[Dict]:
        """Add a human answer to a question."""
        data = self._load_data()
        
        for q in data["questions"]:
            if q["id"] == question_id:
                answer = Answer(content, author)
                q["answers"].append(answer.to_dict())
                q["status"] = "answered"
                data["stats"]["total_answers"] += 1
                self._save_data(data)
                return answer.to_dict()
        
        return None
    
    def vote(self, question_id: str, answer_id: str = None, is_upvote: bool = True) -> bool:
        """Vote on a question or answer."""
        data = self._load_data()
        
        for q in data["questions"]:
            if q["id"] == question_id:
                if answer_id is None:
                    # Vote on question
                    if is_upvote:
                        q["upvotes"] += 1
                    else:
                        q["downvotes"] += 1
                else:
                    # Vote on answer
                    if answer_id == "ai_answer" and q.get("ai_answer"):
                        if is_upvote:
                            q["ai_answer"]["upvotes"] += 1
                        else:
                            q["ai_answer"]["downvotes"] += 1
                    else:
                        for a in q["answers"]:
                            if a["id"] == answer_id:
                                if is_upvote:
                                    a["upvotes"] += 1
                                else:
                                    a["downvotes"] += 1
                                break
                
                self._save_data(data)
                return True
        
        return False
    
    def get_questions(self, category: str = None, sort_by: str = "newest",
                     limit: int = 20) -> List[Dict]:
        """Get questions with filtering and sorting."""
        data = self._load_data()
        questions = data.get("questions", [])
        
        # Filter by category
        if category and category != "all":
            questions = [q for q in questions if q.get("category") == category]
        
        # Sort
        if sort_by == "newest":
            questions = sorted(questions, key=lambda x: x.get("created_at", ""), reverse=True)
        elif sort_by == "popular":
            questions = sorted(questions, key=lambda x: x.get("upvotes", 0), reverse=True)
        elif sort_by == "unanswered":
            questions = [q for q in questions if not q.get("answers") and q.get("status") == "open"]
        
        return questions[:limit]
    
    def get_question(self, question_id: str) -> Optional[Dict]:
        """Get a single question by ID."""
        data = self._load_data()
        
        for q in data["questions"]:
            if q["id"] == question_id:
                q["views"] += 1
                self._save_data(data)
                return q
        
        return None
    
    def get_stats(self) -> Dict:
        """Get community statistics."""
        data = self._load_data()
        questions = data.get("questions", [])
        
        return {
            "total_questions": len(questions),
            "total_answers": sum(len(q.get("answers", [])) for q in questions),
            "answered_questions": len([q for q in questions if q.get("answers")]),
            "categories": {cat: len([q for q in questions if q.get("category") == cat]) 
                          for cat in self.CATEGORIES.keys()}
        }
    
    def search(self, query: str) -> List[Dict]:
        """Search questions by keyword."""
        data = self._load_data()
        questions = data.get("questions", [])
        query = query.lower()
        
        results = []
        for q in questions:
            if (query in q.get("title", "").lower() or 
                query in q.get("content", "").lower() or
                any(query in tag.lower() for tag in q.get("tags", []))):
                results.append(q)
        
        return results


# Global instance
community_qa = CommunityQA()


# Helper functions
def ask_question(title: str, content: str, author: str, category: str = "general", 
                tags: List[str] = None) -> Question:
    """Create a new question."""
    return community_qa.create_question(title, content, author, category, tags)


def answer_question(question_id: str, content: str, author: str) -> Optional[Dict]:
    """Answer a question."""
    return community_qa.add_answer(question_id, content, author)


def get_questions(category: str = None, sort_by: str = "newest") -> List[Dict]:
    """Get questions."""
    return community_qa.get_questions(category, sort_by)


def vote_question(question_id: str, is_upvote: bool = True) -> bool:
    """Vote on a question."""
    return community_qa.vote(question_id, is_upvote=is_upvote)


def vote_answer(question_id: str, answer_id: str, is_upvote: bool = True) -> bool:
    """Vote on an answer."""
    return community_qa.vote(question_id, answer_id, is_upvote)
