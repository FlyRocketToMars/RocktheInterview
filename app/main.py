"""
MLE Interview Prep Platform
Main Streamlit Application Entry Point
"""
import streamlit as st
import json
from pathlib import Path

# Page config - must be first Streamlit command
st.set_page_config(
    page_title="RocktheInterview",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium dark theme
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary: #6366f1;
        --primary-dark: #4f46e5;
        --secondary: #22d3ee;
        --accent: #f472b6;
        --bg-dark: #0f172a;
        --bg-card: #1e293b;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
    }
    
    /* Dark background */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border-right: 1px solid rgba(99, 102, 241, 0.2);
    }
    
    /* Card styling */
    .css-1r6slb0, .css-12oz5g7 {
        background: rgba(30, 41, 59, 0.8);
        border-radius: 16px;
        border: 1px solid rgba(99, 102, 241, 0.2);
        backdrop-filter: blur(10px);
    }
    
    /* Headers */
    h1, h2, h3 {
        background: linear-gradient(90deg, #6366f1, #22d3ee);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #6366f1, #4f46e5);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #6366f1, #22d3ee);
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #22d3ee;
        font-size: 2.5rem !important;
    }
    
    /* Text inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 12px;
        color: #f1f5f9;
    }
    
    /* Select boxes */
    .stSelectbox > div > div {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 12px;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(30, 41, 59, 0.6);
        border-radius: 12px;
        color: #94a3b8;
        padding: 10px 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #6366f1, #4f46e5);
        color: white;
    }
    
    /* Cards container */
    .card {
        background: rgba(30, 41, 59, 0.8);
        border-radius: 16px;
        border: 1px solid rgba(99, 102, 241, 0.2);
        padding: 1.5rem;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
    }
    
    /* Animated gradient border */
    .gradient-border {
        position: relative;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(34, 211, 238, 0.1));
        border-radius: 16px;
        padding: 2px;
    }
    
    .gradient-border::before {
        content: "";
        position: absolute;
        inset: 0;
        border-radius: 16px;
        padding: 2px;
        background: linear-gradient(90deg, #6366f1, #22d3ee, #f472b6, #6366f1);
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        background-size: 300% 100%;
        animation: gradient-move 3s linear infinite;
    }
    
    @keyframes gradient-move {
        0% { background-position: 0% 50%; }
        100% { background-position: 300% 50%; }
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


def load_data():
    """Load company and skills data"""
    # data/ is at project root, main.py is in app/ folder
    data_dir = Path(__file__).parent.parent / "data"
    
    with open(data_dir / "companies.json", "r", encoding="utf-8") as f:
        companies = json.load(f)
    
    with open(data_dir / "skills_taxonomy.json", "r", encoding="utf-8") as f:
        skills = json.load(f)
    
    return companies, skills


def init_session_state():
    """Initialize session state variables"""
    if "user_profile" not in st.session_state:
        st.session_state.user_profile = {
            "resume_text": "",
            "extracted_skills": [],
            "projects": []
        }
    
    if "target" not in st.session_state:
        st.session_state.target = {
            "company": None,
            "level": None,
            "jd_text": "",
            "jd_skills": []
        }
    
    if "analysis" not in st.session_state:
        st.session_state.analysis = {
            "gaps": [],
            "strengths": [],
            "study_plan": []
        }
    
    if "current_step" not in st.session_state:
        st.session_state.current_step = 0


def render_hero():
    """Render the hero section"""
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="font-size: 3.5rem; margin-bottom: 0.5rem;">
            🎸 RocktheInterview
        </h1>
        <p style="font-size: 1.25rem; color: #94a3b8; max-width: 600px; margin: 0 auto;">
            基于 Gap Analysis 的个性化面试准备平台 - 支持SDE/MLE/PM/DS等多种角色
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_progress_steps():
    """Render the progress indicator"""
    steps = ["📄 简历", "🎯 目标", "📋 JD", "📊 分析", "📚 计划"]
    current = st.session_state.current_step
    
    cols = st.columns(len(steps))
    for i, (col, step) in enumerate(zip(cols, steps)):
        with col:
            if i < current:
                st.markdown(f"<div style='text-align:center; color:#22d3ee;'>✅ {step}</div>", unsafe_allow_html=True)
            elif i == current:
                st.markdown(f"<div style='text-align:center; color:#6366f1; font-weight:bold;'>➡️ {step}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='text-align:center; color:#64748b;'>○ {step}</div>", unsafe_allow_html=True)
    
    # Progress bar
    progress = (current / (len(steps) - 1)) if current > 0 else 0
    st.progress(progress)


def render_stats():
    """Render quick stats"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📄 简历技能", len(st.session_state.user_profile.get("extracted_skills", [])))
    
    with col2:
        st.metric("🎯 目标公司", st.session_state.target.get("company") or "未选择")
    
    with col3:
        gaps = st.session_state.analysis.get("gaps", [])
        st.metric("🔴 技能Gap", len(gaps))
    
    with col4:
        plan = st.session_state.analysis.get("study_plan", [])
        completed = sum(1 for item in plan if item.get("completed", False))
        total = len(plan) if plan else 0
        st.metric("✅ 学习进度", f"{completed}/{total}")


def main():
    """Main application entry point"""
    init_session_state()
    
    # Load data
    try:
        companies, skills = load_data()
        st.session_state.companies = companies
        st.session_state.skills_taxonomy = skills
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return
    
    # Import auth module
    from components.auth import check_authentication, render_auth_page, logout, get_current_user
    
    # Check authentication
    if not check_authentication():
        render_auth_page()
        return
    
    # Sidebar navigation
    with st.sidebar:
        # Language selector at top
        from components.i18n import LANGUAGES
        if "language" not in st.session_state:
            st.session_state.language = "zh"
        
        lang = st.selectbox(
            "🌐 语言/Language",
            list(LANGUAGES.keys()),
            format_func=lambda x: LANGUAGES[x],
            index=list(LANGUAGES.keys()).index(st.session_state.language),
            key="lang_selector"
        )
        st.session_state.language = lang
        
        st.markdown("---")
        
        # User info
        user_email = get_current_user()
        is_guest = st.session_state.get("is_guest", False)
        
        # Import translation function
        from components.i18n import t
        lang = st.session_state.get("language", "zh")
        
        if is_guest:
            st.markdown(f"### {t('sidebar_guest', lang)}")
            st.caption(t("sidebar_guest_hint", lang))
        else:
            st.markdown(f"### 👋 {user_email}")
        
        if st.button(t("auth_logout", lang), use_container_width=True):
            logout()
            st.rerun()
        
        st.markdown("---")
        st.markdown(f"### {t('nav_title', lang)}")
        
        # Build navigation options based on language
        nav_options = [
            t("nav_home", lang),
            t("nav_resume", lang),
            t("nav_target", lang),
            t("nav_jd", lang),
            t("nav_analysis", lang),
            t("nav_plan", lang),
            t("nav_questions", lang),
            t("nav_mock", lang),
            t("nav_jobs", lang),
            t("nav_resources", lang),
            t("nav_community", lang),
            t("nav_profile", lang),
            t("nav_notifications", lang),
        ]
        
        page = st.radio(
            t("nav_select", lang),
            nav_options,
            label_visibility="collapsed",
            key="nav_selection"
        )
        
        st.markdown("---")
        st.markdown(f"### {t('sidebar_stats', lang)}")
        render_stats()
        
        st.markdown("---")
        st.markdown(f"""
        <div style="text-align: center; color: #64748b; font-size: 0.8rem;">
            {t("footer", lang)}
        </div>
        """, unsafe_allow_html=True)
    
    # Get page index for routing
    from components.i18n import t
    lang = st.session_state.get("language", "zh")
    
    # Map pages by index
    page_index = nav_options.index(page) if page in nav_options else 0
    
    # Main content based on selected page index
    if page_index == 0:  # Home
        render_hero()
        render_progress_steps()
        
        st.markdown("---")
        
        # Feature cards
        st.markdown(f"### {t('home_features', lang)}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="card">
                <h3>{t('home_gap_title', lang)}</h3>
                <p style="color: #94a3b8;">
                    {t('home_gap_desc', lang)}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="card">
                <h3>{t('home_company_title', lang)}</h3>
                <p style="color: #94a3b8;">
                    {t('home_company_desc', lang)}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="card">
                <h3>{t('home_plan_title', lang)}</h3>
                <p style="color: #94a3b8;">
                    {t('home_plan_desc', lang)}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Quick start
        st.markdown(f"### {t('home_quickstart', lang)}")
        
        def start_prep():
            st.session_state.nav_selection = t("nav_resume", lang)
            st.session_state.current_step = 1
            
        st.button(t("home_start_btn", lang), 
                 use_container_width=True, 
                 on_click=start_prep)
    
    elif page_index == 1:  # Resume
        st.markdown(f"## {t('resume_title', lang)}")
        st.markdown(t("resume_hint", lang))
        
        # File uploader
        uploaded_file = st.file_uploader("📥 Upload Resume (PDF)", type="pdf")
        
        if uploaded_file is not None:
            from components.utils import parse_pdf
            with st.spinner("Parsing PDF..."):
                pdf_text = parse_pdf(uploaded_file.getvalue())
                if pdf_text and not pdf_text.startswith("Error"):
                     st.session_state.user_profile["resume_text"] = pdf_text
                     st.success("PDF loaded successfully! You can edit the text below if needed.")
                else:
                    st.error(f"Failed to parse PDF: {pdf_text}")
        
        resume_text = st.text_area(
            t("resume_label", lang),
            value=st.session_state.user_profile.get("resume_text", ""),
            height=400,
            placeholder=t("resume_placeholder", lang)
        )
        
        if st.button(t("resume_extract_btn", lang), use_container_width=True):
            if resume_text.strip():
                st.session_state.user_profile["resume_text"] = resume_text
                # Extract skills (简化版本，使用关键词匹配)
                from components.skill_extractor import extract_skills
                extracted = extract_skills(resume_text, st.session_state.skills_taxonomy)
                st.session_state.user_profile["extracted_skills"] = extracted
                st.session_state.current_step = 2
                st.success(t("resume_success", lang).format(len(extracted)))
                st.rerun()
            else:
                st.error(t("resume_error", lang))
    
    elif page_index == 2:  # Target
        st.markdown(f"## {t('target_title', lang)}")
        
        companies_data = st.session_state.companies.get("companies", [])
        role_descriptions = st.session_state.companies.get("role_descriptions", {})
        company_names = [c["name"] for c in companies_data]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            company = st.selectbox(t("target_company", lang), company_names)
        
        # Get selected company data
        selected_company = next((c for c in companies_data if c["name"] == company), None)
        
        with col2:
            # Get available roles for selected company
            available_roles = list(selected_company.get("roles", {}).keys()) if selected_company else []
            role = st.selectbox(t("target_role", lang), available_roles, 
                              format_func=lambda x: f"{x} - {role_descriptions.get(x, x)}")
        
        with col3:
            # Get levels for selected role
            role_data = selected_company.get("roles", {}).get(role, {}) if selected_company else {}
            levels = role_data.get("levels", [])
            level = st.selectbox(t("target_level", lang), levels)
        
        if selected_company and role and role_data:
            st.markdown(f"### {t('target_rounds', lang)}")
            for round_info in role_data.get("interview_rounds", []):
                focus_text = ', '.join(round_info['focus'])
                st.markdown(f"""
                <div class="card">
                    <strong>Round {round_info['round']}: {round_info['name']}</strong>
                    <br>
                    <span style="color: #94a3b8;">
                        ⏱️ {round_info['duration_min']} {t('target_duration', lang)} | 
                        🎯 {focus_text}
                    </span>
                </div>
                """, unsafe_allow_html=True)
        
        if st.button(t("target_confirm_btn", lang), use_container_width=True):
            st.session_state.target["company"] = company
            st.session_state.target["role"] = role
            st.session_state.target["level"] = level
            st.session_state.current_step = 3
            st.rerun()
    
    elif page_index == 3:  # JD
        st.markdown(f"## {t('jd_title', lang)}")
        
        # URL Input
        jd_url = st.text_input("🔗 Import from URL", placeholder="https://www.linkedin.com/jobs/...")
        
        if st.button("Fetch URL"):
            if jd_url:
                from components.utils import fetch_url_content
                with st.spinner("Fetching content..."):
                    fetched_text = fetch_url_content(jd_url)
                    if not fetched_text.startswith("Error"):
                        st.session_state.target["jd_text"] = fetched_text
                        st.success("Content fetched successfully!")
                    else:
                        st.error(fetched_text)
        
        jd_text = st.text_area(
            t("jd_label", lang),
            value=st.session_state.target.get("jd_text", ""),
            height=400,
            placeholder=t("jd_placeholder", lang)
        )
        
        if st.button(t("jd_analyze_btn", lang), use_container_width=True):
            if jd_text.strip():
                st.session_state.target["jd_text"] = jd_text
                from components.skill_extractor import extract_skills
                jd_skills = extract_skills(jd_text, st.session_state.skills_taxonomy)
                st.session_state.target["jd_skills"] = jd_skills
                st.session_state.current_step = 4
                st.success(t("jd_success", lang).format(len(jd_skills)))
                st.rerun()
            else:
                st.error(t("jd_error", lang))
    
    elif page_index == 4:  # Gap Analysis
        st.markdown(f"## {t('analysis_title', lang)}")
        
        resume_skills = set(st.session_state.user_profile.get("extracted_skills", []))
        jd_skills = set(st.session_state.target.get("jd_skills", []))
        
        if not resume_skills or not jd_skills:
            st.warning(t("analysis_warning", lang))
        else:
            gaps = jd_skills - resume_skills
            strengths = resume_skills & jd_skills
            extra = resume_skills - jd_skills
            
            st.session_state.analysis["gaps"] = list(gaps)
            st.session_state.analysis["strengths"] = list(strengths)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"### {t('analysis_gaps', lang)}")
                for skill in sorted(gaps):
                    st.markdown(f"- {skill}")
            
            with col2:
                st.markdown(f"### {t('analysis_strengths', lang)}")
                for skill in sorted(strengths):
                    st.markdown(f"- ✅ {skill}")
            
            with col3:
                st.markdown(f"### {t('analysis_extra', lang)}")
                for skill in sorted(extra):
                    st.markdown(f"- {skill}")
            
            if st.button(t("analysis_generate_btn", lang), use_container_width=True):
                st.session_state.current_step = 5
                st.rerun()
    
    elif page_index == 5:  # Study Plan
        st.markdown(f"## {t('plan_title', lang)}")
        
        gaps = st.session_state.analysis.get("gaps", [])
        
        if not gaps:
            st.info(t("plan_no_gaps", lang))
        else:
            # Generate study plan
            st.markdown(f"### {t('plan_phases', lang)}")
            
            # Phase 1: Gap filling
            with st.expander(t("plan_phase1", lang), expanded=True):
                for i, skill in enumerate(gaps):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.checkbox(t("plan_learn", lang).format(skill), key=f"gap_{i}")
                    with col2:
                        st.markdown(f"[{t('plan_search', lang)}](https://www.google.com/search?q={skill}+tutorial)")
            
            # Phase 2: Coding
            with st.expander(t("plan_phase2", lang)):
                st.markdown("""
                - [ ] LeetCode Medium x 50
                - [ ] LeetCode Hard x 20  
                - [ ] Company Tagged Questions
                """)
            
            # Phase 3: System Design
            with st.expander(t("plan_phase3", lang)):
                st.markdown("""
                - [ ] Recommendation System Design
                - [ ] Search & Ranking System
                - [ ] Ad System Design
                - [ ] Content Moderation System
                """)
            
            # Phase 4: Behavioral
            with st.expander(t("plan_phase4", lang)):
                st.markdown("""
                - [ ] STAR Stories x 10
                - [ ] Resume Deep Dive
                - [ ] Mock Interviews
                """)
    
    elif page_index == 6:  # Interview Questions
        from components.interview_questions import render_interview_questions
        render_interview_questions()
    
    elif page_index == 7:  # Mock Interview
        from components.mock_interview import render_mock_interview
        render_mock_interview()
    
    elif page_index == 8:  # Job Match
        from components.job_matching import render_job_matching
        render_job_matching()
    
    elif page_index == 9:  # Resources
        from components.tech_resources import render_tech_resources
        render_tech_resources()
    
    elif page_index == 10:  # Community
        from components.community_qa import render_community_qa
        render_community_qa()
    
    elif page_index == 11:  # Profile
        from components.user_profile import render_user_profile
        render_user_profile()
    
    elif page_index == 12:  # Notifications
        from components.notification_settings import render_notification_settings
        render_notification_settings()


if __name__ == "__main__":
    main()
