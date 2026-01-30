"""
Job Matching Component
Browse job listings and match with resume using Gemini AI
"""
import streamlit as st
import json
import sys
from pathlib import Path
from typing import Dict, List
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from data.job_aggregator import job_aggregator, GeminiClassifier
from data.job_feeds import job_feeds, get_custom_search


def load_resume() -> str:
    """Load user's resume from session state."""
    return st.session_state.get("resume_text", "")


def render_daily_jobs():
    """Render daily job listings section."""
    
    st.markdown("### 📅 每日新职位")
    st.markdown(f"*{datetime.now().strftime('%Y年%m月%d日')} - 点击链接查看最新 MLE 职位*")
    
    # Custom search
    st.markdown("#### 🔍 自定义搜索")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        keywords = st.text_input("职位关键词", value="Machine Learning Engineer", key="job_keywords")
    with col2:
        location = st.text_input("地点 (可选)", placeholder="例如: San Francisco", key="job_location")
    with col3:
        remote_only = st.checkbox("仅远程", key="job_remote")
    
    if keywords:
        col1, col2, col3 = st.columns(3)
        with col1:
            linkedin_url = get_custom_search(keywords, "linkedin", location, remote_only)
            st.markdown(f"[🔗 LinkedIn 搜索]({linkedin_url})")
        with col2:
            indeed_url = get_custom_search(keywords, "indeed", location, remote_only)
            st.markdown(f"[🔗 Indeed 搜索]({indeed_url})")
        with col3:
            glassdoor_url = get_custom_search(keywords, "glassdoor", location, remote_only)
            st.markdown(f"[🔗 Glassdoor 搜索]({glassdoor_url})")
    
    st.markdown("---")
    
    # Specialized searches
    st.markdown("#### 🎯 按专业领域")
    
    specialized = job_feeds.get_specialized_searches()
    
    cols = st.columns(4)
    for i, (key, search) in enumerate(specialized.items()):
        with cols[i % 4]:
            st.markdown(f"**{search['name']}**")
            st.markdown(f"[LinkedIn]({search.get('linkedin', '#')}) | [Indeed]({search.get('indeed', '#')})")
    
    st.markdown("---")
    
    # Job platforms - today's jobs
    st.markdown("#### 💼 求职平台 (最近24小时)")
    
    platforms = job_feeds.get_platform_links()
    
    cols = st.columns(3)
    for i, (key, platform) in enumerate(platforms.items()):
        with cols[i % 3]:
            st.markdown(f"{platform['icon']} **[{platform['name']}]({platform['mle_search']})**")
    
    st.markdown("---")
    
    # Company career pages
    st.markdown("#### 🏢 公司招聘页面 (直达链接)")
    st.caption("点击直接跳转到各公司 MLE 职位搜索结果")
    
    companies = job_feeds.get_company_links()
    
    # Group by tier
    tier1_keys = ["google", "meta", "amazon", "microsoft", "apple", "openai"]
    tier2_keys = ["anthropic", "nvidia", "netflix", "bytedance", "stripe", "uber"]
    tier3_keys = ["airbnb", "spotify", "databricks"]
    
    st.markdown("**🔥 顶级科技公司**")
    cols = st.columns(6)
    for i, key in enumerate(tier1_keys):
        if key in companies:
            company = companies[key]
            with cols[i]:
                st.markdown(f"{company['icon']} [{company['name']}]({company['url']})")
    
    st.markdown("**🚀 热门 AI 公司**")
    cols = st.columns(6)
    for i, key in enumerate(tier2_keys):
        if key in companies:
            company = companies[key]
            with cols[i]:
                st.markdown(f"{company['icon']} [{company['name']}]({company['url']})")
    
    st.markdown("**⭐ 其他优质公司**")
    cols = st.columns(6)
    for i, key in enumerate(tier3_keys):
        if key in companies:
            company = companies[key]
            with cols[i]:
                st.markdown(f"{company['icon']} [{company['name']}]({company['url']})")
    
    # Tips
    st.markdown("---")
    st.markdown("#### 💡 求职小贴士")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **🎯 高效求职策略:**
        - LinkedIn 设置「Open to Work」
        - 每天查看 LinkedIn 24h 内新职位
        - 投递后主动联系 Recruiter
        - 准备好 1-page resume
        """)
    with col2:
        st.markdown("""
        **📊 薪酬研究:**
        - [levels.fyi](https://www.levels.fyi/) - 详细薪酬数据
        - [Glassdoor](https://www.glassdoor.com/) - 公司评价 + 面试经验
        - [Blind](https://www.teamblind.com/) - 匿名讨论
        - [一亩三分地](https://www.1point3acres.com/) - 华人求职社区
        """)




def render_job_matching():
    """Render the job matching page."""
    
    st.markdown("## 💼 职位匹配中心")
    st.markdown("*AI 驱动的职位推荐和简历匹配*")
    
    # Legal disclaimer
    st.info("""
    ⚠️ **免责声明**: 本页面提供的是各公司**官方招聘页面链接**，不抓取或存储任何公司的职位数据。
    点击链接将跳转到官方招聘网站查看最新职位。
    """)
    
    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📅 每日新职位", "🎯 JD匹配", "🏢 公司招聘", "📊 自定义JD", "🔗 招聘链接"])
    
    # ============ Tab 1: Daily New Jobs ============
    with tab1:
        render_daily_jobs()
    
    # ============ Tab 2: Resume Matching ============
    with tab2:
        st.markdown("### 🎯 简历-职位智能匹配")
        st.info("💡 上传或粘贴简历，AI 会为你推荐最匹配的职位")
        
        # Get resume from session or allow input
        resume_text = load_resume()
        
        if not resume_text:
            st.warning("⚠️ 未检测到简历。请在「输入简历」页面上传简历，或在下方粘贴。")
            resume_text = st.text_area(
                "粘贴简历内容",
                height=200,
                placeholder="粘贴你的简历文本..."
            )
        else:
            st.success(f"✅ 已加载简历 ({len(resume_text)} 字符)")
            with st.expander("预览简历"):
                st.text(resume_text[:1000] + "..." if len(resume_text) > 1000 else resume_text)
        
        if resume_text and st.button("🔍 开始匹配", type="primary"):
            with st.spinner("🤖 Gemini AI 正在分析匹配度..."):
                matched_jobs = job_aggregator.match_resume(resume_text)
            
            st.markdown("### 📊 匹配结果")
            st.markdown(f"*共分析 {len(matched_jobs)} 个职位*")
            
            for i, job in enumerate(matched_jobs[:10]):
                score = job.get("match_score", 0)
                score_pct = int(score * 100)
                
                # Color based on score
                if score_pct >= 70:
                    score_color = "🟢"
                elif score_pct >= 50:
                    score_color = "🟡"
                else:
                    score_color = "🔴"
                
                with st.expander(f"{score_color} **{job['title']}** @ {job['company']} - 匹配度: {score_pct}%"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**📍 地点**: {job.get('location', 'N/A')}")
                        st.markdown(f"**📊 级别**: {job.get('level', 'N/A')}")
                        st.markdown(f"**💰 薪资**: {job.get('salary_range', 'N/A')}")
                        st.markdown(f"**🏠 远程**: {'是' if job.get('remote') else '否'}")
                        
                        if job.get("categories"):
                            cats = " ".join([f"`{c}`" for c in job["categories"]])
                            st.markdown(f"**🏷️ 分类**: {cats}")
                    
                    with col2:
                        # Match score gauge
                        st.metric("匹配度", f"{score_pct}%")
                        st.markdown(f"[🔗 申请职位]({job.get('url', '#')})")
                    
                    st.markdown("**📋 要求:**")
                    for req in job.get("requirements", []):
                        st.markdown(f"- {req}")
    
    # ============ Tab 3: Jobs by Company ============
    with tab3:
        st.markdown("### 🏢 按公司浏览")
        
        companies = job_aggregator.get_all_companies()
        company_names = {k: v["name"] for k, v in companies.items()}
        
        selected_company = st.selectbox(
            "选择公司",
            list(company_names.keys()),
            format_func=lambda x: company_names.get(x, x)
        )
        
        if selected_company:
            company_info = companies[selected_company]
            
            st.markdown(f"#### {company_info['name']}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"🔗 [官方招聘页面]({company_info.get('careers_url', '#')})")
            with col2:
                st.markdown(f"💰 [薪酬数据 (levels.fyi)]({company_info.get('levels_url', '#')})")
            
            st.markdown("---")
            
            # Get jobs for this company
            company_jobs = job_aggregator.get_jobs({"company": company_info["name"]})
            
            if company_jobs:
                st.markdown(f"*共 {len(company_jobs)} 个职位*")
                
                for job in company_jobs:
                    with st.container():
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            st.markdown(f"**{job['title']}**")
                            st.caption(f"📍 {job.get('location', 'N/A')} | 💰 {job.get('salary_range', 'N/A')}")
                        
                        with col2:
                            st.markdown(f"`{job.get('level', 'N/A')}`")
                        
                        with col3:
                            st.markdown(f"[申请]({job.get('url', '#')})")
                        
                        st.markdown("---")
            else:
                st.info("暂无该公司职位数据。点击上方链接访问官方招聘页面。")
    
    # ============ Tab 4: Custom JD Matching ============
    with tab4:
        st.markdown("### 📝 自定义 JD 匹配")
        st.markdown("*粘贴感兴趣的职位描述，AI 分析匹配度*")
        
        st.info("💡 从公司官网复制职位描述，粘贴到下方，分析与你简历的匹配度")
        
        # Get resume
        resume_text = load_resume()
        
        if not resume_text:
            st.warning("⚠️ 请先在「输入简历」页面上传简历")
        
        # JD input
        custom_jd = st.text_area(
            "粘贴职位描述 (JD)",
            height=300,
            placeholder="从公司官网复制职位描述粘贴到这里..."
        )
        
        col1, col2 = st.columns(2)
        with col1:
            jd_company = st.text_input("公司名称", placeholder="例如: Google")
        with col2:
            jd_title = st.text_input("职位名称", placeholder="例如: Senior MLE")
        
        if custom_jd and resume_text and st.button("🔍 分析匹配度", type="primary"):
            with st.spinner("🤖 Gemini AI 正在分析..."):
                classifier = GeminiClassifier()
                
                # Create job dict
                job = {
                    "title": jd_title or "自定义职位",
                    "company": jd_company or "未知公司",
                    "description": custom_jd,
                    "requirements": []
                }
                
                # Classify the JD
                classification = classifier.classify_job(job)
                
                # Match with resume
                match_score = classifier.match_resume_to_job(resume_text, job)
            
            st.markdown("### 📊 分析结果")
            
            # Display results
            col1, col2 = st.columns([1, 2])
            
            with col1:
                score_pct = int(match_score * 100)
                if score_pct >= 70:
                    st.success(f"🎯 匹配度: **{score_pct}%**")
                elif score_pct >= 50:
                    st.warning(f"⚠️ 匹配度: **{score_pct}%**")
                else:
                    st.error(f"❌ 匹配度: **{score_pct}%**")
            
            with col2:
                st.markdown(f"**职位级别**: {classification.get('level', 'N/A')}")
                cats = ", ".join(classification.get("categories", []))
                st.markdown(f"**职位分类**: {cats}")
            
            st.markdown("---")
            
            st.markdown("**🛠️ 提取的技能要求:**")
            skills = classification.get("skills_required", [])
            if skills:
                st.markdown(" | ".join([f"`{s}`" for s in skills]))
            
            st.markdown("**💡 建议:**")
            if score_pct >= 70:
                st.markdown("✅ 你的简历与这个职位匹配度很高，建议直接申请！")
            elif score_pct >= 50:
                st.markdown("⚠️ 匹配度中等，建议针对职位要求优化简历后申请。")
            else:
                st.markdown("❌ 匹配度较低，可能需要补充相关技能或经验。")
        
        # Saved JDs
        if "saved_jds" not in st.session_state:
            st.session_state.saved_jds = []
        
        if custom_jd and jd_company and jd_title:
            if st.button("💾 保存此 JD"):
                st.session_state.saved_jds.append({
                    "company": jd_company,
                    "title": jd_title,
                    "description": custom_jd[:500]
                })
                st.success("已保存！")
    
    # ============ Tab 5: Career Links ============
    with tab5:
        st.markdown("### 🔗 招聘直达链接")
        st.markdown("*点击直接跳转到各公司 MLE 招聘页面*")
        
        companies = job_aggregator.get_all_companies()
        
        # Group by tier
        tier1 = ["google", "meta", "amazon", "microsoft", "apple"]
        tier2 = ["openai", "anthropic", "bytedance", "netflix", "nvidia"]
        
        st.markdown("#### 🏢 FAANG+ 大厂")
        cols = st.columns(5)
        for i, company_id in enumerate(tier1):
            if company_id in companies:
                info = companies[company_id]
                with cols[i]:
                    st.markdown(f"**{info['name']}**")
                    st.markdown(f"[招聘]({info.get('careers_url', '#')})")
                    st.markdown(f"[薪酬]({info.get('levels_url', '#')})")
        
        st.markdown("#### 🚀 AI 独角兽 & 热门公司")
        cols = st.columns(5)
        for i, company_id in enumerate(tier2):
            if company_id in companies:
                info = companies[company_id]
                with cols[i]:
                    st.markdown(f"**{info['name']}**")
                    st.markdown(f"[招聘]({info.get('careers_url', '#')})")
                    st.markdown(f"[薪酬]({info.get('levels_url', '#')})")
        
        st.markdown("---")
        st.markdown("#### 📊 综合求职平台")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**通用求职**")
            st.markdown("""
            - [LinkedIn Jobs](https://www.linkedin.com/jobs/)
            - [Indeed](https://www.indeed.com/)
            - [Glassdoor](https://www.glassdoor.com/Job/index.htm)
            """)
        
        with col2:
            st.markdown("**AI/ML 专项**")
            st.markdown("""
            - [AI Jobs](https://aijobs.net/)
            - [ML Jobs List](https://mljobslist.com/)
            - [Hugging Face Jobs](https://huggingface.co/jobs)
            """)
        
        with col3:
            st.markdown("**Startup**")
            st.markdown("""
            - [Y Combinator](https://www.workatastartup.com/)
            - [AngelList](https://angel.co/jobs)
            - [Wellfound](https://wellfound.com/)
            """)
    
    # ============ Stats Section ============
    st.markdown("---")
    st.markdown("### 📈 职位市场概览")
    
    all_jobs = job_aggregator.get_jobs()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("总职位数", len(all_jobs))
    
    with col2:
        remote_count = len([j for j in all_jobs if j.get("remote")])
        st.metric("远程职位", remote_count)
    
    with col3:
        companies_set = set(j.get("company") for j in all_jobs)
        st.metric("覆盖公司", len(companies_set))
    
    with col4:
        # Count categories
        all_cats = []
        for j in all_jobs:
            all_cats.extend(j.get("categories", []))
        st.metric("职位分类", len(set(all_cats)))
