"""
Learning Plan UI Component
Displays daily study tasks and progress tracking
"""
import streamlit as st
from datetime import datetime
from pathlib import Path
import sys

# Add parent path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def render_learning_plan():
    """Render the learning plan page."""
    from data.learning_planner import (
        learning_planner, get_today_study_tasks, get_study_progress,
        mark_task_complete, get_plan_templates, create_study_plan
    )
    
    st.markdown("## 📅 每日学习计划")
    st.markdown("*个性化学习路线，助你高效备战面试*")
    
    # Get user ID
    user_id = st.session_state.get("user_email", "guest")
    
    # Check if user has a plan
    progress = get_study_progress(user_id)
    
    # Show plan selection if no active plan
    if not progress.get("has_plan"):
        render_plan_selection(user_id)
        return
    
    # Show today's tasks
    today_tasks = get_today_study_tasks(user_id)
    
    # Header with progress
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 总进度", f"{progress['progress_percent']}%")
    
    with col2:
        st.metric("📅 学习天数", f"{progress['completed_days']}/{progress['total_days']}")
    
    with col3:
        st.metric("🔥 连续打卡", f"{progress['streak_days']} 天")
    
    with col4:
        st.metric("📆 当前周", f"第 {progress.get('current_week', 1)} 周")
    
    # Progress bar
    st.progress(progress['progress_percent'] / 100)
    
    st.markdown("---")
    
    # Today's focus
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1e3a5f 0%, #2d1b4e 100%); 
                padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem;">
        <h3 style="margin: 0; color: #60a5fa;">📌 今日重点: {today_tasks['phase_name']}</h3>
        <p style="color: #94a3b8; margin: 0.5rem 0 0 0;">
            第 {today_tasks['week']} 周 · {today_tasks['date']} · 
            预计学习 {today_tasks['total_minutes']} 分钟
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Motivational quote
    st.info(f"💡 {today_tasks['motivational_quote']}")
    
    # Today's tasks
    st.markdown("### 📋 今日任务")
    
    for i, task in enumerate(today_tasks['tasks']):
        task_key = f"task_{task['type']}_{i}"
        
        with st.container():
            col1, col2, col3 = st.columns([1, 4, 1])
            
            with col1:
                st.markdown(f"<h2 style='margin: 0;'>{task['icon']}</h2>", 
                          unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"**{task['name']}** ({task['duration_minutes']} 分钟)")
                st.markdown(f"*{task['suggested_activity']}*")
                if task.get('topic'):
                    st.markdown(f"📎 主题: {task['topic']}")
            
            with col3:
                if st.button("✅ 完成", key=task_key):
                    mark_task_complete(user_id, task['type'])
                    st.success("打卡成功！")
                    st.rerun()
        
        st.markdown("---")
    
    # Quick actions
    st.markdown("### ⚡ 快捷操作")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📝 刷题", use_container_width=True):
            st.session_state.nav_selection = "🎯 题库练习"
            st.rerun()
    
    with col2:
        if st.button("📰 阅读", use_container_width=True):
            st.session_state.nav_selection = "📖 技术资源"
            st.rerun()
    
    with col3:
        if st.button("🎤 模拟", use_container_width=True):
            st.session_state.nav_selection = "🎤 AI模拟面试"
            st.rerun()
    
    with col4:
        if st.button("🔄 换计划", use_container_width=True):
            # Clear current plan
            data = learning_planner._load_plans()
            if user_id in data["plans"]:
                del data["plans"][user_id]
                learning_planner._save_plans(data)
            st.rerun()
    
    # Week overview
    with st.expander("📊 本周计划概览", expanded=False):
        plan = learning_planner.get_user_plan(user_id)
        if plan:
            current_week = progress.get('current_week', 1)
            for phase in plan['phases']:
                if current_week in phase['week']:
                    st.markdown(f"**{phase['name']}**")
                    st.markdown("**学习主题:**")
                    for topic in phase['topics']:
                        st.markdown(f"- {topic}")
                    
                    st.markdown("**每日时间分配:**")
                    for task_type, minutes in phase['daily_tasks'].items():
                        if minutes > 0:
                            task_info = learning_planner.TASK_TYPES.get(task_type, {})
                            st.markdown(f"- {task_info.get('icon', '')} {task_info.get('name', task_type)}: {minutes} 分钟")
                    break


def render_plan_selection(user_id: str):
    """Render plan selection UI for new users."""
    from data.learning_planner import get_plan_templates, create_study_plan
    
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h2>🎯 开始你的面试准备之旅</h2>
        <p style="color: #94a3b8;">选择一个学习计划，系统将为你生成每日任务</p>
    </div>
    """, unsafe_allow_html=True)
    
    templates = get_plan_templates()
    
    cols = st.columns(len(templates))
    
    for i, template in enumerate(templates):
        with cols[i]:
            st.markdown(f"""
            <div style="background: #1e293b; padding: 1.5rem; border-radius: 12px; 
                        text-align: center; height: 280px;">
                <h3 style="color: #60a5fa;">{template['name']}</h3>
                <p style="color: #94a3b8;">⏱️ {template['duration_weeks']} 周</p>
                <p style="color: #94a3b8;">🎯 {template['target_role']}</p>
                <p style="font-size: 0.9rem; color: #64748b;">
                    {template['description']}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"选择此计划", key=f"select_{template['id']}", 
                        use_container_width=True):
                create_study_plan(user_id, template['id'])
                st.success(f"🎉 已创建 {template['name']}！")
                st.rerun()
    
    st.markdown("---")
    
    # Custom plan option
    with st.expander("⚙️ 自定义计划 (高级)", expanded=False):
        st.markdown("*根据你的时间安排自定义每日学习时长*")
        
        daily_hours = st.slider("每日学习时间 (小时)", 0.5, 4.0, 2.0, 0.5)
        
        focus_areas = st.multiselect(
            "重点领域",
            ["ML 基础", "深度学习", "系统设计", "编程", "行为面试"],
            default=["ML 基础", "系统设计"]
        )
        
        target_date = st.date_input("目标面试日期")
        
        if st.button("生成自定义计划", use_container_width=True):
            # Use 8-week template with custom settings
            plan = create_study_plan(user_id, "mle_8week")
            st.success("🎉 计划创建成功！")
            st.rerun()


def render_study_calendar():
    """Render a calendar view of study progress."""
    st.markdown("### 📅 学习日历")
    
    # Simple calendar view using colored boxes
    from data.learning_planner import learning_planner
    user_id = st.session_state.get("user_email", "guest")
    plan = learning_planner.get_user_plan(user_id)
    
    if not plan:
        st.info("创建学习计划后可查看日历")
        return
    
    daily_logs = plan.get("daily_logs", {})
    
    # Show last 4 weeks
    cols = st.columns(7)
    days = ["一", "二", "三", "四", "五", "六", "日"]
    
    for i, day in enumerate(days):
        with cols[i]:
            st.markdown(f"**{day}**")
    
    # Generate calendar grid
    from datetime import datetime, timedelta
    today = datetime.now().date()
    start = today - timedelta(days=today.weekday() + 21)  # 3 weeks ago, Monday
    
    for week in range(4):
        cols = st.columns(7)
        for day in range(7):
            check_date = start + timedelta(days=week*7 + day)
            date_str = check_date.isoformat()
            
            with cols[day]:
                if date_str in daily_logs:
                    st.markdown("🟢")
                elif check_date < today:
                    st.markdown("⚫")
                elif check_date == today:
                    st.markdown("🔵")
                else:
                    st.markdown("⚪")
