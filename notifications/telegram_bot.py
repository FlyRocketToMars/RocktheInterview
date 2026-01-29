"""
Telegram Bot Push Module
Sends daily study tasks via Telegram
"""
import os
import requests
import json
from pathlib import Path


def send_telegram_message(message: str) -> bool:
    """
    Send a message via Telegram Bot API.
    
    Args:
        message: The message to send (supports Markdown)
    
    Returns:
        True if successful, False otherwise
    """
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        print("Error: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set")
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        print("Telegram message sent successfully!")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Telegram message: {e}")
        return False


def load_daily_content() -> str:
    """Load the daily study content from generated file."""
    content_file = Path(__file__).parent / "daily_content.json"
    
    if content_file.exists():
        with open(content_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("message", "")
    
    # Default message if no content generated
    return """
🎯 *MLE Interview Prep - 每日提醒*

📚 今日学习任务:
• 复习一个核心ML概念
• 完成2道LeetCode题目
• 阅读一篇ML系统设计文章

💪 Keep going! 面试成功就在前方！
"""


def main():
    """Main entry point for Telegram push."""
    message = load_daily_content()
    
    # Add emoji header
    header = "🤖 *MLE Interview Prep*\n\n"
    full_message = header + message
    
    success = send_telegram_message(full_message)
    
    if not success:
        exit(1)


if __name__ == "__main__":
    main()
