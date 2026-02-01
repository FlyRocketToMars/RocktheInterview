"""
Interview Trends Component
Displays latest MLE interview trends by domain
"""
import streamlit as st
import json
from pathlib import Path


def load_trends_data():
    """Load interview trends data."""
    data_file = Path(__file__).parent.parent.parent / "data" / "interview_trends_2026.json"
    
    try:
        with open(data_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"无法加载趋势数据: {e}")
        return None


def render_heat_indicator(heat: int) -> str:
    """Render heat level as fire emojis."""
    return "🔥" * heat + "⚪" * (5 - heat)


def render_interview_trends():
    """Render the interview trends page."""
    
    st.markdown("## 📈 2026 面试趋势")
    st.markdown("*基于最新面试数据，了解各方向考察重点*")
    
    data = load_trends_data()
    if not data:
        return
    
    # Overview section
    overview = data.get("trends_overview", {})
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1e3a5f 0%, #2d1b4e 100%); 
                padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem;">
        <h3 style="margin: 0; color: #60a5fa;">📊 {overview.get('title', '')}</h3>
        <p style="color: #e2e8f0; margin: 1rem 0;">
            {overview.get('summary', '')}
        </p>
        <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 1rem;">
            <span style="color: #22d3ee;">🔥 热门:</span>
            {"".join([f'<span style="background: rgba(34, 211, 238, 0.2); padding: 0.25rem 0.75rem; border-radius: 20px; color: #22d3ee; font-size: 0.85rem;">{t}</span>' for t in overview.get('hot_topics', [])])}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Domain tabs
    trends_by_domain = data.get("trends_by_domain", {})
    
    domain_names = [f"{v['icon']} {v['name']}" for v in trends_by_domain.values()]
    domain_keys = list(trends_by_domain.keys())
    
    tabs = st.tabs(domain_names)
    
    for i, (domain_key, domain_data) in enumerate(trends_by_domain.items()):
        with tabs[i]:
            render_domain_trends(domain_data)
    
    # Company specific section
    st.markdown("---")
    st.markdown("### 🏢 公司特定趋势")
    
    company_trends = data.get("company_specific_trends", {})
    
    cols = st.columns(len(company_trends))
    for i, (company_key, company_data) in enumerate(company_trends.items()):
        with cols[i]:
            render_company_card(company_data)
    
    # Salary trends
    st.markdown("---")
    st.markdown("### 💰 薪资趋势参考")
    
    salary = data.get("salary_trends", {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**典型薪资范围 (US, E5/L5 级别):**")
        for role, range_str in salary.get("ranges", {}).items():
            st.markdown(f"- **{role}**: {range_str}")
    
    with col2:
        st.markdown("**趋势洞察:**")
        for trend in salary.get("trends", []):
            st.markdown(f"- {trend}")


def render_domain_trends(domain_data: dict):
    """Render trends for a specific domain."""
    
    # Header with heat indicator
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"### {domain_data.get('icon', '')} {domain_data.get('name', '')}")
    
    with col2:
        heat = domain_data.get('heat', 3)
        st.markdown(f"**热度:** {render_heat_indicator(heat)}")
    
    with col3:
        weight = domain_data.get('weight_in_interview', 'N/A')
        st.markdown(f"**面试占比:** {weight}")
    
    # Summary
    st.info(f"📌 {domain_data.get('summary', '')}")
    
    # Hot topics
    for topic_data in domain_data.get("hot_topics", []):
        with st.expander(f"🔥 {topic_data.get('topic', '')} ({topic_data.get('frequency', '')} 频率)", expanded=False):
            
            # Companies
            companies = topic_data.get("companies", [])
            st.markdown(f"**常见公司:** {', '.join(companies)}")
            
            # Key points
            st.markdown("**考点:**")
            for point in topic_data.get("key_points", []):
                st.markdown(f"- {point}")
            
            # Sample questions
            st.markdown("**示例问题:**")
            for q in topic_data.get("sample_questions", []):
                st.markdown(f"- 💬 *{q}*")
    
    # Preparation tips
    with st.expander("💡 备考建议", expanded=True):
        for tip in domain_data.get("preparation_tips", []):
            st.markdown(f"✅ {tip}")


def render_company_card(company_data: dict):
    """Render a company-specific trends card."""
    
    st.markdown(f"""
    <div style="background: #1e293b; padding: 1rem; border-radius: 12px; height: 100%;">
        <h4 style="color: #60a5fa; margin: 0 0 0.5rem 0;">{company_data.get('name', '')}</h4>
        <p style="color: #94a3b8; font-size: 0.85rem; margin: 0;">
            <strong>重点:</strong> {', '.join(company_data.get('focus_areas', [])[:2])}
        </p>
        <p style="color: #64748b; font-size: 0.8rem; margin-top: 0.5rem;">
            最新变化: {company_data.get('recent_changes', ['N/A'])[0][:30]}...
        </p>
    </div>
    """, unsafe_allow_html=True)


# Quick summary for home page
def render_trends_summary():
    """Render a brief trends summary for the home page."""
    
    data = load_trends_data()
    if not data:
        return
    
    st.markdown("### 📈 2026 面试热点")
    
    overview = data.get("trends_overview", {})
    hot_topics = overview.get("hot_topics", [])[:5]
    
    cols = st.columns(5)
    for i, topic in enumerate(hot_topics):
        with cols[i]:
            st.markdown(f"""
            <div style="text-align: center; padding: 0.5rem; background: rgba(34, 211, 238, 0.1); 
                        border-radius: 8px; border: 1px solid rgba(34, 211, 238, 0.3);">
                <span style="font-size: 0.8rem; color: #22d3ee;">{topic}</span>
            </div>
            """, unsafe_allow_html=True)
