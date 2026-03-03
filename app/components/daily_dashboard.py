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
    
    # Check if user has set up their profile or study plan
    user_data = daily_learning.get_user_profile(user_id)
    from data.learning_planner import learning_planner
    plan_data = learning_planner.get_user_plan(user_id)
    
    if not plan_data or plan_data.get("status") != "active":
        from components.learning_plan import render_plan_selection
        render_plan_selection(user_id)
        return
        
    user_profile = user_data.get("profile", {}) if user_data else {}
    # Synthesize dummy profile from study plan if missing
    if not user_profile and plan_data:
        user_profile = {
            "target_company": "Any",
            "target_role": plan_data.get("target_role", "SDE/MLE"),
            "interview_date": plan_data.get("end_date", (datetime.now() + timedelta(days=30)).isoformat()),
            "daily_hours": plan_data.get("daily_hours", 2),
            "weak_areas": []
        }
    
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
    
    # ============ Daily Journal & AI Reflection ============
    st.markdown("---")
    st.markdown("### 📔 今日学习日记 & AI 回顾")
    st.caption("记录今天学了什么，AI 帮你回顾并建议明天的计划。")
    
    journal_key = f"journal_{user_id}_{today}"
    
    # Load existing journal
    import json
    journal_file = Path(__file__).parent.parent.parent / "data" / "daily_journals.json"
    if not journal_file.exists():
        journal_file.write_text('{}', encoding='utf-8')
    
    try:
        all_journals = json.loads(journal_file.read_text(encoding='utf-8'))
    except:
        all_journals = {}
    
    user_journals = all_journals.get(user_id, {})
    today_journal = user_journals.get(today, {})
    
    # Journal input
    with st.form(f"daily_journal_form_{today}"):
        st.markdown("#### ✏️ 今天你学了什么？")
        
        col_j1, col_j2 = st.columns(2)
        with col_j1:
            topics_learned = st.text_area(
                "📚 学习内容",
                value=today_journal.get("topics", ""),
                height=80,
                placeholder="例: 复习了 Transformer 注意力机制，做了 LeetCode 146 LRU Cache..."
            )
        with col_j2:
            difficulties = st.text_area(
                "❓ 遇到的困难/不确定的点",
                value=today_journal.get("difficulties", ""),
                height=80,
                placeholder="例: 不太理解 multi-head attention 的维度变化，A/B testing 的 power analysis..."
            )
        
        mood = st.select_slider(
            "今天的学习状态",
            options=["😫 很差", "😐 一般", "🙂 还行", "😄 不错", "🔥 超棒"],
            value=today_journal.get("mood", "🙂 还行"),
            key=f"mood_{today}"
        )
        
        hours = st.slider("今天学习了多少小时？", 0.0, 8.0, 
                          float(today_journal.get("hours", 0.0)), 0.5, key=f"hours_{today}")
        
        save_journal = st.form_submit_button("💾 保存日记", type="primary")
        
        if save_journal:
            today_journal = {
                "topics": topics_learned,
                "difficulties": difficulties,
                "mood": mood,
                "hours": hours,
                "saved_at": datetime.now().isoformat()
            }
            if user_id not in all_journals:
                all_journals[user_id] = {}
            all_journals[user_id][today] = today_journal
            journal_file.write_text(json.dumps(all_journals, indent=2, ensure_ascii=False), encoding='utf-8')
            st.success("✅ 今日日记已保存！")
            st.rerun()
    
    # AI Reflection button
    if today_journal.get("topics"):
        if st.button("🤖 AI 帮我回顾 & 规划明天", type="primary", use_container_width=True):
            with st.spinner("AI Coach 正在分析你的学习记录..."):
                ai_feedback = _get_ai_reflection(today_journal, user_profile, user_journals)
                st.session_state[f"ai_reflection_{today}"] = ai_feedback
        
        # Display AI feedback
        ai_feedback = st.session_state.get(f"ai_reflection_{today}")
        if ai_feedback:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1e3a5f, #2d1b4e); padding: 1.25rem; 
                        border-radius: 12px; margin-top: 0.75rem;">
                <p style="margin: 0 0 0.5rem 0; color: #60a5fa; font-weight: 600;">🤖 AI Coach 反馈</p>
                <div style="color: #e2e8f0; font-size: 0.9rem; line-height: 1.6;">
                    {ai_feedback}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Show recent journal entries
    past_entries = [(d, j) for d, j in sorted(user_journals.items(), reverse=True) if d != today]
    if past_entries:
        with st.expander(f"📅 历史日记 ({len(past_entries)} 天)"):
            for date_str, entry in past_entries[:7]:
                st.markdown(f"""
                <div style="background: #1e293b; padding: 0.75rem; border-radius: 8px; margin-bottom: 0.5rem;">
                    <p style="margin: 0; color: #60a5fa; font-weight: 600;">📅 {date_str} | {entry.get('mood', '')} | ⏱️ {entry.get('hours', 0)}h</p>
                    <p style="margin: 0.25rem 0; color: #e2e8f0; font-size: 0.85rem;">📚 {entry.get('topics', '无记录')[:100]}</p>
                    {f'<p style="margin: 0; color: #fca5a5; font-size: 0.8rem;">❓ {entry.get("difficulties", "")[:80]}</p>' if entry.get('difficulties') else ''}
                </div>
                """, unsafe_allow_html=True)
    
    # Quick actions
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⚙️ 重设/选择其他学习计划", use_container_width=True):
            st.session_state.show_setup = True
            st.rerun()
    
    with col2:
        if st.button("📊 查看学习统计", use_container_width=True):
            show_stats(user_id)
    
    # Show setup wizard if requested
    if st.session_state.get("show_setup"):
        from components.learning_plan import render_plan_selection
        render_plan_selection(user_id)


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
            link_html = ""
            if mission.get("link"):
                link_label = mission.get("link_label", "🔗 开始")
                link_html = f'<a href="{mission["link"]}" target="_blank" style="color: #60a5fa; font-size: 0.8rem; text-decoration: none;">{link_label} →</a>'
            
            st.markdown(f"""
            <div style="background: {bg_color}; padding: 1rem; border-radius: 12px; 
                        border-left: 4px solid {border_color}; 
                        opacity: {'0.6' if is_completed else '1'};">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="font-size: 1.5rem;">{mission.get('icon', '📌')}</span>
                    <div style="flex: 1;">
                        <p style="margin: 0; color: #f1f5f9; font-weight: 600; 
                                  text-decoration: {'line-through' if is_completed else 'none'};">
                            {mission.get('title', '')}
                        </p>
                        <p style="margin: 0; color: #94a3b8; font-size: 0.85rem;">
                            {mission.get('description', '')}
                        </p>
                        {f'<p style="margin: 0.25rem 0 0 0;">{link_html}</p>' if link_html else ''}
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


def _get_ai_reflection(today_journal: dict, user_profile: dict, user_journals: dict) -> str:
    """Use AI to reflect on today's learning and suggest tomorrow's plan."""
    import os
    try:
        import google.generativeai as genai
        api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", "")
        if not api_key:
            return _fallback_reflection(today_journal)
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        # Build context from recent journals
        recent_days = sorted(user_journals.items(), reverse=True)[:5]
        history_text = ""
        for d, j in recent_days:
            history_text += f"- {d}: 学习了{j.get('topics','?')}, 状态:{j.get('mood','?')}, {j.get('hours',0)}h\n"
        
        prompt = f"""你是一位温暖又专业的面试準备教练。请根据学员今天的学习日记给出反馈和明日计划。

学员背景:
- 目标公司: {user_profile.get('target_company', '未设置')}
- 目标角色: {user_profile.get('target_role', 'MLE')}

今日日记:
- 学习内容: {today_journal.get('topics', '未填写')}
- 遇到困难: {today_journal.get('difficulties', '无')}
- 学习状态: {today_journal.get('mood', '一般')}
- 学习时长: {today_journal.get('hours', 0)} 小时

最近学习记录:
{history_text or '无历史记录'}

请用以下格式回复 (用中文, 简洁有力, 总共不超过 300 字):

✅ **今日表现**: (对今天学习的肯定和客观评价)

💡 **关于你的困难**: (针对学员提到的困难给出具体建议或解题思路)

📋 **明日建议计划**:
1. (基于今天的薄弱点，建议明天做什么)
2. (补充练习)
3. (复习巩固)

💪 **鼓励**: (一句激励的话)
"""
        
        response = model.generate_content(prompt)
        # Convert markdown to HTML-safe
        text = response.text.replace("\n", "<br>")
        return text
    except Exception as e:
        return _fallback_reflection(today_journal)


def _fallback_reflection(today_journal: dict) -> str:
    """Fallback reflection when AI is not available."""
    hours = today_journal.get("hours", 0)
    topics = today_journal.get("topics", "")
    
    feedback = "✅ <b>今日表现</b>: "
    if hours >= 3:
        feedback += f"太厉害了！今天学习了 {hours} 小时，保持这个节奏！<br><br>"
    elif hours >= 1:
        feedback += f"不错，{hours}小时的练习正在积累实力。<br><br>"
    else:
        feedback += "每一步都算数。明天可以试着多投入一点时间。<br><br>"
    
    if today_journal.get("difficulties"):
        feedback += f"💡 <b>关于你的困难</b>: 建议把不确定的点记下来，明天专门花 30 分钟研究一下。可以在题库里搜索相关topic做几道练习题。<br><br>"
    
    feedback += "📋 <b>明日建议</b>:<br>"
    feedback += "1. 复习今天的重点内容（间隔重复效果最佳）<br>"
    feedback += "2. 做 1-2 道相关的面试题<br>"
    feedback += "3. 花 20 分钟浏览最新论文<br><br>"
    feedback += "💪 <b>坚持就是胜利，你离 Offer 越来越近了！</b>"
    
    return feedback


def render_setup_wizard_deprecated(user_id: str, is_edit: bool = False):
    from components.learning_plan import render_plan_selection
    render_plan_selection(user_id)

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
