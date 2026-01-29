"""
Email Sender Module
Sends daily study tasks via Email (SMTP)
"""
import os
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from datetime import datetime


def send_email(subject: str, body_html: str) -> bool:
    """
    Send an email via SMTP.
    
    Args:
        subject: Email subject
        body_html: Email body in HTML format
    
    Returns:
        True if successful, False otherwise
    """
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    to_email = os.getenv("NOTIFY_EMAIL")
    
    if not smtp_user or not smtp_password or not to_email:
        print("Error: Email configuration incomplete")
        return False
    
    # Create message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_email
    
    # HTML body
    html_part = MIMEText(body_html, "html", "utf-8")
    msg.attach(html_part)
    
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, to_email, msg.as_string())
        print("Email sent successfully!")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
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


def generate_html_email(content: dict) -> str:
    """Generate a beautiful HTML email."""
    today = datetime.now().strftime("%Y年%m月%d日")
    
    tasks_html = "".join([
        f'<li style="margin: 10px 0; padding: 10px; background: #f0f9ff; border-radius: 8px; border-left: 4px solid #6366f1;">{task}</li>'
        for task in content.get("tasks", [])
    ])
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
    </head>
    <body style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #f8fafc;">
        <div style="background: linear-gradient(135deg, #6366f1, #22d3ee); padding: 30px; border-radius: 16px 16px 0 0; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 24px;">🎯 MLE Interview Prep</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0;">每日学习提醒 - {today}</p>
        </div>
        
        <div style="background: white; padding: 30px; border-radius: 0 0 16px 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
            <h2 style="color: #1e293b; margin-top: 0;">📚 今日任务</h2>
            <ul style="list-style: none; padding: 0;">
                {tasks_html}
            </ul>
            
            <div style="background: #fef3c7; padding: 15px; border-radius: 12px; margin-top: 20px;">
                <p style="margin: 0; color: #92400e;">
                    💡 <strong>小贴士:</strong> {content.get("tips", "保持节奏，稳步前进！")}
                </p>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <a href="#" style="display: inline-block; background: linear-gradient(90deg, #6366f1, #4f46e5); color: white; padding: 12px 30px; border-radius: 8px; text-decoration: none; font-weight: 600;">
                    开始学习 →
                </a>
            </div>
        </div>
        
        <p style="text-align: center; color: #94a3b8; font-size: 12px; margin-top: 20px;">
            MLE Interview Prep Platform | Made with ❤️
        </p>
    </body>
    </html>
    """
    
    return html


def main():
    """Main entry point for email push."""
    content = load_daily_content()
    
    today = datetime.now().strftime("%m/%d")
    subject = f"🎯 MLE面试准备 - {today} 每日任务"
    
    body_html = generate_html_email(content)
    
    success = send_email(subject, body_html)
    
    if not success:
        exit(1)


if __name__ == "__main__":
    main()
