"""
Supabase Database Client
Handles persistent storage for users, community Q&A, and other data
"""
import os
import streamlit as st
from typing import Dict, List, Optional
from datetime import datetime

# Try to import supabase, fall back to JSON if not available
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False


def get_supabase_client() -> Optional['Client']:
    """Get Supabase client, returns None if not configured."""
    if not SUPABASE_AVAILABLE:
        return None
    
    # Try to get credentials from Streamlit secrets first, then env vars
    try:
        url = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
        key = st.secrets.get("SUPABASE_KEY") or os.getenv("SUPABASE_KEY")
    except:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        return None
    
    try:
        return create_client(url, key)
    except Exception as e:
        print(f"Failed to create Supabase client: {e}")
        return None


class SupabaseUserStore:
    """User data storage using Supabase."""
    
    def __init__(self):
        self.client = get_supabase_client()
        self.table_name = "users"
    
    @property
    def is_available(self) -> bool:
        return self.client is not None
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID."""
        if not self.is_available:
            return None
        
        try:
            response = self.client.table(self.table_name).select("*").eq("user_id", user_id).execute()
            if response.data:
                return response.data[0]
        except Exception as e:
            print(f"Error fetching user: {e}")
        return None
    
    def create_user(self, user_data: Dict) -> bool:
        """Create a new user."""
        if not self.is_available:
            return False
        
        try:
            self.client.table(self.table_name).insert(user_data).execute()
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    def update_user(self, user_id: str, updates: Dict) -> bool:
        """Update user data."""
        if not self.is_available:
            return False
        
        try:
            updates["updated_at"] = datetime.now().isoformat()
            self.client.table(self.table_name).update(updates).eq("user_id", user_id).execute()
            return True
        except Exception as e:
            print(f"Error updating user: {e}")
            return False
    
    def get_leaderboard(self, limit: int = 20) -> List[Dict]:
        """Get top users by points."""
        if not self.is_available:
            return []
        
        try:
            response = self.client.table(self.table_name).select("*").order("points", desc=True).limit(limit).execute()
            return response.data or []
        except Exception as e:
            print(f"Error fetching leaderboard: {e}")
            return []
    
    def get_all_users(self) -> List[Dict]:
        """Get all users."""
        if not self.is_available:
            return []
        
        try:
            response = self.client.table(self.table_name).select("*").execute()
            return response.data or []
        except Exception as e:
            print(f"Error fetching users: {e}")
            return []


class SupabaseCommunityStore:
    """Community Q&A storage using Supabase."""
    
    def __init__(self):
        self.client = get_supabase_client()
        self.questions_table = "questions"
        self.answers_table = "answers"
    
    @property
    def is_available(self) -> bool:
        return self.client is not None
    
    def get_questions(self, limit: int = 50, category: str = None) -> List[Dict]:
        """Get questions with optional filtering."""
        if not self.is_available:
            return []
        
        try:
            query = self.client.table(self.questions_table).select("*").order("created_at", desc=True).limit(limit)
            if category:
                query = query.eq("category", category)
            response = query.execute()
            return response.data or []
        except Exception as e:
            print(f"Error fetching questions: {e}")
            return []
    
    def get_question(self, question_id: str) -> Optional[Dict]:
        """Get a single question by ID."""
        if not self.is_available:
            return None
        
        try:
            response = self.client.table(self.questions_table).select("*").eq("id", question_id).execute()
            if response.data:
                return response.data[0]
        except Exception as e:
            print(f"Error fetching question: {e}")
        return None
    
    def create_question(self, question_data: Dict) -> Optional[str]:
        """Create a new question."""
        if not self.is_available:
            return None
        
        try:
            response = self.client.table(self.questions_table).insert(question_data).execute()
            if response.data:
                return response.data[0].get("id")
        except Exception as e:
            print(f"Error creating question: {e}")
        return None
    
    def add_answer(self, answer_data: Dict) -> bool:
        """Add an answer to a question."""
        if not self.is_available:
            return False
        
        try:
            self.client.table(self.answers_table).insert(answer_data).execute()
            return True
        except Exception as e:
            print(f"Error adding answer: {e}")
            return False
    
    def get_answers(self, question_id: str) -> List[Dict]:
        """Get answers for a question."""
        if not self.is_available:
            return []
        
        try:
            response = self.client.table(self.answers_table).select("*").eq("question_id", question_id).order("upvotes", desc=True).execute()
            return response.data or []
        except Exception as e:
            print(f"Error fetching answers: {e}")
            return []


# Global instances
user_store = SupabaseUserStore()
community_store = SupabaseCommunityStore()


def is_supabase_configured() -> bool:
    """Check if Supabase is properly configured."""
    return user_store.is_available
