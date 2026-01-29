"""
MLE Interview Prep Platform
Main Streamlit Application Entry Point
"""
import streamlit as st
import json
from pathlib import Path

# Page config - must be first Streamlit command
st.set_page_config(
    page_title="Interview Prep Platform",
    page_icon="🎯",
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
            🎯 Interview Prep Platform
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
        
        if is_guest:
            st.markdown("### 👤 访客模式")
            st.caption("登录后可保存进度")
        else:
            st.markdown(f"### 👋 {user_email}")
        
        if st.button("🚪 退出登录", use_container_width=True):
            logout()
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 🧭 导航")
        
        page = st.radio(
            "选择页面",
            ["🏠 首页", "📄 输入简历", "🎯 选择目标", "📋 输入JD", "📊 Gap分析", "📚 学习计划"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("### 📊 快速统计")
        render_stats()
        
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #64748b; font-size: 0.8rem;">
            Made with ❤️ for Job Seekers
        </div>
        """, unsafe_allow_html=True)
    
    # Main content based on selected page
    if page == "🏠 首页":
        render_hero()
        render_progress_steps()
        
        st.markdown("---")
        
        # Feature cards
        st.markdown("### ✨ 核心功能")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="card">
                <h3>🔍 Gap Analysis</h3>
                <p style="color: #94a3b8;">
                    对比你的简历和目标JD，精准识别需要补齐的技能短板
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="card">
                <h3>🏢 公司定制</h3>
                <p style="color: #94a3b8;">
                    针对Google/Meta/Amazon等公司的面试结构，定制化准备策略
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="card">
                <h3>📚 智能计划</h3>
                <p style="color: #94a3b8;">
                    根据面试日期倒推，生成按轮次组织的学习计划
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Quick start
        st.markdown("### 🚀 快速开始")
        if st.button("开始准备面试 →", use_container_width=True):
            st.session_state.current_step = 1
            st.rerun()
    
    elif page == "📄 输入简历":
        st.markdown("## 📄 输入你的简历")
        st.markdown("粘贴你的简历内容，我们将自动提取技能关键词")
        
        resume_text = st.text_area(
            "简历内容",
            value=st.session_state.user_profile.get("resume_text", ""),
            height=400,
            placeholder="粘贴你的简历内容...\n\n例如:\nSenior Machine Learning Engineer with 5 years of experience...\n\nSkills: PyTorch, TensorFlow, Recommendation Systems..."
        )
        
        if st.button("提取技能 →", use_container_width=True):
            if resume_text.strip():
                st.session_state.user_profile["resume_text"] = resume_text
                # Extract skills (简化版本，使用关键词匹配)
                from components.skill_extractor import extract_skills
                extracted = extract_skills(resume_text, st.session_state.skills_taxonomy)
                st.session_state.user_profile["extracted_skills"] = extracted
                st.session_state.current_step = 2
                st.success(f"成功提取 {len(extracted)} 个技能!")
                st.rerun()
            else:
                st.error("请先输入简历内容")
    
    elif page == "🎯 选择目标":
        st.markdown("## 🎯 选择目标公司和职位")
        
        companies_data = st.session_state.companies.get("companies", [])
        role_descriptions = st.session_state.companies.get("role_descriptions", {})
        company_names = [c["name"] for c in companies_data]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            company = st.selectbox("目标公司", company_names)
        
        # Get selected company data
        selected_company = next((c for c in companies_data if c["name"] == company), None)
        
        with col2:
            # Get available roles for selected company
            available_roles = list(selected_company.get("roles", {}).keys()) if selected_company else []
            role = st.selectbox("目标角色", available_roles, 
                              format_func=lambda x: f"{x} - {role_descriptions.get(x, x)}")
        
        with col3:
            # Get levels for selected role
            role_data = selected_company.get("roles", {}).get(role, {}) if selected_company else {}
            levels = role_data.get("levels", [])
            level = st.selectbox("目标级别", levels)
        
        if selected_company and role and role_data:
            st.markdown("### 📋 面试结构")
            for round_info in role_data.get("interview_rounds", []):
                st.markdown(f"""
                <div class="card">
                    <strong>Round {round_info['round']}: {round_info['name']}</strong>
                    <br>
                    <span style="color: #94a3b8;">
                        ⏱️ {round_info['duration_min']}分钟 | 
                        🎯 {', '.join(round_info['focus'])}
                    </span>
                </div>
                """, unsafe_allow_html=True)
        
        if st.button("确认目标 →", use_container_width=True):
            st.session_state.target["company"] = company
            st.session_state.target["role"] = role
            st.session_state.target["level"] = level
            st.session_state.current_step = 3
            st.rerun()
    
    elif page == "📋 输入JD":
        st.markdown("## 📋 输入职位描述 (JD)")
        
        jd_text = st.text_area(
            "JD内容",
            value=st.session_state.target.get("jd_text", ""),
            height=400,
            placeholder="粘贴职位描述...\n\n例如:\nWe are looking for a Machine Learning Engineer to join our team...\n\nRequirements:\n- 3+ years of experience in ML\n- Experience with PyTorch or TensorFlow..."
        )
        
        if st.button("分析JD →", use_container_width=True):
            if jd_text.strip():
                st.session_state.target["jd_text"] = jd_text
                from components.skill_extractor import extract_skills
                jd_skills = extract_skills(jd_text, st.session_state.skills_taxonomy)
                st.session_state.target["jd_skills"] = jd_skills
                st.session_state.current_step = 4
                st.success(f"从JD中提取 {len(jd_skills)} 个技能要求!")
                st.rerun()
            else:
                st.error("请先输入JD内容")
    
    elif page == "📊 Gap分析":
        st.markdown("## 📊 Gap Analysis")
        
        resume_skills = set(st.session_state.user_profile.get("extracted_skills", []))
        jd_skills = set(st.session_state.target.get("jd_skills", []))
        
        if not resume_skills or not jd_skills:
            st.warning("请先完成简历和JD的输入")
        else:
            gaps = jd_skills - resume_skills
            strengths = resume_skills & jd_skills
            extra = resume_skills - jd_skills
            
            st.session_state.analysis["gaps"] = list(gaps)
            st.session_state.analysis["strengths"] = list(strengths)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### 🔴 需要补齐")
                for skill in sorted(gaps):
                    st.markdown(f"- {skill}")
            
            with col2:
                st.markdown("### 🟢 已具备")
                for skill in sorted(strengths):
                    st.markdown(f"- ✅ {skill}")
            
            with col3:
                st.markdown("### 🔵 额外技能")
                for skill in sorted(extra):
                    st.markdown(f"- {skill}")
            
            if st.button("生成学习计划 →", use_container_width=True):
                st.session_state.current_step = 5
                st.rerun()
    
    elif page == "📚 学习计划":
        st.markdown("## 📚 个性化学习计划")
        
        gaps = st.session_state.analysis.get("gaps", [])
        company = st.session_state.target.get("company")
        
        if not gaps:
            st.info("你没有明显的技能Gap，可以专注于面试模拟练习！")
        else:
            # Generate study plan
            st.markdown("### 📅 学习阶段")
            
            # Phase 1: Gap filling
            with st.expander("📖 阶段1: 技能补齐 (1-2周)", expanded=True):
                for i, skill in enumerate(gaps):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.checkbox(f"学习: {skill}", key=f"gap_{i}")
                    with col2:
                        st.markdown(f"[搜索资料](https://www.google.com/search?q={skill}+tutorial)")
            
            # Phase 2: Coding
            with st.expander("💻 阶段2: Coding练习 (1-2周)"):
                st.markdown("""
                - [ ] LeetCode Medium x 50题
                - [ ] LeetCode Hard x 20题  
                - [ ] 公司Tag题目练习
                """)
            
            # Phase 3: System Design
            with st.expander("🏗️ 阶段3: ML System Design (1周)"):
                st.markdown("""
                - [ ] 推荐系统设计
                - [ ] 搜索排序系统
                - [ ] 广告系统设计
                - [ ] 内容审核系统
                """)
            
            # Phase 4: Behavioral
            with st.expander("🗣️ 阶段4: Behavioral准备 (3-5天)"):
                st.markdown("""
                - [ ] 准备STAR故事 x 10
                - [ ] 简历项目深挖准备
                - [ ] 模拟面试练习
                """)


if __name__ == "__main__":
    main()
