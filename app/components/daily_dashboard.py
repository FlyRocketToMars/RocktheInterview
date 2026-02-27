"""
Daily Learning Dashboard Component
Displays personalized daily study tasks in a foolproof format
"""
import streamlit as st
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from data.daily_learning import daily_learning
from components.ai_coach import ai_coach


def render_daily_dashboard():
    """Render the daily learning dashboard using AI Coach."""
    
    user_id = st.session_state.get("user_email", "guest")
    
    # Check if user has set up their profile
    user_data = daily_learning.get_user_profile(user_id)
    
    if not user_data:
        render_setup_wizard(user_id)
        return
        
    user_profile = user_data.get("profile", {})
    
    # AI Generation
    with st.spinner("🤖 AI Coach 正在生成今日简报..."):
        briefing = ai_coach.generate_daily_briefing(user_id, user_profile)
        missions = ai_coach.generate_daily_missions(user_id, user_profile)
    
    # Header with AI Greeting
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1e3a5f 0%, #2d1b4e 100%); 
                padding: 1.5rem; border-radius: 16px; margin-bottom: 1.5rem; text-align: center;">
        <h1 style="margin: 0; font-size: 2rem;">
            {briefing.get('greeting', '☀️ 今日学习计划')}
        </h1>
        <p style="color: #94a3b8; margin: 0.5rem 0 0 0; font-size: 1.1rem;">
            {briefing.get('motivation', '')}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # AI Insight Alert
    if briefing.get('ai_insight'):
        st.info(f"💡 **AI 诊断**: {briefing['ai_insight']}")
        
    if briefing.get('new_content_alert'):
        st.warning(f"🔔 **新内容推送**: {briefing['new_content_alert']}")
    
    # Stats row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style="background: #1e293b; padding: 1rem; border-radius: 12px; text-align: center;">
            <p style="color: #64748b; margin: 0; font-size: 0.8rem;">今日重点</p>
            <p style="color: #60a5fa; margin: 0; font-size: 1.1rem; font-weight: 600;">
                {briefing.get('focus_today', '综合')}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        days_left = briefing.get('days_left')
        color = "#22c55e" if days_left and days_left > 14 else "#eab308" if days_left and days_left > 7 else "#ef4444"
        st.markdown(f"""
        <div style="background: #1e293b; padding: 1rem; border-radius: 12px; text-align: center;">
            <p style="color: #64748b; margin: 0; font-size: 0.8rem;">距面试</p>
            <p style="color: {color}; margin: 0; font-size: 1.5rem; font-weight: 700;">
                {days_left if days_left else '??'} 天
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # We check session state for checked missions simply to display progress
        completed = sum(1 for m in missions if st.session_state.get(f"mission_{m['id']}", False))
        total = len(missions)
        st.markdown(f"""
        <div style="background: #1e293b; padding: 1rem; border-radius: 12px; text-align: center;">
            <p style="color: #64748b; margin: 0; font-size: 0.8rem;">今日进度</p>
            <p style="color: #22d3ee; margin: 0; font-size: 1.5rem; font-weight: 700;">
                {completed}/{total}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="background: #1e293b; padding: 1rem; border-radius: 12px; text-align: center;">
            <p style="color: #64748b; margin: 0; font-size: 0.8rem;">目标公司</p>
            <p style="color: #f472b6; margin: 0; font-size: 1.1rem; font-weight: 600;">
                {briefing.get('target_company', 'N/A')}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tasks
    st.markdown("### 🎯 Today's Missions")
    st.caption("AI 根据你的弱点和目标公司为你定制的专属今日任务。")
    
    today = datetime.now().strftime("%Y-%m-%d")
    for mission in missions:
        render_mission_card(user_id, today, mission)
    
    # Quick actions
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⚙️ 修改学习计划", use_container_width=True):
            st.session_state.show_setup = True
            st.rerun()
    
    with col2:
        if st.button("📊 查看学习统计", use_container_width=True):
            show_stats(user_id)
    
    # Show setup wizard if requested
    if st.session_state.get("show_setup"):
        render_setup_wizard(user_id, is_edit=True)


def render_mission_card(user_id: str, date: str, mission: dict):
    """Render a single AI mission card."""
    
    # We will use session state for now to track completion of UI-generated AI missions
    state_key = f"mission_{mission['id']}"
    is_completed = st.session_state.get(state_key, False)
    
    priority = mission.get("priority", "medium")
    
    priority_colors = {
        "high": "#ef4444",
        "medium": "#eab308",
        "low": "#22c55e"
    }
    
    bg_color = "#22c55e20" if is_completed else "#1e293b"
    border_color = "#22c55e" if is_completed else priority_colors.get(priority, "#6366f1")
    
    with st.container():
        col1, col2, col3 = st.columns([0.5, 5, 1])
        
        with col1:
            # Checkbox - checking it updates session state
            checked = st.checkbox(
                "",
                value=is_completed,
                key=f"chk_{state_key}",
                label_visibility="collapsed"
            )
            
            if checked != is_completed:
                st.session_state[state_key] = checked
                st.rerun()
        
        with col2:
            st.markdown(f"""
            <div style="background: {bg_color}; padding: 1rem; border-radius: 12px; 
                        border-left: 4px solid {border_color}; 
                        opacity: {'0.6' if is_completed else '1'};">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="font-size: 1.5rem;">{mission.get('icon', '📌')}</span>
                    <div>
                        <p style="margin: 0; color: #f1f5f9; font-weight: 600; 
                                  text-decoration: {'line-through' if is_completed else 'none'};">
                            {mission.get('title', '')}
                        </p>
                        <p style="margin: 0; color: #94a3b8; font-size: 0.85rem;">
                            {mission.get('description', '')}
                        </p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style="text-align: center; padding: 0.5rem;">
                <p style="margin: 0; color: #64748b; font-size: 0.75rem;">Duration</p>
                <p style="margin: 0; color: #94a3b8; font-size: 0.85rem;">{mission.get('duration', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Details expander based on mission type/content
        if mission.get("type") == "coding" and "content" in mission:
            with st.expander("📝 题目详情"):
                st.markdown(f"**题目:** {mission['content'].get('question', '')}")
                if "focus" in mission["content"]:
                    st.caption(f"重点解析: {mission['content']['focus']}")
        
        elif mission.get("type") == "reading" and "content" in mission:
            with st.expander("📖 阅读材料"):
                st.markdown(f"**主题:** {mission['content'].get('topic', '')}")
        
        elif mission.get("type") == "trending" and "content" in mission:
             with st.expander("🔥 前沿知识点"):
                st.markdown(f"**核心问题:** {mission['content'].get('title', '')}")
                st.info(mission['content'].get('description', ''))


def render_setup_wizard(user_id: str, is_edit: bool = False):
    """Render the setup wizard for new users."""
    
    st.markdown("## 🎯 设置你的面试目标")
    st.markdown("*告诉我们你的目标，系统会为你定制每日学习计划*")
    
    with st.form("setup_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            target_company = st.selectbox(
                "🏢 目标公司",
                options=["Google", "Meta", "Amazon", "Microsoft", "OpenAI", "TikTok", 
                         "Snap", "Stripe", "Uber", "Airbnb", "Netflix", "LinkedIn", "Apple", "NVIDIA", "其他"],
                index=0
            )
            
            target_role = st.selectbox(
                "💼 目标职位",
                options=["MLE", "SDE", "DS", "Research Scientist"],
                index=0
            )
            
            target_level = st.selectbox(
                "📊 目标级别",
                options=["L3/E3 (Junior)", "L4/E4 (Mid)", "L5/E5 (Senior)", "L6/E6 (Staff)", "L7+ (Principal+)"],
                index=2
            )
        
        with col2:
            interview_date = st.date_input(
                "📅 面试日期",
                value=datetime.now() + timedelta(days=30),
                min_value=datetime.now(),
                help="如果还不确定，选一个大概的日期"
            )
            
            daily_hours = st.slider(
                "⏰ 每天可学习时间 (小时)",
                min_value=1,
                max_value=8,
                value=2,
                help="包括刷题、复习、模拟面试等"
            )
        
        st.markdown("### 🎯 你的薄弱环节")
        st.caption("选择你需要重点加强的方向 (可多选)")
        
        weak_areas = []
        weak_col1, weak_col2, weak_col3, weak_col4 = st.columns(4)
        
        with weak_col1:
            if st.checkbox("🤖 LLM/GenAI", value=True):
                weak_areas.append("LLM")
        with weak_col2:
            if st.checkbox("🏗️ 系统设计"):
                weak_areas.append("System Design")
        with weak_col3:
            if st.checkbox("💻 算法编程"):
                weak_areas.append("Coding")
        with weak_col4:
            if st.checkbox("🗣️ 行为面试"):
                weak_areas.append("Behavioral")
        
        preferred_style = st.radio(
            "📚 学习风格偏好",
            options=["balanced", "intensive", "relaxed"],
            format_func=lambda x: {
                "balanced": "⚖️ 平衡型 - 每个方向都练",
                "intensive": "🔥 强化型 - 集中突破薄弱项",
                "relaxed": "🧘 舒适型 - 按自己节奏来"
            }[x],
            horizontal=True
        )
        
        submitted = st.form_submit_button("✅ 开始我的面试准备", use_container_width=True)
        
        if submitted:
            daily_learning.setup_user_profile(user_id, {
                "target_company": target_company,
                "target_role": target_role,
                "target_level": target_level.split()[0],  # Get L5 from "L5/E5 (Senior)"
                "interview_date": interview_date.strftime("%Y-%m-%d"),
                "daily_hours": daily_hours,
                "weak_areas": weak_areas,
                "preferred_style": preferred_style
            })
            
            st.success("🎉 设置完成！正在生成你的专属学习计划...")
            st.session_state.show_setup = False
            st.rerun()


def show_stats(user_id: str):
    """Show learning statistics."""
    
    stats = daily_learning.get_weekly_summary(user_id)
    
    st.markdown("### 📊 学习统计")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📝 完成题目", stats.get("total_questions", 0))
    with col2:
        st.metric("🏗️ 掌握主题", stats.get("total_topics", 0))
    with col3:
        hours = stats.get("total_minutes", 0) // 60
        st.metric("⏱️ 学习时长", f"{hours}h")
    with col4:
        st.metric("🔥 连续天数", stats.get("streak_days", 0))


# Main entry point
if __name__ == "__main__":
    render_daily_dashboard()
