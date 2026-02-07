"""
Redesigned Main App - Minimalist Interview Prep Dashboard
Focus: AI-driven, single-page workflow, crystal-clear progress tracking
"""
import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json

# Add parent directory to path
app_dir = Path(__file__).parent
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))

# Import components
from components.auth import check_authentication, render_auth_page, logout, get_current_user
from components.i18n import LANGUAGES
from components.ai_coach import ai_coach

# Page config
st.set_page_config(
    page_title="Interview Prep - AI Coach",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"  # Hide sidebar by default
)

# Custom CSS for minimalist design
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Minimalist color scheme */
    :root {
        --primary: #3b82f6;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --bg-dark: #0f172a;
        --bg-card: #1e293b;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
    }
    
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* Hero section */
    .hero {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        color: white;
    }
    
    .hero h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .hero p {
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* Mission cards */
    .mission-card {
        background: var(--bg-card);
        border-left: 4px solid var(--primary);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        transition: transform 0.2s;
    }
    
    .mission-card:hover {
        transform: translateX(4px);
    }
    
    .mission-card.completed {
        border-left-color: var(--success);
        opacity: 0.6;
    }
    
    /* Progress ring */
    .progress-ring {
        text-align: center;
        padding: 2rem;
    }
    
    .progress-number {
        font-size: 3rem;
        font-weight: 700;
        color: var(--primary);
    }
    
    /* Quick action buttons */
    .quick-action {
        background: var(--bg-card);
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s;
        border: 2px solid transparent;
    }
    
    .quick-action:hover {
        border-color: var(--primary);
        transform: translateY(-2px);
    }
    
    /* Stats */
    .stat-card {
        background: var(--bg-card);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary);
    }
    
    .stat-label {
        color: var(--text-secondary);
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


def render_ai_briefing(user_email: str):
    """AI-generated daily briefing."""
    st.markdown("### 🤖 AI Daily Briefing")
    
    # Get user profile (TODO: load from actual storage)
    user_profile = {
        "interview_date": (datetime.now() + timedelta(days=45)).isoformat(),
        "target_company": "Google",
        "target_role": "MLE",
        "weak_areas": ["System Design", "ML Theory"]
    }
    
    # Generate AI briefing
    briefing_data = ai_coach.generate_daily_briefing(user_email, user_profile)
    
    days_text = f"**{briefing_data['days_left']} days**" if briefing_data['days_left'] else "soon"
    
    briefing = f"""
    **{briefing_data['greeting']}**
    
    📅 {days_text} until your {briefing_data['target_company']} {briefing_data['target_role']} interview
    
    🎯 **Today's Focus**: {briefing_data['focus_today']}
    
    💡 **AI Insight**: {briefing_data['ai_insight']}
    """
    
    if briefing_data.get('new_content_alert'):
        briefing += f"\n\n{briefing_data['new_content_alert']}"
    
    briefing += f"\n\n⚡ {briefing_data['motivation']}"
    
    st.info(briefing)


def render_todays_missions(user_email: str):
    """Render today's 3 core missions."""
    st.markdown("### 🎯 Today's Missions")
    st.markdown("*Complete these 3 tasks to level up*")
    
    # Get user profile
    user_profile = {
        "interview_date": (datetime.now() + timedelta(days=45)).isoformat(),
        "target_company": "Google",
        "target_role": "MLE",
        "weak_areas": ["System Design"]
    }
    
    # Generate missions from AI Coach
    missions = ai_coach.generate_daily_missions(user_email, user_profile)
    
    for idx, mission in enumerate(missions):
        completed_class = "completed" if mission.get("completed") else ""
        # Use index + type for unique key to avoid duplicates
        checkbox_key = f"mission_{idx}_{mission.get('type', 'task')}"
        
        col1, col2 = st.columns([0.05, 0.95])
        
        with col1:
            completed = st.checkbox("", key=checkbox_key, value=mission.get("completed", False))
        
        with col2:
            st.markdown(f"""
            <div class="mission-card {completed_class}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="font-size: 1.5rem;">{mission['icon']}</span>
                        <strong style="font-size: 1.1rem; margin-left: 0.5rem;">{mission['title']}</strong>
                        <p style="color: var(--text-secondary); margin-top: 0.5rem; margin-bottom: 0;">
                            {mission['description']}
                        </p>
                    </div>
                    <div style="text-align: right;">
                        <span style="background: var(--primary); padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.85rem;">
                            {mission['duration']}
                        </span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)


def render_progress_overview(user_email: str):
    """Render overall progress."""
    st.markdown("### 📊 Your Progress")
    
    col1, col2, col3, col4 = st.columns(4)
    
    stats = [
        {"label": "Coding", "value": "67%", "color": "#10b981"},
        {"label": "System Design", "value": "45%", "color": "#f59e0b"},
        {"label": "ML Theory", "value": "82%", "color": "#3b82f6"},
        {"label": "Streak", "value": "7🔥", "color": "#ef4444"}
    ]
    
    for col, stat in zip([col1, col2, col3, col4], stats):
        with col:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number" style="color: {stat['color']};">{stat['value']}</div>
                <div class="stat-label">{stat['label']}</div>
            </div>
            """, unsafe_allow_html=True)


def render_quick_actions():
    """Quick action buttons."""
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🎤 Mock Interview", use_container_width=True):
            st.session_state.page = "mock"
    
    with col2:
        if st.button("📝 Add Question", use_container_width=True):
            st.session_state.page = "add_question"
    
    with col3:
        if st.button("🔥 Trending Topics", use_container_width=True):
            st.session_state.page = "trending"
    
    with col4:
        if st.button("📊 Full Progress", use_container_width=True):
            st.session_state.page = "progress"


def render_today_page(user_email: str):
    """Main 'Today' dashboard - 80% of user time here."""
    
    # Hero section
    st.markdown(f"""
    <div class="hero">
        <h1>🎯 Today's Battle Plan</h1>
        <p>{datetime.now().strftime('%A, %B %d, %Y')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # AI Briefing
    render_ai_briefing(user_email)
    
    st.markdown("---")
    
    # Today's missions
    render_todays_missions(user_email)
    
    st.markdown("---")
    
    # Progress overview
    render_progress_overview(user_email)
    
    st.markdown("---")
    
    # Quick actions
    render_quick_actions()


def render_progress_page(user_email: str):
    """Detailed progress tracking page."""
    st.markdown("## 📊 Progress Tracking")
    
    st.info("🚧 Deep progress analytics coming soon!")
    
    # TODO: Implement
    # - Knowledge graph visualization
    # - Weak points heatmap
    # - Historical performance
    # - Comparison with peers


def render_settings_page(user_email: str):
    """Settings and profile page."""
    st.markdown("## ⚙️ Settings")
    
    with st.form("profile_settings"):
        st.markdown("### 🎯 Interview Goals")
        
        col1, col2 = st.columns(2)
        
        with col1:
            target_company = st.selectbox(
                "Target Company",
                ["Google", "Meta", "OpenAI", "Amazon", "Microsoft", "Netflix"]
            )
            target_role = st.selectbox(
                "Target Role",
                ["MLE", "SWE", "Research Scientist", "Data Scientist"]
            )
        
        with col2:
            interview_date = st.date_input(
                "Interview Date",
                value=datetime.now() + timedelta(days=45)
            )
            daily_hours = st.slider(
                "Daily Study Hours",
                min_value=1,
                max_value=8,
                value=3
            )
        
        st.markdown("### 🎯 Focus Areas")
        weak_areas = st.multiselect(
            "What do you want to focus on?",
            ["Coding", "System Design", "ML Theory", "Behavioral", "LLM/GenAI"],
            default=["System Design", "ML Theory"]
        )
        
        submitted = st.form_submit_button("💾 Save Settings", use_container_width=True)
        
        if submitted:
            st.success("✅ Settings saved!")


def main():
    """Main app entry point."""
    
    # Check authentication
    if not check_authentication():
        render_auth_page()
        return
    
    user_email = get_current_user()
    
    # Top navigation bar
    col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
    
    with col1:
        st.markdown("### 🎯 Interview Prep AI")
    
    with col3:
        if st.button("🏠 Today"):
            st.session_state.page = "today"
    
    with col4:
        if st.button("📊 Progress"):
            st.session_state.page = "progress"
    
    with col5:
        if st.button("⚙️ Settings"):
            st.session_state.page = "settings"
    
    st.markdown("---")
    
    # Initialize page state
    if "page" not in st.session_state:
        st.session_state.page = "today"
    
    # Route to appropriate page
    if st.session_state.page == "today":
        render_today_page(user_email)
    elif st.session_state.page == "progress":
        render_progress_page(user_email)
    elif st.session_state.page == "settings":
        render_settings_page(user_email)


if __name__ == "__main__":
    main()
