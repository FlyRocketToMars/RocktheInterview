"""
Community Q&A Component
UI for the community question and answer system
"""
import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from data.community_qa import community_qa, CommunityQA
from data.gamification import gamification, award_points, get_profile


def get_username() -> str:
    """Get current user's display name."""
    return st.session_state.get("username", "匿名用户")


def format_time(iso_time: str) -> str:
    """Format ISO time to readable string."""
    try:
        dt = datetime.fromisoformat(iso_time)
        now = datetime.now()
        diff = now - dt
        
        if diff.days > 30:
            return dt.strftime("%Y-%m-%d")
        elif diff.days > 0:
            return f"{diff.days}天前"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600}小时前"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60}分钟前"
        else:
            return "刚刚"
    except:
        return iso_time[:10] if iso_time else ""


def render_question_card(question: dict, show_full: bool = False):
    """Render a question card."""
    q_id = question.get("id", "")
    title = question.get("title", "无标题")
    content = question.get("content", "")
    author = question.get("author", "匿名")
    category = question.get("category", "general")
    created_at = question.get("created_at", "")
    upvotes = question.get("upvotes", 0)
    views = question.get("views", 0)
    answers_count = len(question.get("answers", [])) + (1 if question.get("ai_answer") else 0)
    tags = question.get("tags", [])
    
    category_name = CommunityQA.CATEGORIES.get(category, "❓ 其他")
    
    with st.container():
        # Header row
        col1, col2, col3 = st.columns([1, 6, 2])
        
        with col1:
            st.markdown(f"""
            <div style="text-align: center; padding: 10px;">
                <div style="font-size: 1.5em; font-weight: bold;">{upvotes}</div>
                <div style="font-size: 0.8em; color: #888;">👍 赞</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if show_full:
                st.markdown(f"### {title}")
            else:
                if st.button(f"📌 {title}", key=f"q_{q_id}"):
                    st.session_state.viewing_question = q_id
                    st.rerun()
            
            st.caption(f"{category_name} | 👤 {author} | 🕐 {format_time(created_at)}")
            
            if not show_full:
                st.caption(content[:150] + "..." if len(content) > 150 else content)
            
            if tags:
                tags_html = " ".join([f"`{tag}`" for tag in tags[:5]])
                st.markdown(tags_html)
        
        with col3:
            st.markdown(f"""
            <div style="text-align: center; padding: 10px;">
                <div style="font-size: 0.9em;">💬 {answers_count} 回答</div>
                <div style="font-size: 0.8em; color: #888;">👁️ {views} 浏览</div>
            </div>
            """, unsafe_allow_html=True)
        
        if show_full:
            st.markdown("---")
            st.markdown(content)
        
        st.markdown("---")


def render_answer(answer: dict, question_id: str):
    """Render an answer."""
    a_id = answer.get("id", "")
    content = answer.get("content", "")
    author = answer.get("author", "匿名")
    is_ai = answer.get("is_ai", False)
    created_at = answer.get("created_at", "")
    upvotes = answer.get("upvotes", 0)
    downvotes = answer.get("downvotes", 0)
    is_accepted = answer.get("is_accepted", False)
    
    # Answer container with styling
    border_color = "#4CAF50" if is_accepted else ("#2196F3" if is_ai else "#333")
    
    with st.container():
        col1, col2 = st.columns([1, 9])
        
        with col1:
            # Voting buttons
            if st.button("👍", key=f"up_{a_id}_{question_id}"):
                community_qa.vote(question_id, a_id, True)
                st.rerun()
            
            st.markdown(f"**{upvotes - downvotes}**")
            
            if st.button("👎", key=f"down_{a_id}_{question_id}"):
                community_qa.vote(question_id, a_id, False)
                st.rerun()
            
            if is_accepted:
                st.markdown("✅")
        
        with col2:
            # Author badge
            if is_ai:
                st.markdown("🤖 **AI 助手回答**")
                st.info("以下是 AI 生成的参考答案，请结合社区回答综合参考")
            else:
                st.markdown(f"👤 **{author}** 回答")
            
            st.caption(f"🕐 {format_time(created_at)}")
            
            # Answer content
            st.markdown(content)
        
        st.markdown("---")


def render_ask_question():
    """Render the ask question form."""
    st.markdown("### ✍️ 提问")
    
    with st.form("ask_question_form"):
        title = st.text_input("问题标题", placeholder="简洁描述你的问题")
        
        category = st.selectbox(
            "问题分类",
            list(CommunityQA.CATEGORIES.keys()),
            format_func=lambda x: CommunityQA.CATEGORIES.get(x, x)
        )
        
        content = st.text_area(
            "问题详情",
            height=200,
            placeholder="详细描述你的问题，包括:\n- 背景信息\n- 你尝试过的方法\n- 具体困惑的点"
        )
        
        tags_input = st.text_input("标签 (用逗号分隔)", placeholder="例如: 系统设计, Google, 推荐系统")
        
        col1, col2 = st.columns(2)
        with col1:
            get_ai = st.checkbox("获取 AI 参考答案", value=True)
        with col2:
            anonymous = st.checkbox("匿名提问")
        
        submitted = st.form_submit_button("🚀 发布问题", type="primary")
        
        if submitted and title and content:
            author = "匿名用户" if anonymous else get_username()
            tags = [t.strip() for t in tags_input.split(",") if t.strip()]
            
            with st.spinner("正在发布问题并获取 AI 回答..."):
                question = community_qa.create_question(
                    title=title,
                    content=content,
                    author=author,
                    category=category,
                    tags=tags,
                    get_ai_answer=get_ai
                )
            
            # Award points for asking question
            if not anonymous and author != "匿名用户":
                points = award_points(author, "ask_question")
                gamification.increment_stat(author, "total_questions")
                st.toast(f"🎉 获得 {points} 积分！")
            
            st.success("问题发布成功！")
            st.session_state.viewing_question = question.id
            st.rerun()


def render_question_detail(question_id: str):
    """Render a single question with all answers."""
    question = community_qa.get_question(question_id)
    
    if not question:
        st.error("问题不存在")
        return
    
    # Back button
    if st.button("← 返回列表"):
        st.session_state.viewing_question = None
        st.rerun()
    
    # Question card
    render_question_card(question, show_full=True)
    
    # AI Answer (if exists)
    if question.get("ai_answer"):
        st.markdown("### 🤖 AI 参考答案")
        render_answer(question["ai_answer"], question_id)
    
    # Human answers
    answers = question.get("answers", [])
    if answers:
        st.markdown(f"### 👥 社区回答 ({len(answers)})")
        
        # Sort by votes
        answers = sorted(answers, key=lambda x: x.get("upvotes", 0) - x.get("downvotes", 0), reverse=True)
        
        for answer in answers:
            render_answer(answer, question_id)
    
    # Add answer form
    st.markdown("### ✍️ 我来回答")
    
    with st.form("add_answer_form"):
        answer_content = st.text_area(
            "你的回答",
            height=200,
            placeholder="分享你的经验和见解..."
        )
        
        col1, col2 = st.columns(2)
        with col1:
            anonymous_answer = st.checkbox("匿名回答")
        
        submitted = st.form_submit_button("📝 提交回答", type="primary")
        
        if submitted and answer_content:
            author = "匿名用户" if anonymous_answer else get_username()
            community_qa.add_answer(question_id, answer_content, author)
            
            # Award points for answering
            if not anonymous_answer and author != "匿名用户":
                points = award_points(author, "answer_question")
                gamification.increment_stat(author, "total_answers")
                st.toast(f"🎉 获得 {points} 积分！感谢你的贡献")
            
            st.success("回答提交成功！")
            st.rerun()


def render_community_qa():
    """Main render function for community Q&A page."""
    
    st.markdown("## 💬 面试问答社区")
    st.markdown("*提问 → AI 先答 → 社区补充 → 共同成长*")
    
    # Username input (simple auth)
    if "username" not in st.session_state:
        st.session_state.username = ""
    
    with st.sidebar:
        st.markdown("### 👤 我的账号")
        username = st.text_input("昵称", value=st.session_state.username, key="username_input")
        if username != st.session_state.username:
            st.session_state.username = username
        
        st.markdown("---")
        
        # Stats
        stats = community_qa.get_stats()
        st.markdown("### 📊 社区统计")
        st.metric("总问题数", stats.get("total_questions", 0))
        st.metric("总回答数", stats.get("total_answers", 0))
        st.metric("已解答", stats.get("answered_questions", 0))
    
    # Check if viewing a specific question
    if st.session_state.get("viewing_question"):
        render_question_detail(st.session_state.viewing_question)
        return
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["📋 浏览问题", "✍️ 我要提问", "🔍 搜索"])
    
    with tab1:
        # Filters
        col1, col2 = st.columns([2, 1])
        
        with col1:
            category_filter = st.selectbox(
                "分类筛选",
                ["all"] + list(CommunityQA.CATEGORIES.keys()),
                format_func=lambda x: "全部分类" if x == "all" else CommunityQA.CATEGORIES.get(x, x)
            )
        
        with col2:
            sort_by = st.selectbox(
                "排序",
                ["newest", "popular", "unanswered"],
                format_func=lambda x: {"newest": "最新", "popular": "最热", "unanswered": "待回答"}[x]
            )
        
        # Questions list
        questions = community_qa.get_questions(
            category=category_filter if category_filter != "all" else None,
            sort_by=sort_by
        )
        
        if not questions:
            st.info("暂无问题，成为第一个提问者吧！")
        else:
            for question in questions:
                render_question_card(question)
    
    with tab2:
        render_ask_question()
    
    with tab3:
        st.markdown("### 🔍 搜索问题")
        
        search_query = st.text_input("搜索关键词", placeholder="输入关键词搜索问题...")
        
        if search_query:
            results = community_qa.search(search_query)
            
            if results:
                st.markdown(f"*找到 {len(results)} 个相关问题*")
                for question in results:
                    render_question_card(question)
            else:
                st.info("未找到相关问题，试试其他关键词？")


# For direct import
if __name__ == "__main__":
    render_community_qa()
