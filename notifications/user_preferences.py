"""
User Notification Preferences Module
Manages user push notification settings and preferences
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any


class UserPreferences:
    """Manages user notification preferences stored in JSON file."""
    
    def __init__(self):
        self.prefs_file = Path(__file__).parent.parent / "data" / "user_preferences.json"
        self.logs_file = Path(__file__).parent.parent / "data" / "notification_logs.json"
        self._ensure_files()
    
    def _ensure_files(self):
        """Create preference and log files if they don't exist."""
        if not self.prefs_file.exists():
            self.prefs_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.prefs_file, "w", encoding="utf-8") as f:
                json.dump({"users": {}}, f, ensure_ascii=False, indent=2)
        
        if not self.logs_file.exists():
            with open(self.logs_file, "w", encoding="utf-8") as f:
                json.dump({"logs": []}, f, ensure_ascii=False, indent=2)
    
    def _load_prefs(self) -> Dict:
        """Load preferences from file."""
        with open(self.prefs_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _save_prefs(self, data: Dict):
        """Save preferences to file."""
        with open(self.prefs_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_user_prefs(self, email: str) -> Dict:
        """
        Get notification preferences for a user.
        
        Returns default preferences if user not found.
        """
        data = self._load_prefs()
        
        default_prefs = {
            "email": email,
            "channels": {
                "telegram": {"enabled": False, "chat_id": ""},
                "email": {"enabled": True, "address": email},
                "wechat": {"enabled": False, "user_id": ""}
            },
            "schedule": {
                "enabled": True,
                "time": "08:00",  # 每天推送时间
                "timezone": "Asia/Shanghai",
                "frequency": "daily"  # daily, weekdays, custom
            },
            "content": {
                "include_coding": True,
                "include_ml_theory": True,
                "include_system_design": True,
                "include_behavioral": True,
                "task_count": 3,  # 每日任务数量
                "priority_gaps": True  # 优先推送 Gap 技能
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        return data.get("users", {}).get(email, default_prefs)
    
    def save_user_prefs(self, email: str, prefs: Dict) -> bool:
        """Save notification preferences for a user."""
        try:
            data = self._load_prefs()
            if "users" not in data:
                data["users"] = {}
            
            prefs["updated_at"] = datetime.now().isoformat()
            data["users"][email] = prefs
            self._save_prefs(data)
            return True
        except Exception as e:
            print(f"Error saving preferences: {e}")
            return False
    
    def update_channel(self, email: str, channel: str, enabled: bool, **kwargs) -> bool:
        """Update a specific channel's settings."""
        prefs = self.get_user_prefs(email)
        
        if channel not in prefs["channels"]:
            return False
        
        prefs["channels"][channel]["enabled"] = enabled
        prefs["channels"][channel].update(kwargs)
        
        return self.save_user_prefs(email, prefs)
    
    def get_enabled_channels(self, email: str) -> List[str]:
        """Get list of enabled notification channels for a user."""
        prefs = self.get_user_prefs(email)
        return [
            channel for channel, settings in prefs.get("channels", {}).items()
            if settings.get("enabled", False)
        ]
    
    def get_all_subscribed_users(self) -> List[Dict]:
        """Get all users with notifications enabled."""
        data = self._load_prefs()
        subscribed = []
        
        for email, prefs in data.get("users", {}).items():
            if prefs.get("schedule", {}).get("enabled", False):
                enabled_channels = self.get_enabled_channels(email)
                if enabled_channels:
                    subscribed.append({
                        "email": email,
                        "channels": enabled_channels,
                        "prefs": prefs
                    })
        
        return subscribed
    
    # =========== Notification Logs ===========
    
    def log_notification(self, email: str, channel: str, status: str, message: str = ""):
        """Log a notification send attempt."""
        try:
            with open(self.logs_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            log_entry = {
                "email": email,
                "channel": channel,
                "status": status,  # "success", "failed", "skipped"
                "message": message,
                "timestamp": datetime.now().isoformat()
            }
            
            data["logs"].append(log_entry)
            
            # Keep only last 500 logs
            if len(data["logs"]) > 500:
                data["logs"] = data["logs"][-500:]
            
            with open(self.logs_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error logging notification: {e}")
    
    def get_user_logs(self, email: str, limit: int = 20) -> List[Dict]:
        """Get notification logs for a specific user."""
        try:
            with open(self.logs_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            user_logs = [log for log in data.get("logs", []) if log.get("email") == email]
            return user_logs[-limit:][::-1]  # Most recent first
        except Exception:
            return []
    
    def get_recent_logs(self, limit: int = 50) -> List[Dict]:
        """Get recent notification logs for all users."""
        try:
            with open(self.logs_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            return data.get("logs", [])[-limit:][::-1]
        except Exception:
            return []


# Convenience functions
_prefs_instance: Optional[UserPreferences] = None

def get_preferences() -> UserPreferences:
    """Get singleton instance of UserPreferences."""
    global _prefs_instance
    if _prefs_instance is None:
        _prefs_instance = UserPreferences()
    return _prefs_instance
