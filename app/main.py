"""
MLE Interview Prep Platform
Main Streamlit Application Entry Point
"""
import streamlit as st
import json
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

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
    
    /* ========== MOBILE RESPONSIVE ========== */
    
    /* Mobile breakpoint: < 768px */
    @media (max-width: 768px) {
        /* Adjust main container padding */
        .main .block-container {
            padding: 1rem 0.5rem !important;
            max-width: 100% !important;
        }
        
        /* Stack columns vertically on mobile */
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
        }
        
        /* Smaller headers on mobile */
        h1 {
            font-size: 1.5rem !important;
        }
        h2 {
            font-size: 1.25rem !important;
        }
        h3 {
            font-size: 1.1rem !important;
        }
        
        /* Smaller metrics on mobile */
        [data-testid="stMetricValue"] {
            font-size: 1.5rem !important;
        }
        
        /* Adjust button size */
        .stButton > button {
            padding: 0.5rem 1rem;
            font-size: 0.9rem;
        }
        
        /* Compact tabs on mobile */
        .stTabs [data-baseweb="tab"] {
            padding: 8px 12px;
            font-size: 0.85rem;
        }
        
        /* Sidebar auto-collapse on mobile */
        [data-testid="stSidebar"] {
            min-width: 0 !important;
        }
        
        [data-testid="stSidebar"][aria-expanded="false"] {
            min-width: 0 !important;
            width: 0 !important;
        }
        
        /* Full-width cards */
        .card {
            padding: 1rem;
            margin: 0.5rem 0;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            font-size: 0.9rem !important;
        }
        
        /* Table scrolling on mobile */
        .stDataFrame {
            overflow-x: auto;
        }
        
        /* Radio buttons vertical */
        [data-testid="stRadio"] > div {
            flex-direction: column !important;
        }
    }
    
    /* Tablet breakpoint: 768px - 1024px */
    @media (min-width: 768px) and (max-width: 1024px) {
        .main .block-container {
            padding: 1.5rem 1rem !important;
        }
        
        h1 {
            font-size: 1.75rem !important;
        }
        
        [data-testid="stMetricValue"] {
            font-size: 2rem !important;
        }
    }
    
    /* Touch-friendly elements */
    @media (pointer: coarse) {
        /* Larger touch targets */
        .stButton > button {
            min-height: 44px;
        }
        
        .stCheckbox, .stRadio {
            padding: 0.5rem 0;
        }
        
        /* Increase spacing between interactive elements */
        [data-testid="stVerticalBlock"] > div {
            margin-bottom: 0.75rem;
        }
    }
    
    /* Landscape phone optimization */
    @media (max-height: 500px) and (orientation: landscape) {
        .main .block-container {
            padding: 0.5rem !important;
        }
    }
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
            t("nav_daily", lang),
            t("nav_setup", lang),
            t("nav_questions", lang),
            t("nav_mock", lang),
            t("nav_community", lang),
            t("nav_profile", lang),
        ]
        
        page = st.radio(
            t("nav_select", lang),
            nav_options,
            label_visibility="collapsed",
            key="nav_selection"
        )
        
        st.markdown("---")
        st.markdown(f"### {t('sidebar_stats', lang)}")
        
        from data.daily_learning import daily_learning
        user_data = daily_learning.get_user_profile(user_email)
        if user_data and "profile" in user_data:
            profile = user_data["profile"]
            progress = user_data.get("progress", {})
            company = profile.get("target_company", "N/A")
            role = profile.get("target_role", "")
            level = profile.get("target_level", "")
            streak = progress.get("streak_days", 0)
            mins = progress.get("total_study_minutes", 0)
            
            st.markdown(f"""
            <div style="background: #1e293b; padding: 12px; border-radius: 12px; border-left: 4px solid #3b82f6; margin-bottom: 12px;">
                <p style="margin: 0; color: #94a3b8; font-size: 0.8rem;">🎯 Target / 目标定位</p>
                <p style="margin: 4px 0 0 0; color: #f8fafc; font-weight: bold; font-size: 1.1rem;">
                    {company} <span style="font-size: 0.9rem; color: #94a3b8; font-weight: normal;">| {role}</span>
                </p>
                <p style="margin: 2px 0 0 0; color: #64748b; font-size: 0.8rem;">{level}</p>
            </div>
            
            <div style="display: flex; gap: 10px;">
                <div style="flex: 1; background: #1e293b; padding: 12px; border-radius: 12px; border-left: 4px solid #f59e0b;">
                    <p style="margin: 0; color: #94a3b8; font-size: 0.75rem;">🔥 Streak</p>
                    <p style="margin: 4px 0 0 0; color: #f8fafc; font-weight: bold; font-size: 1rem;">
                        {streak} Days
                    </p>
                </div>
                <div style="flex: 1; background: #1e293b; padding: 12px; border-radius: 12px; border-left: 4px solid #10b981;">
                    <p style="margin: 0; color: #94a3b8; font-size: 0.75rem;">⏱️ Study</p>
                    <p style="margin: 4px 0 0 0; color: #f8fafc; font-weight: bold; font-size: 1rem;">
                        {mins // 60} h
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("🎯 Please go to 'Target & Setup' to set your goal.")
        
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
            st.session_state.nav_selection = t("nav_setup", lang)
            st.session_state.current_step = 1
            
        st.button(t("home_start_btn", lang), 
                 use_container_width=True, 
                 on_click=start_prep)
    
    elif page_index == 1:  # Daily Dashboard - TODAY'S STUDY PLAN
        from components.daily_dashboard import render_daily_dashboard
        render_daily_dashboard()
    
    elif page_index == 2:  # Target & Setup (Consolidated)
        # Tabbed interface for Target and Setup
        setup_tabs = st.tabs([
            t("nav_resume", lang), 
            t("nav_target", lang), 
            t("nav_jd", lang), 
            t("nav_analysis", lang), 
            t("nav_plan", lang)
        ])
        
        with setup_tabs[0]: # Resume
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
            
            def extract_skills_only():
                if resume_text.strip():
                    st.session_state.user_profile["resume_text"] = resume_text
                    from components.skill_extractor import extract_skills
                    extracted = extract_skills(resume_text, st.session_state.skills_taxonomy)
                    st.session_state.user_profile["extracted_skills"] = extracted
                    st.session_state.extract_success = len(extracted)
                else:
                    st.session_state.extract_error = True
            
            st.button(t("resume_extract_btn", lang), use_container_width=True, on_click=extract_skills_only)
            
            # Show success/error messages
            if st.session_state.get("extract_success"):
                st.success(t("resume_success", lang).format(st.session_state.extract_success))
                del st.session_state.extract_success
            if st.session_state.get("extract_error"):
                st.error(t("resume_error", lang))
                del st.session_state.extract_error

        with setup_tabs[1]: # Target
            st.markdown(f"## {t('target_title', lang)}")
            
            companies_data = st.session_state.companies.get("companies", [])
            role_descriptions = st.session_state.companies.get("role_descriptions", {})
            company_names = [c["name"] for c in companies_data]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                companies = st.multiselect(t("target_company", lang), company_names, default=[company_names[0]] if company_names else None)
            
            # Get selected company data (use first selected for previewing roles/levels)
            selected_company_name = companies[0] if companies else None
            selected_company = next((c for c in companies_data if c["name"] == selected_company_name), None)
            
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
                st.session_state.target["companies"] = companies
                if companies:
                    st.session_state.target["company"] = companies[0]
                else:
                    st.session_state.target["company"] = "全部"
                st.session_state.target["role"] = role
                st.session_state.target["level"] = level
                
                # Fetch profile and update
                from components.auth import get_current_user
                from data.daily_learning import daily_learning
                user_email = get_current_user()
                if user_email:
                    daily_learning.setup_user_profile(user_email, {
                        "target_companies": companies,
                        "target_company": companies[0] if companies else "全部",
                        "target_role": role,
                        "target_level": level,
                    })
                
                st.success("Target Confirmed!")

        with setup_tabs[2]: # JD
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
            
            # File Upload
            st.markdown("---")
            uploaded_jd = st.file_uploader("📎 Upload Job Description (PDF/TXT)", type=["pdf", "txt"])
            
            if uploaded_jd is not None:
                if uploaded_jd.name.endswith(".pdf"):
                    from components.utils import parse_pdf
                    with st.spinner("Parsing PDF..."):
                        pdf_text = parse_pdf(uploaded_jd.getvalue())
                        if pdf_text and not pdf_text.startswith("Error"):
                             st.session_state.target["jd_text"] = pdf_text
                             st.success("PDF loaded successfully! You can edit the text below if needed.")
                        else:
                            st.error(f"Failed to parse PDF: {pdf_text}")
                elif uploaded_jd.name.endswith(".txt"):
                    text_content = uploaded_jd.getvalue().decode("utf-8")
                    st.session_state.target["jd_text"] = text_content
                    st.success("Text file loaded successfully!")
            
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
                    st.success(t("jd_success", lang).format(len(jd_skills)))
                else:
                    st.error(t("jd_error", lang))

        with setup_tabs[3]: # Analysis
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

        with setup_tabs[4]: # Plan
            from components.learning_plan import render_learning_plan
            render_learning_plan()

    elif page_index == 3:  # 🎯 题库练习 (Includes Trends, Questions, Jobs)
        question_tabs = st.tabs([
            t("nav_questions", lang), 
            t("nav_trends", lang),
            t("nav_jobs", lang)
        ])
        
        with question_tabs[0]:
            from components.interview_questions import render_interview_questions
            render_interview_questions()
            
        with question_tabs[1]:
            from components.interview_trends import render_interview_trends
            render_interview_trends()
            
        with question_tabs[2]:
            from components.job_matching import render_job_matching
            render_job_matching()
    
    elif page_index == 4:  # 🎤 AI模拟面试
        from components.mock_interview import render_mock_interview
        render_mock_interview()
    
    elif page_index == 5:  # 💬 社区与资源 (Includes Community, Resources, Papers)
        community_tabs = st.tabs([
            t("nav_community", lang),
            t("nav_resources", lang),
            t("nav_papers", lang),
            "📖 故事库"
        ])
        
        with community_tabs[0]:
            from components.community_qa import render_community_qa
            render_community_qa()
            
        with community_tabs[1]:
            from components.tech_resources import render_tech_resources
            render_tech_resources()
            
        with community_tabs[2]:
            from components.paper_reading import render_paper_reading
            render_paper_reading()
        
        with community_tabs[3]:
            from components.story_bank import render_story_bank
            render_story_bank()
    
    elif page_index == 6:  # 👤 个人中心与设置 (Includes Profile, Notifications)
        profile_tabs = st.tabs([
            t("nav_profile", lang),
            t("nav_notifications", lang)
        ])
        
        with profile_tabs[0]:
            from components.user_profile import render_user_profile
            render_user_profile()
            
        with profile_tabs[1]:
            from components.notification_settings import render_notification_settings
            render_notification_settings()


if __name__ == "__main__":
    main()
