"""
User Question Notes
Per-user personal notes on interview questions.
Supports Supabase with local JSON fallback.
"""
import json
from datetime import datetime
from pathlib import Path

LOCAL_FILE = Path(__file__).parent / "user_question_notes.json"

try:
    from data.supabase_client import get_supabase_client, is_supabase_configured
    HAS_SUPABASE = True
except ImportError:
    HAS_SUPABASE = False


def _ensure_file():
    if not LOCAL_FILE.exists():
        LOCAL_FILE.write_text('{}', encoding='utf-8')


def _load():
    _ensure_file()
    try:
        return json.loads(LOCAL_FILE.read_text(encoding='utf-8'))
    except:
        return {}


def _save(data):
    LOCAL_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')


def get_note(user_id: str, question_id: str) -> str:
    """Get a user's note for a question."""
    if HAS_SUPABASE and is_supabase_configured():
        try:
            client = get_supabase_client()
            result = client.table("user_question_notes").select("note").eq(
                "user_id", user_id
            ).eq("question_id", question_id).execute()
            if result.data:
                return result.data[0].get("note", "")
        except:
            pass
    
    data = _load()
    return data.get(user_id, {}).get(question_id, {}).get("note", "")


def save_note(user_id: str, question_id: str, note: str):
    """Save a user's note for a question."""
    if HAS_SUPABASE and is_supabase_configured():
        try:
            client = get_supabase_client()
            # Upsert
            client.table("user_question_notes").upsert({
                "user_id": user_id,
                "question_id": question_id,
                "note": note,
                "updated_at": datetime.now().isoformat()
            }).execute()
            return
        except:
            pass
    
    data = _load()
    if user_id not in data:
        data[user_id] = {}
    data[user_id][question_id] = {
        "note": note,
        "updated_at": datetime.now().isoformat()
    }
    _save(data)


def get_all_notes(user_id: str) -> dict:
    """Get all notes for a user."""
    if HAS_SUPABASE and is_supabase_configured():
        try:
            client = get_supabase_client()
            result = client.table("user_question_notes").select("*").eq(
                "user_id", user_id
            ).execute()
            return {r["question_id"]: r["note"] for r in (result.data or [])}
        except:
            pass
    
    data = _load()
    return {k: v.get("note", "") for k, v in data.get(user_id, {}).items()}
