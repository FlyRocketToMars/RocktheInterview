"""
Authentication Module
User authentication using Supabase
"""
import streamlit as st
from typing import Optional, Dict
import json
import hashlib
import os
from pathlib import Path
from datetime import datetime

# Try to import supabase, fall back to local auth if not available
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False


class LocalAuth:
    """
    Local file-based authentication for development/demo purposes.
    Stores users in a local JSON file.
    """
    
    def __init__(self):
        self.users_file = Path(__file__).parent.parent.parent / "data" / "users.json"
        self._ensure_users_file()
    
    def _ensure_users_file(self):
        """Create users file if it doesn't exist."""
        if not self.users_file.exists():
            self.users_file.write_text('{"users": {}}', encoding='utf-8')
    
    def _load_users(self) -> Dict:
        """Load users from file."""
        with open(self.users_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_users(self, data: Dict):
        """Save users to file."""
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def sign_up(self, email: str, password: str) -> tuple[bool, str]:
        """
        Register a new user.
        Returns (success, message).
        """
        data = self._load_users()
        
        if email in data["users"]:
            return False, "该邮箱已注册"
        
        data["users"][email] = {
            "email": email,
            "password_hash": self._hash_password(password),
            "created_at": datetime.now().isoformat(),
            "profile": {},
            "study_progress": {}
        }
        
        self._save_users(data)
        return True, "注册成功！"
    
    def sign_in(self, email: str, password: str) -> tuple[bool, str, Optional[Dict]]:
        """
        Sign in a user.
        Returns (success, message, user_data).
        """
        data = self._load_users()
        
        if email not in data["users"]:
            return False, "用户不存在", None
        
        user = data["users"][email]
        
        if user["password_hash"] != self._hash_password(password):
            return False, "密码错误", None
        
        return True, "登录成功！", user
    
    def save_user_data(self, email: str, key: str, value: any):
        """Save data for a user."""
        data = self._load_users()
        
        if email in data["users"]:
            data["users"][email][key] = value
            self._save_users(data)
    
    def get_user_data(self, email: str) -> Optional[Dict]:
        """Get user data."""
        data = self._load_users()
        return data["users"].get(email)


class SupabaseAuth:
    """
    Supabase-based authentication for production.
    """
    
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
        
        self.client: Client = create_client(url, key)
    
    def sign_up(self, email: str, password: str) -> tuple[bool, str]:
        """Register a new user."""
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password
            })
            
            if response.user:
                return True, "注册成功！请检查邮箱验证。"
            else:
                return False, "注册失败"
        except Exception as e:
            return False, f"注册失败: {str(e)}"
    
    def sign_in(self, email: str, password: str) -> tuple[bool, str, Optional[Dict]]:
        """Sign in a user."""
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                user_data = {
                    "email": email,
                    "id": response.user.id
                }
                return True, "登录成功！", user_data
            else:
                return False, "登录失败", None
        except Exception as e:
            return False, f"登录失败: {str(e)}", None
    
    def sign_out(self):
        """Sign out current user."""
        self.client.auth.sign_out()
    
    def save_user_data(self, user_id: str, key: str, value: any):
        """Save data to Supabase."""
        try:
            self.client.table("user_data").upsert({
                "user_id": user_id,
                "key": key,
                "value": json.dumps(value)
            }).execute()
        except Exception as e:
            st.error(f"保存数据失败: {e}")
    
    def get_user_data(self, user_id: str) -> Optional[Dict]:
        """Get user data from Supabase."""
        try:
            response = self.client.table("user_data").select("*").eq("user_id", user_id).execute()
            
            if response.data:
                result = {}
                for row in response.data:
                    result[row["key"]] = json.loads(row["value"])
                return result
            return None
        except Exception:
            return None


def get_auth_handler():
    """Get the appropriate auth handler based on environment."""
    if SUPABASE_AVAILABLE and os.getenv("SUPABASE_URL"):
        return SupabaseAuth()
    else:
        return LocalAuth()


def render_auth_page():
    """Render the authentication page."""
    
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="font-size: 3rem;">🔐 用户登录</h1>
        <p style="color: #94a3b8;">登录后可保存你的学习进度</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Auth mode tabs
    tab1, tab2 = st.tabs(["🔑 登录", "📝 注册"])
    
    auth = get_auth_handler()
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("📧 邮箱", placeholder="your@email.com")
            password = st.text_input("🔒 密码", type="password", placeholder="输入密码")
            
            submitted = st.form_submit_button("登录", use_container_width=True)
            
            if submitted:
                if email and password:
                    success, message, user_data = auth.sign_in(email, password)
                    
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.user_email = email
                        st.session_state.user_data = user_data
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("请填写邮箱和密码")
    
    with tab2:
        with st.form("register_form"):
            new_email = st.text_input("📧 邮箱", placeholder="your@email.com", key="reg_email")
            new_password = st.text_input("🔒 密码", type="password", placeholder="设置密码 (至少6位)", key="reg_pass")
            confirm_password = st.text_input("🔒 确认密码", type="password", placeholder="再次输入密码", key="reg_confirm")
            
            submitted = st.form_submit_button("注册", use_container_width=True)
            
            if submitted:
                if not new_email or not new_password:
                    st.error("请填写所有字段")
                elif len(new_password) < 6:
                    st.error("密码至少6位")
                elif new_password != confirm_password:
                    st.error("两次密码不一致")
                else:
                    success, message = auth.sign_up(new_email, new_password)
                    
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
    
    # Guest mode option
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: #64748b;'>或者</p>", unsafe_allow_html=True)
    
    if st.button("👤 以访客身份继续", use_container_width=True):
        st.session_state.authenticated = True
        st.session_state.user_email = "guest"
        st.session_state.is_guest = True
        st.rerun()


def check_authentication() -> bool:
    """Check if user is authenticated."""
    return st.session_state.get("authenticated", False)


def get_current_user() -> Optional[str]:
    """Get current user email."""
    return st.session_state.get("user_email")


def logout():
    """Log out current user."""
    for key in ["authenticated", "user_email", "user_data", "is_guest"]:
        if key in st.session_state:
            del st.session_state[key]


def save_user_progress(progress_data: Dict):
    """Save user's study progress."""
    email = get_current_user()
    
    if not email or email == "guest":
        return
    
    auth = get_auth_handler()
    auth.save_user_data(email, "study_progress", progress_data)


def load_user_progress() -> Optional[Dict]:
    """Load user's study progress."""
    email = get_current_user()
    
    if not email or email == "guest":
        return None
    
    auth = get_auth_handler()
    user_data = auth.get_user_data(email)
    
    if user_data:
        return user_data.get("study_progress")
    return None
