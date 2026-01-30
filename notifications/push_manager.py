"""
Push Manager Module
Unified entry point for sending notifications across all channels
"""
import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from .telegram_bot import send_telegram_message
from .email_sender import send_email, generate_html_email
from .wechat_push import WeChatPusher, generate_markdown_content
from .user_preferences import get_preferences, UserPreferences


class NotificationManager:
    """
    Unified notification manager for sending messages across all channels.
    """
    
    def __init__(self):
        self.prefs = get_preferences()
        self._wechat_pusher: Optional[WeChatPusher] = None
    
    @property
    def wechat_pusher(self) -> Optional[WeChatPusher]:
        """Lazy-load WeChat pusher."""
        if self._wechat_pusher is None and os.getenv("WECHAT_CORP_ID"):
            self._wechat_pusher = WeChatPusher()
        return self._wechat_pusher
    
    def send_telegram(self, message: str, chat_id: str = None) -> Tuple[bool, str]:
        """
        Send a Telegram message.
        
        Args:
            message: Markdown-formatted message
            chat_id: Optional override for chat ID (uses env var if not provided)
        
        Returns:
            Tuple of (success, error_message)
        """
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        target_chat = chat_id or os.getenv("TELEGRAM_CHAT_ID")
        
        if not bot_token:
            return False, "TELEGRAM_BOT_TOKEN not configured"
        if not target_chat:
            return False, "No chat ID provided"
        
        try:
            # Temporarily override chat ID if custom one provided
            original_chat_id = os.environ.get("TELEGRAM_CHAT_ID")
            if chat_id:
                os.environ["TELEGRAM_CHAT_ID"] = chat_id
            
            success = send_telegram_message(message)
            
            # Restore original
            if original_chat_id:
                os.environ["TELEGRAM_CHAT_ID"] = original_chat_id
            
            return success, "" if success else "Send failed"
        except Exception as e:
            return False, str(e)
    
    def send_email_notification(self, subject: str, content: Dict, to_email: str = None) -> Tuple[bool, str]:
        """
        Send an email notification.
        
        Args:
            subject: Email subject
            content: Dict with "tasks" and "tips" keys
            to_email: Optional override for recipient email
        
        Returns:
            Tuple of (success, error_message)
        """
        if not os.getenv("SMTP_USER"):
            return False, "SMTP not configured"
        
        try:
            # Generate HTML
            html_body = generate_html_email(content)
            
            # Temporarily override email if custom one provided
            original_email = os.environ.get("NOTIFY_EMAIL")
            if to_email:
                os.environ["NOTIFY_EMAIL"] = to_email
            
            success = send_email(subject, html_body)
            
            # Restore original
            if original_email:
                os.environ["NOTIFY_EMAIL"] = original_email
            
            return success, "" if success else "Send failed"
        except Exception as e:
            return False, str(e)
    
    def send_wechat(self, content: Dict, user_id: str = "@all") -> Tuple[bool, str]:
        """
        Send a WeChat Work message.
        
        Args:
            content: Dict with "tasks" and "tips" keys
            user_id: WeChat user ID or "@all"
        
        Returns:
            Tuple of (success, error_message)
        """
        if not self.wechat_pusher:
            return False, "WeChat not configured"
        
        try:
            markdown = generate_markdown_content(content)
            success = self.wechat_pusher.send_markdown(markdown, to_user=user_id)
            return success, "" if success else "Send failed"
        except Exception as e:
            return False, str(e)
    
    def send_to_user(self, email: str, content: Dict, channels: List[str] = None) -> Dict[str, Tuple[bool, str]]:
        """
        Send notification to a user through their enabled channels.
        
        Args:
            email: User's email address
            content: Notification content dict
            channels: Optional list of channels to use (overrides user prefs)
        
        Returns:
            Dict mapping channel -> (success, error_message)
        """
        prefs = self.prefs.get_user_prefs(email)
        target_channels = channels or self.prefs.get_enabled_channels(email)
        
        results = {}
        today = datetime.now().strftime("%m/%d")
        
        # Prepare message content
        telegram_msg = self._format_telegram_message(content)
        email_subject = f"🎯 面试准备 - {today} 每日任务"
        
        for channel in target_channels:
            channel_settings = prefs.get("channels", {}).get(channel, {})
            
            if channel == "telegram":
                chat_id = channel_settings.get("chat_id") or os.getenv("TELEGRAM_CHAT_ID")
                success, error = self.send_telegram(telegram_msg, chat_id)
            
            elif channel == "email":
                to_email = channel_settings.get("address") or email
                success, error = self.send_email_notification(email_subject, content, to_email)
            
            elif channel == "wechat":
                user_id = channel_settings.get("user_id") or "@all"
                success, error = self.send_wechat(content, user_id)
            
            else:
                success, error = False, f"Unknown channel: {channel}"
            
            results[channel] = (success, error)
            
            # Log the notification
            status = "success" if success else "failed"
            self.prefs.log_notification(email, channel, status, error)
        
        return results
    
    def send_test_notification(self, email: str, channel: str) -> Tuple[bool, str]:
        """
        Send a test notification to verify configuration.
        
        Args:
            email: User's email
            channel: Channel to test
        
        Returns:
            Tuple of (success, error_message)
        """
        test_content = {
            "tasks": [
                "✅ 这是一条测试消息",
                "📱 通知配置成功！",
                "🎯 开始你的面试准备之旅"
            ],
            "tips": "恭喜！你的通知设置已完成配置。"
        }
        
        results = self.send_to_user(email, test_content, channels=[channel])
        return results.get(channel, (False, "Channel not found"))
    
    def broadcast_daily_notifications(self, content: Dict) -> Dict[str, Dict]:
        """
        Send daily notifications to all subscribed users.
        
        Args:
            content: Daily notification content
        
        Returns:
            Dict mapping email -> channel results
        """
        subscribers = self.prefs.get_all_subscribed_users()
        all_results = {}
        
        for user in subscribers:
            email = user["email"]
            results = self.send_to_user(email, content, user["channels"])
            all_results[email] = results
        
        return all_results
    
    def _format_telegram_message(self, content: Dict) -> str:
        """Format content for Telegram (Markdown)."""
        today = datetime.now().strftime("%Y年%m月%d日")
        
        lines = [
            f"🎯 *MLE面试准备 - 每日提醒*",
            f"📅 {today}",
            "",
            "📚 *今日任务:*"
        ]
        
        for i, task in enumerate(content.get("tasks", []), 1):
            lines.append(f"  {i}. {task}")
        
        lines.append("")
        lines.append(f"💡 *小贴士:* {content.get('tips', '加油！')}")
        
        return "\n".join(lines)
    
    def get_channel_status(self) -> Dict[str, bool]:
        """Get configuration status for all channels."""
        return {
            "telegram": bool(os.getenv("TELEGRAM_BOT_TOKEN")),
            "email": bool(os.getenv("SMTP_USER") and os.getenv("SMTP_PASSWORD")),
            "wechat": bool(os.getenv("WECHAT_CORP_ID"))
        }


# Convenience function
def get_notification_manager() -> NotificationManager:
    """Get a NotificationManager instance."""
    return NotificationManager()
