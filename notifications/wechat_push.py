"""
WeChat Push Module
Sends daily study tasks via WeChat Work (企业微信) or Official Account (公众号)
"""
import os
import requests
import json
from pathlib import Path
from datetime import datetime


class WeChatPusher:
    """WeChat Work (企业微信) message pusher."""
    
    def __init__(self):
        self.corp_id = os.getenv("WECHAT_CORP_ID")
        self.agent_id = os.getenv("WECHAT_AGENT_ID")
        self.secret = os.getenv("WECHAT_SECRET")
        self.access_token = None
    
    def get_access_token(self) -> str:
        """Get WeChat Work access token."""
        if not self.corp_id or not self.secret:
            raise ValueError("WECHAT_CORP_ID or WECHAT_SECRET not set")
        
        url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
        params = {
            "corpid": self.corp_id,
            "corpsecret": self.secret
        }
        
        response = requests.get(url, params=params, timeout=30)
        data = response.json()
        
        if data.get("errcode") == 0:
            self.access_token = data.get("access_token")
            return self.access_token
        else:
            raise ValueError(f"Failed to get token: {data.get('errmsg')}")
    
    def send_text_card(self, title: str, description: str, url: str = "", to_user: str = "@all") -> bool:
        """
        Send a text card message.
        
        Args:
            title: Card title
            description: Card description (supports limited HTML)
            url: URL to open when card is clicked
            to_user: Target users ("@all" for everyone)
        
        Returns:
            True if successful
        """
        if not self.access_token:
            self.get_access_token()
        
        api_url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={self.access_token}"
        
        payload = {
            "touser": to_user,
            "msgtype": "textcard",
            "agentid": self.agent_id,
            "textcard": {
                "title": title,
                "description": description,
                "url": url or "https://github.com",
                "btntxt": "查看详情"
            }
        }
        
        try:
            response = requests.post(api_url, json=payload, timeout=30)
            data = response.json()
            
            if data.get("errcode") == 0:
                print("WeChat message sent successfully!")
                return True
            else:
                print(f"WeChat send failed: {data.get('errmsg')}")
                return False
        except Exception as e:
            print(f"WeChat send error: {e}")
            return False
    
    def send_markdown(self, content: str, to_user: str = "@all") -> bool:
        """
        Send a markdown message (企业微信支持).
        
        Args:
            content: Markdown content
            to_user: Target users
        
        Returns:
            True if successful
        """
        if not self.access_token:
            self.get_access_token()
        
        api_url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={self.access_token}"
        
        payload = {
            "touser": to_user,
            "msgtype": "markdown",
            "agentid": self.agent_id,
            "markdown": {
                "content": content
            }
        }
        
        try:
            response = requests.post(api_url, json=payload, timeout=30)
            data = response.json()
            
            if data.get("errcode") == 0:
                print("WeChat markdown sent successfully!")
                return True
            else:
                print(f"WeChat send failed: {data.get('errmsg')}")
                return False
        except Exception as e:
            print(f"WeChat send error: {e}")
            return False


def load_daily_content() -> dict:
    """Load the daily study content from generated file."""
    content_file = Path(__file__).parent / "daily_content.json"
    
    if content_file.exists():
        with open(content_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    return {
        "tasks": [
            "复习一个核心ML概念",
            "完成2道LeetCode题目",
            "阅读一篇ML系统设计文章"
        ],
        "tips": "坚持每天进步一点点！"
    }


def generate_markdown_content(content: dict) -> str:
    """Generate markdown content for WeChat."""
    today = datetime.now().strftime("%Y年%m月%d日")
    
    tasks_md = "\n".join([f"> {task}" for task in content.get("tasks", [])])
    
    markdown = f"""# 🎯 MLE面试准备 - 每日提醒

**日期**: {today}

## 📚 今日任务

{tasks_md}

## 💡 小贴士

{content.get("tips", "保持节奏，稳步前进！")}

---
*Keep going! 面试成功就在前方！*
"""
    
    return markdown


def main():
    """Main entry point for WeChat push."""
    corp_id = os.getenv("WECHAT_CORP_ID")
    
    if not corp_id:
        print("WeChat not configured, skipping...")
        return
    
    content = load_daily_content()
    markdown = generate_markdown_content(content)
    
    pusher = WeChatPusher()
    
    try:
        success = pusher.send_markdown(markdown)
        if not success:
            # Fallback to text card
            today = datetime.now().strftime("%m月%d日")
            tasks_desc = "<div class='gray'>" + "</div><div class='gray'>".join(content.get("tasks", [])) + "</div>"
            
            success = pusher.send_text_card(
                title=f"🎯 MLE面试准备 - {today}",
                description=tasks_desc,
                url="https://github.com"
            )
        
        if not success:
            exit(1)
    except Exception as e:
        print(f"WeChat push failed: {e}")
        exit(1)


if __name__ == "__main__":
    main()
