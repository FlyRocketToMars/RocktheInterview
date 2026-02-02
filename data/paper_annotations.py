"""
Paper Annotations Module
Collaborative paper discussion and annotation system
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import hashlib


class PaperAnnotations:
    """Manages collaborative paper annotations and discussions."""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent
        self.data_file = self.data_dir / "paper_annotations.json"
        self._ensure_data_file()
    
    def _ensure_data_file(self):
        """Create data file if it doesn't exist."""
        if not self.data_file.exists():
            self._save_data({
                "papers": {},
                "stats": {
                    "total_annotations": 0,
                    "total_discussions": 0,
                    "active_users": []
                }
            })
    
    def _load_data(self) -> Dict:
        """Load annotations data."""
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"papers": {}, "stats": {}}
    
    def _save_data(self, data: Dict):
        """Save annotations data."""
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Save error: {e}")
    
    def _get_paper_id(self, paper_url: str) -> str:
        """Generate a unique ID for a paper from its URL."""
        return hashlib.md5(paper_url.encode()).hexdigest()[:12]
    
    def add_paper(self, paper_info: Dict) -> str:
        """Add a paper to the annotation system."""
        data = self._load_data()
        
        paper_id = self._get_paper_id(paper_info.get("url", ""))
        
        if paper_id not in data["papers"]:
            data["papers"][paper_id] = {
                "id": paper_id,
                "title": paper_info.get("title", ""),
                "url": paper_info.get("url", ""),
                "abstract": paper_info.get("abstract", ""),
                "authors": paper_info.get("authors", []),
                "source": paper_info.get("source", ""),
                "added_at": datetime.now().isoformat(),
                "added_by": paper_info.get("added_by", "anonymous"),
                "annotations": [],
                "discussions": [],
                "tags": paper_info.get("tags", []),
                "reading_status": {},  # user_id: status
                "key_takeaways": [],
                "difficulty": paper_info.get("difficulty", "medium"),
                "relevance_score": 0,
                "upvotes": 0
            }
            self._save_data(data)
        
        return paper_id
    
    def add_annotation(self, paper_id: str, user_id: str, annotation: Dict) -> bool:
        """Add an annotation to a paper."""
        data = self._load_data()
        
        if paper_id not in data["papers"]:
            return False
        
        new_annotation = {
            "id": f"ann_{datetime.now().timestamp()}",
            "user_id": user_id,
            "type": annotation.get("type", "note"),  # note, highlight, question, insight
            "content": annotation.get("content", ""),
            "section": annotation.get("section", ""),  # abstract, method, results, etc.
            "created_at": datetime.now().isoformat(),
            "upvotes": 0,
            "upvoted_by": [],
            "replies": []
        }
        
        data["papers"][paper_id]["annotations"].append(new_annotation)
        data["stats"]["total_annotations"] = data["stats"].get("total_annotations", 0) + 1
        
        # Track active users
        if user_id not in data["stats"].get("active_users", []):
            data["stats"]["active_users"] = data["stats"].get("active_users", []) + [user_id]
        
        self._save_data(data)
        return True
    
    def add_discussion(self, paper_id: str, user_id: str, content: str, 
                       parent_id: Optional[str] = None) -> bool:
        """Add a discussion comment on a paper."""
        data = self._load_data()
        
        if paper_id not in data["papers"]:
            return False
        
        new_comment = {
            "id": f"disc_{datetime.now().timestamp()}",
            "user_id": user_id,
            "content": content,
            "created_at": datetime.now().isoformat(),
            "parent_id": parent_id,
            "upvotes": 0,
            "upvoted_by": [],
            "replies": []
        }
        
        if parent_id:
            # Add as reply to existing comment
            for disc in data["papers"][paper_id]["discussions"]:
                if disc["id"] == parent_id:
                    disc["replies"].append(new_comment)
                    break
        else:
            # Add as top-level comment
            data["papers"][paper_id]["discussions"].append(new_comment)
        
        data["stats"]["total_discussions"] = data["stats"].get("total_discussions", 0) + 1
        self._save_data(data)
        return True
    
    def add_key_takeaway(self, paper_id: str, user_id: str, takeaway: str) -> bool:
        """Add a key takeaway to a paper."""
        data = self._load_data()
        
        if paper_id not in data["papers"]:
            return False
        
        new_takeaway = {
            "id": f"take_{datetime.now().timestamp()}",
            "user_id": user_id,
            "content": takeaway,
            "created_at": datetime.now().isoformat(),
            "upvotes": 0
        }
        
        data["papers"][paper_id]["key_takeaways"].append(new_takeaway)
        self._save_data(data)
        return True
    
    def update_reading_status(self, paper_id: str, user_id: str, status: str) -> bool:
        """Update a user's reading status for a paper."""
        data = self._load_data()
        
        if paper_id not in data["papers"]:
            return False
        
        # status: "want_to_read", "reading", "finished", "reviewed"
        data["papers"][paper_id]["reading_status"][user_id] = {
            "status": status,
            "updated_at": datetime.now().isoformat()
        }
        
        self._save_data(data)
        return True
    
    def upvote_paper(self, paper_id: str, user_id: str) -> bool:
        """Upvote a paper."""
        data = self._load_data()
        
        if paper_id not in data["papers"]:
            return False
        
        data["papers"][paper_id]["upvotes"] = data["papers"][paper_id].get("upvotes", 0) + 1
        self._save_data(data)
        return True
    
    def upvote_annotation(self, paper_id: str, annotation_id: str, user_id: str) -> bool:
        """Upvote an annotation."""
        data = self._load_data()
        
        if paper_id not in data["papers"]:
            return False
        
        for ann in data["papers"][paper_id]["annotations"]:
            if ann["id"] == annotation_id:
                if user_id not in ann.get("upvoted_by", []):
                    ann["upvotes"] = ann.get("upvotes", 0) + 1
                    ann["upvoted_by"] = ann.get("upvoted_by", []) + [user_id]
                    self._save_data(data)
                    return True
        
        return False
    
    def get_paper(self, paper_id: str) -> Optional[Dict]:
        """Get a paper with all its annotations."""
        data = self._load_data()
        return data["papers"].get(paper_id)
    
    def get_all_papers(self) -> List[Dict]:
        """Get all papers."""
        data = self._load_data()
        papers = list(data["papers"].values())
        # Sort by upvotes and recent activity
        return sorted(papers, key=lambda x: (x.get("upvotes", 0), x.get("added_at", "")), reverse=True)
    
    def get_trending_papers(self, limit: int = 10) -> List[Dict]:
        """Get trending papers based on recent activity."""
        papers = self.get_all_papers()
        # Simple trending: most annotations + discussions in last 7 days
        return papers[:limit]
    
    def get_user_reading_list(self, user_id: str) -> Dict:
        """Get a user's reading list organized by status."""
        data = self._load_data()
        
        reading_list = {
            "want_to_read": [],
            "reading": [],
            "finished": [],
            "reviewed": []
        }
        
        for paper in data["papers"].values():
            if user_id in paper.get("reading_status", {}):
                status = paper["reading_status"][user_id].get("status", "want_to_read")
                if status in reading_list:
                    reading_list[status].append(paper)
        
        return reading_list
    
    def search_papers(self, query: str) -> List[Dict]:
        """Search papers by title or content."""
        data = self._load_data()
        query = query.lower()
        
        results = []
        for paper in data["papers"].values():
            if (query in paper.get("title", "").lower() or 
                query in paper.get("abstract", "").lower() or
                any(query in tag.lower() for tag in paper.get("tags", []))):
                results.append(paper)
        
        return results
    
    def get_stats(self) -> Dict:
        """Get annotation system statistics."""
        data = self._load_data()
        
        return {
            "total_papers": len(data["papers"]),
            "total_annotations": data["stats"].get("total_annotations", 0),
            "total_discussions": data["stats"].get("total_discussions", 0),
            "active_users": len(data["stats"].get("active_users", []))
        }


# Global instance
paper_annotations = PaperAnnotations()
