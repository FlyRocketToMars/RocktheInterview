"""
Notification Settings Component
Frontend UI for managing push notification preferences
"""
import streamlit as st
from pathlib import Path
import sys

# Add notifications module to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from notifications.user_preferences import get_preferences
from notifications.push_manager import get_notification_manager


def render_notification_settings():
    """Render the notification settings page."""
    st.markdown("## 🔔 通知设置")
    st.markdown("配置你的每日学习任务推送方式")
    
    # Get current user
    from .auth import get_current_user
    user_email = get_current_user()
    
    if not user_email or st.session_state.get("is_guest", False):
        st.warning("请先登录以配置通知设置")
        return
    
    prefs_manager = get_preferences()
    notification_manager = get_notification_manager()
    
    # Load current preferences
    user_prefs = prefs_manager.get_user_prefs(user_email)
    channel_status = notification_manager.get_channel_status()
    
    st.markdown("---")
    
    # ============ Channel Configuration ============
    st.markdown("### 📬 推送渠道")
    
    col1, col2, col3 = st.columns(3)
    
    # Telegram
    with col1:
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.6); padding: 1rem; border-radius: 12px; border: 1px solid rgba(99, 102, 241, 0.2);">
            <h4 style="margin: 0;">📱 Telegram</h4>
        </div>
        """, unsafe_allow_html=True)
        
        tg_prefs = user_prefs.get("channels", {}).get("telegram", {})
        tg_enabled = st.checkbox(
            "启用 Telegram",
            value=tg_prefs.get("enabled", False),
            key="tg_enabled",
            disabled=not channel_status["telegram"]
        )
        
        if not channel_status["telegram"]:
            st.caption("⚠️ 系统未配置 Telegram Bot")
        else:
            tg_chat_id = st.text_input(
                "Chat ID (可选，留空使用默认)",
                value=tg_prefs.get("chat_id", ""),
                key="tg_chat_id",
                placeholder="例如: 123456789"
            )
            
            if st.button("📤 发送测试", key="test_tg", use_container_width=True):
                with st.spinner("发送中..."):
                    success, error = notification_manager.send_test_notification(user_email, "telegram")
                    if success:
                        st.success("✅ Telegram 测试消息已发送!")
                    else:
                        st.error(f"❌ 发送失败: {error}")
    
    # Email
    with col2:
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.6); padding: 1rem; border-radius: 12px; border: 1px solid rgba(99, 102, 241, 0.2);">
            <h4 style="margin: 0;">📧 邮件</h4>
        </div>
        """, unsafe_allow_html=True)
        
        email_prefs = user_prefs.get("channels", {}).get("email", {})
        email_enabled = st.checkbox(
            "启用邮件推送",
            value=email_prefs.get("enabled", True),
            key="email_enabled",
            disabled=not channel_status["email"]
        )
        
        if not channel_status["email"]:
            st.caption("⚠️ 系统未配置 SMTP")
        else:
            email_address = st.text_input(
                "接收邮箱",
                value=email_prefs.get("address", user_email),
                key="email_address"
            )
            
            if st.button("📤 发送测试", key="test_email", use_container_width=True):
                with st.spinner("发送中..."):
                    success, error = notification_manager.send_test_notification(user_email, "email")
                    if success:
                        st.success("✅ 测试邮件已发送!")
                    else:
                        st.error(f"❌ 发送失败: {error}")
    
    # WeChat
    with col3:
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.6); padding: 1rem; border-radius: 12px; border: 1px solid rgba(99, 102, 241, 0.2);">
            <h4 style="margin: 0;">💬 企业微信</h4>
        </div>
        """, unsafe_allow_html=True)
        
        wechat_prefs = user_prefs.get("channels", {}).get("wechat", {})
        wechat_enabled = st.checkbox(
            "启用企业微信",
            value=wechat_prefs.get("enabled", False),
            key="wechat_enabled",
            disabled=not channel_status["wechat"]
        )
        
        if not channel_status["wechat"]:
            st.caption("⚠️ 系统未配置企业微信")
        else:
            wechat_user_id = st.text_input(
                "用户ID (留空发送给所有人)",
                value=wechat_prefs.get("user_id", ""),
                key="wechat_user_id"
            )
            
            if st.button("📤 发送测试", key="test_wechat", use_container_width=True):
                with st.spinner("发送中..."):
                    success, error = notification_manager.send_test_notification(user_email, "wechat")
                    if success:
                        st.success("✅ 微信测试消息已发送!")
                    else:
                        st.error(f"❌ 发送失败: {error}")
    
    st.markdown("---")
    
    # ============ Schedule Settings ============
    st.markdown("### ⏰ 推送时间")
    
    schedule_prefs = user_prefs.get("schedule", {})
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        schedule_enabled = st.checkbox(
            "启用每日推送",
            value=schedule_prefs.get("enabled", True),
            key="schedule_enabled"
        )
    
    with col2:
        push_time = st.time_input(
            "推送时间",
            value=_parse_time(schedule_prefs.get("time", "08:00")),
            key="push_time"
        )
    
    with col3:
        frequency = st.selectbox(
            "推送频率",
            ["daily", "weekdays", "weekends"],
            index=["daily", "weekdays", "weekends"].index(schedule_prefs.get("frequency", "daily")),
            format_func=lambda x: {"daily": "每天", "weekdays": "工作日", "weekends": "周末"}[x],
            key="frequency"
        )
    
    st.markdown("---")
    
    # ============ Content Preferences ============
    st.markdown("### 📚 内容偏好")
    
    content_prefs = user_prefs.get("content", {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        include_coding = st.checkbox("💻 Coding 练习", value=content_prefs.get("include_coding", True))
        include_ml = st.checkbox("🧠 ML 理论", value=content_prefs.get("include_ml_theory", True))
    
    with col2:
        include_sd = st.checkbox("🏗️ 系统设计", value=content_prefs.get("include_system_design", True))
        include_bq = st.checkbox("🗣️ Behavioral", value=content_prefs.get("include_behavioral", True))
    
    task_count = st.slider(
        "每日任务数量",
        min_value=1,
        max_value=5,
        value=content_prefs.get("task_count", 3),
        key="task_count"
    )
    
    priority_gaps = st.checkbox(
        "🎯 优先推送 Gap 技能",
        value=content_prefs.get("priority_gaps", True),
        help="根据你的 Gap Analysis 结果，优先推送需要补齐的技能"
    )
    
    st.markdown("---")
    
    # ============ Save Button ============
    if st.button("💾 保存设置", use_container_width=True, type="primary"):
        # Build updated preferences
        updated_prefs = {
            "email": user_email,
            "channels": {
                "telegram": {
                    "enabled": tg_enabled,
                    "chat_id": st.session_state.get("tg_chat_id", "")
                },
                "email": {
                    "enabled": email_enabled,
                    "address": st.session_state.get("email_address", user_email)
                },
                "wechat": {
                    "enabled": wechat_enabled,
                    "user_id": st.session_state.get("wechat_user_id", "")
                }
            },
            "schedule": {
                "enabled": schedule_enabled,
                "time": push_time.strftime("%H:%M"),
                "timezone": "Asia/Shanghai",
                "frequency": frequency
            },
            "content": {
                "include_coding": include_coding,
                "include_ml_theory": include_ml,
                "include_system_design": include_sd,
                "include_behavioral": include_bq,
                "task_count": task_count,
                "priority_gaps": priority_gaps
            }
        }
        
        if prefs_manager.save_user_prefs(user_email, updated_prefs):
            st.success("✅ 设置已保存!")
            st.balloons()
        else:
            st.error("❌ 保存失败，请重试")
    
    st.markdown("---")
    
    # ============ Notification History ============
    st.markdown("### 📋 推送历史")
    
    logs = prefs_manager.get_user_logs(user_email, limit=10)
    
    if logs:
        for log in logs:
            timestamp = log.get("timestamp", "")[:16].replace("T", " ")
            channel = log.get("channel", "unknown")
            status = log.get("status", "unknown")
            
            channel_icons = {"telegram": "📱", "email": "📧", "wechat": "💬"}
            status_icons = {"success": "✅", "failed": "❌", "skipped": "⏭️"}
            
            st.markdown(
                f"{channel_icons.get(channel, '📬')} **{channel.title()}** - "
                f"{status_icons.get(status, '❓')} {status} - "
                f"`{timestamp}`"
            )
    else:
        st.info("暂无推送记录")


def _parse_time(time_str: str):
    """Parse time string to datetime.time object."""
    from datetime import time
    try:
        parts = time_str.split(":")
        return time(int(parts[0]), int(parts[1]))
    except Exception:
        return time(8, 0)
