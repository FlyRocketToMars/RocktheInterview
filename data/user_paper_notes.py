"""
User Paper Notes Module
Per-user note-taking on papers, stored in Supabase (with local JSON fallback).
"""
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    from data.supabase_client import get_supabase_client, is_supabase_configured
    HAS_SUPABASE = True
except ImportError:
    HAS_SUPABASE = False

LOCAL_NOTES_FILE = Path(__file__).parent / "user_paper_notes.json"

class UserPaperNotes:
    """Manage per-user notes on papers. Uses Supabase when available, JSON fallback."""
    
    def __init__(self):
        self.use_supabase = HAS_SUPABASE and is_supabase_configured()
        if self.use_supabase:
            self.client = get_supabase_client()
        self._ensure_local_file()
    
    def _ensure_local_file(self):
        if not LOCAL_NOTES_FILE.exists():
            LOCAL_NOTES_FILE.write_text('{}', encoding='utf-8')
    
    def _load_local(self) -> Dict:
        try:
            return json.loads(LOCAL_NOTES_FILE.read_text(encoding='utf-8'))
        except:
            return {}
    
    def _save_local(self, data: Dict):
        LOCAL_NOTES_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    
    def _get_note_key(self, user_id: str, paper_id: str) -> str:
        return f"{user_id}::{paper_id}"
    
    def save_note(self, user_id: str, paper_id: str, paper_title: str, content: str, 
                  note_type: str = "note", section: str = "全文"):
        """Save a user note for a paper."""
        note = {
            "user_id": user_id,
            "paper_id": paper_id,
            "paper_title": paper_title,
            "content": content,
            "note_type": note_type,  # note, summary, question, insight, key_takeaway
            "section": section,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        
        if self.use_supabase:
            try:
                self.client.table("user_paper_notes").upsert({
                    "id": hashlib.md5(f"{user_id}{paper_id}{content[:50]}".encode()).hexdigest()[:16],
                    **note
                }).execute()
                return True
            except Exception as e:
                print(f"Supabase save note failed: {e}")
                # Fallback to local
        
        # Local storage
        data = self._load_local()
        user_notes = data.get(user_id, {})
        paper_notes = user_notes.get(paper_id, {"paper_title": paper_title, "notes": []})
        paper_notes["notes"].append(note)
        paper_notes["paper_title"] = paper_title
        user_notes[paper_id] = paper_notes
        data[user_id] = user_notes
        self._save_local(data)
        return True
    
    def get_notes_for_paper(self, user_id: str, paper_id: str) -> List[Dict]:
        """Get all notes for a specific paper by a user."""
        if self.use_supabase:
            try:
                result = self.client.table("user_paper_notes").select("*").eq(
                    "user_id", user_id
                ).eq("paper_id", paper_id).order("created_at", desc=True).execute()
                return result.data or []
            except Exception as e:
                print(f"Supabase get notes failed: {e}")
        
        # Local fallback
        data = self._load_local()
        paper_data = data.get(user_id, {}).get(paper_id, {})
        return paper_data.get("notes", [])
    
    def get_all_user_notes(self, user_id: str) -> Dict[str, List[Dict]]:
        """Get all notes by a user, grouped by paper."""
        if self.use_supabase:
            try:
                result = self.client.table("user_paper_notes").select("*").eq(
                    "user_id", user_id
                ).order("updated_at", desc=True).execute()
                # Group by paper_id
                grouped = {}
                for note in (result.data or []):
                    pid = note.get("paper_id", "unknown")
                    if pid not in grouped:
                        grouped[pid] = {"paper_title": note.get("paper_title", ""), "notes": []}
                    grouped[pid]["notes"].append(note)
                return grouped
            except Exception as e:
                print(f"Supabase get all notes failed: {e}")
        
        # Local fallback
        data = self._load_local()
        return data.get(user_id, {})
    
    def delete_note(self, user_id: str, paper_id: str, note_index: int):
        """Delete a specific note."""
        if self.use_supabase:
            # Would need note ID for supabase delete
            pass
        
        data = self._load_local()
        paper_notes = data.get(user_id, {}).get(paper_id, {}).get("notes", [])
        if 0 <= note_index < len(paper_notes):
            paper_notes.pop(note_index)
            data[user_id][paper_id]["notes"] = paper_notes
            self._save_local(data)
    
    def get_note_stats(self, user_id: str) -> Dict:
        """Get statistics about a user's notes."""
        all_notes = self.get_all_user_notes(user_id)
        total_papers = len(all_notes)
        total_notes = sum(len(v.get("notes", [])) for v in all_notes.values())
        return {
            "total_papers": total_papers,
            "total_notes": total_notes,
        }


# Global instance
user_paper_notes = UserPaperNotes()
