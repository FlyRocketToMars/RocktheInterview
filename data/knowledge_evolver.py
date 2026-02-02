import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import random

class KnowledgeEvolver:
    """
    Core engine that evolves the question bank by extracting knowledge 
    from new papers, blogs, and technical resources.
    """
    
    def __init__(self):
        self.data_dir = Path(__file__).parent
        self.bank_file = self.data_dir / "dynamic_question_bank.json"
        self._ensure_bank_file()
        
    def _ensure_bank_file(self):
        if not self.bank_file.exists():
            default_data = {
                "last_updated": datetime.now().isoformat(),
                "sources_processed": [],
                "questions": {"theory": [], "system_design": [], "coding": []}
            }
            self._save_bank(default_data)
            
    def _load_bank(self) -> Dict:
        try:
            with open(self.bank_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"questions": {"theory": [], "system_design": []}}
            
    def _save_bank(self, data: Dict):
        with open(self.bank_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def process_content_source(self, source_type: str, item: Dict) -> List[Dict]:
        """
        Process a new content source (paper/blog) and generate questions.
        Returns list of generated questions.
        """
        data = self._load_bank()
        source_id = item.get('url') or item.get('title')
        
        # Avoid duplicate processing
        if source_id in data.get("sources_processed", []):
            return []
            
        generated_questions = []
        
        # 1. Analyze content and extract topics (Simulated NLP)
        title = item.get('title', '')
        abstract = item.get('abstract', '') or item.get('summary', '')
        
        # 2. Generate Theory Questions based on keywords
        if "LLM" in title or "Transformer" in title or "Language Model" in title:
            q = self._generate_llm_question(title, abstract)
            if q: generated_questions.append(q)
            
        elif "Recommendation" in title or "Ranking" in title:
            q = self._generate_sys_design_question(title, abstract)
            if q: generated_questions.append(q)
            
        elif "Diffusion" in title or "Generative" in title:
            q = self._generate_diffusion_question(title, abstract)
            if q: generated_questions.append(q)
            
        # 3. Save to bank
        if generated_questions:
            for q in generated_questions:
                category = q.get("type", "theory")
                if category in data["questions"]:
                    # Check duplicates
                    if not any(ex["title"] == q["title"] for ex in data["questions"][category]):
                        data["questions"][category].append(q)
            
            data["sources_processed"].append(source_id)
            data["last_updated"] = datetime.now().isoformat()
            self._save_bank(data)
            
        return generated_questions

    def _generate_llm_question(self, title: str, abstract: str) -> Dict:
        """Generate an LLM theory question from content."""
        # Heuristic rules to formulate questions
        if "LoRA" in title or "Efficient" in title:
            return {
                "id": f"dyn_llm_{int(datetime.now().timestamp())}",
                "type": "theory",
                "topic": "LLM Efficiency",
                "title": f"解析 {title} 中的参数高效微调技术",
                "description": f"基于新论文 '{title}'，解释其核心创新点以及通过何种方式降低了显存/计算开销。",
                "source": title,
                "is_new": True,
                "added_at": datetime.now().isoformat()
            }
        else:
            return {
                "id": f"dyn_llm_{int(datetime.now().timestamp())}",
                "type": "theory",
                "topic": "LLM Architecture",
                "title": f"结合 {title} 谈谈 LLM 的架构演进",
                "description": f"阅读 '{title}' 的摘要，总结该工作解决了之前架构的哪些痛点 (如 Context Length, Hallucination 等)。",
                "source": title,
                "is_new": True,
                "added_at": datetime.now().isoformat()
            }

    def _generate_sys_design_question(self, title: str, abstract: str) -> Dict:
        """Generate a system design question."""
        return {
            "id": f"dyn_sd_{int(datetime.now().timestamp())}",
            "type": "system_design",
            "topic": "Recommender System",
            "title": f"设计一个基于 {title} 的推荐系统",
            "description": f"新论文 '{title}' 提出了新的排序/检索思路。请设计一个能够应用该技术的大规模推荐系统，重点关注在线 Serving 的延迟挑战。",
            "source": title,
            "is_new": True,
            "added_at": datetime.now().isoformat()
        }

    def _generate_diffusion_question(self, title: str, abstract: str) -> Dict:
        return {
            "id": f"dyn_diff_{int(datetime.now().timestamp())}",
            "type": "theory",
            "topic": "Generative Models",
            "title": f"解析 {title} 中的生成模型原理",
            "description": f"基于 '{title}'，对比该方法与传统 GAN 或 Latent Diffusion 的差异。",
            "source": title,
            "is_new": True,
            "added_at": datetime.now().isoformat()
        }
    
    def get_latest_questions(self, limit: int = 5) -> List[Dict]:
        """Get the most recently added dynamic questions."""
        data = self._load_bank()
        all_q = []
        for cat in data["questions"]:
            all_q.extend(data["questions"][cat])
        
        # Sort by date desc
        all_q.sort(key=lambda x: x.get("added_at", ""), reverse=True)
        return all_q[:limit]

# Global instance
knowledge_evolver = KnowledgeEvolver()
