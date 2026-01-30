"""
Mock Interview UI Component
Interactive chat interface for AI mock interviews
"""
import streamlit as st
import sys
from pathlib import Path
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from data.mock_interview import mock_interview_manager, InterviewSession
from components.i18n import t

def render_setup_page():
    """Render interview setup page."""
    st.markdown("## 🤖 AI 模拟面试")
    st.markdown("选择你的面试配置，AI 将根据目标公司风格进行模拟。")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Load companies if available
        companies = st.session_state.companies.get("companies", [])
        company_names = [c["name"] for c in companies] if companies else ["Google", "Amazon", "Meta", "Microsoft", "Startup"]
        
        target_company = st.selectbox("目标公司", company_names)
        interview_type = st.selectbox("面试类型", ["behavioral", "technical (Coming Soon)"])
    
    with col2:
        level = st.selectbox("目标级别", ["L3/Junior", "L4/Mid-Level", "L5/Senior", "L6/Staff"])
        
    start_btn = st.button("🚀 开始面试", type="primary", use_container_width=True)
    
    if start_btn:
        # Initialize session
        if interview_type == "behavioral":
            session = mock_interview_manager.create_session("behavioral", target_company, level)
            st.session_state.mock_interview_session = session
            
            # Initial greeting from AI
            with st.spinner("面试官正在准备..."):
                mock_interview_manager.send_message(session, "Hi, I'm ready for the interview.")
            
            st.rerun()
        else:
            st.warning("技术面试功能即将上线！")

def render_chat_page():
    """Render active interview chat interface."""
    session = st.session_state.mock_interview_session
    
    st.markdown(f"### 🎙️ {session.target_company} {session.interview_type.capitalize()} Interview")
    st.caption(f"Level: {session.level} | Status: In Progress")
    
    # End interview button in sidebar
    with st.sidebar:
        st.markdown("### 控制台")
        if st.button("🏁 结束面试", type="primary"):
            with st.spinner("AI 正在生成面试反馈..."):
                feedback = mock_interview_manager.generate_feedback(session)
                session.feedback = feedback
                session.status = "completed"
                st.rerun()
    
    # Display chat history (skipping the system setup messages)
    for msg in session.messages:
        # Use different avatars
        avatar = "🤖" if msg["role"] == "model" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])
            
    # Chat input
    if prompt := st.chat_input("输入你的回答..."):
        # Display user message
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        
        # Determine strictness/follow-up probability based on company
        # (This is handled by the backend logic, but we could add UI effects here)
        
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("面试官正在记录并思考..."):
                response = mock_interview_manager.send_message(session, prompt)
                st.markdown(response)

def render_feedback_page():
    """Render interview feedback."""
    session = st.session_state.mock_interview_session
    feedback = session.feedback
    
    st.markdown("## 📊 面试反馈报告")
    
    if not feedback:
        st.error("无法生成反馈报告")
        if st.button("返回"):
            del st.session_state.mock_interview_session
            st.rerun()
        return

    # Handle raw text case if JSON parsing failed
    if "raw_feedback" in feedback:
        st.markdown(feedback["raw_feedback"])
    else:
        # Score card
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("综合评分", f"{feedback.get('score', 0)}/10")
        with col2:
            st.metric("结果判定", feedback.get('verdict', 'N/A'))
        with col3:
            st.metric("STAR应用", feedback.get('star_analysis', 'N/A')[:20]+"...")

        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ✅ 优势 (Strengths)")
            for item in feedback.get("strengths", []):
                st.success(f"**{item}**")
                
        with col2:
            st.markdown("### ⚠️ 改进建议 (Improvements)")
            for item in feedback.get("improvements", []):
                st.warning(f"**{item}**")
                
        st.markdown("### 📝 详细 STAR 分析")
        st.info(feedback.get("star_analysis", "无详细分析"))
        
    st.markdown("---")
    if st.button("开始新的面试"):
        del st.session_state.mock_interview_session
        st.rerun()

def render_mock_interview():
    """Main render function."""
    if "mock_interview_session" not in st.session_state:
        render_setup_page()
    elif st.session_state.mock_interview_session.status == "active":
        render_chat_page()
    else:
        render_feedback_page()
