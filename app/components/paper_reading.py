"""
Paper Reading & Discussion Component
Collaborative paper annotation and discussion UI
"""
import streamlit as st
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from data.paper_annotations import paper_annotations
from data.papers_fetcher import get_hot_papers, papers_aggregator


def render_paper_reading():
    """Render the paper reading and discussion page."""
    
    st.markdown("## 📚 论文阅读与交流")
    st.markdown("*一起读论文，分享见解，共同进步*")
    
    # Stats bar
    stats = paper_annotations.get_stats()
    cols = st.columns(4)
    with cols[0]:
        st.metric("📄 论文数", stats["total_papers"])
    with cols[1]:
        st.metric("📝 注释数", stats["total_annotations"])
    with cols[2]:
        st.metric("💬 讨论数", stats["total_discussions"])
    with cols[3]:
        st.metric("👥 活跃用户", stats["active_users"])
    
    st.markdown("---")
    
    # Main tabs
    tabs = st.tabs([
        "🔥 热门论文", 
        "📖 我的阅读列表", 
        "🆕 最新论文", 
        "➕ 添加论文"
    ])
    
    with tabs[0]:
        render_trending_papers()
    
    with tabs[1]:
        render_my_reading_list()
    
    with tabs[2]:
        render_latest_papers()
    
    with tabs[3]:
        render_add_paper()


def render_trending_papers():
    """Render trending/popular papers."""
    
    papers = paper_annotations.get_all_papers()
    
    if not papers:
        st.info("📭 还没有论文，去「添加论文」或「最新论文」添加一篇吧！")
        return
    
    # Search
    search_query = st.text_input("🔍 搜索论文", placeholder="输入关键词...")
    
    if search_query:
        papers = paper_annotations.search_papers(search_query)
    
    for paper in papers:
        render_paper_card(paper)


def render_paper_card(paper: dict, show_full: bool = False):
    """Render a paper card with annotations."""
    
    with st.container():
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e293b 0%, #334155 100%); 
                    padding: 1rem; border-radius: 12px; margin-bottom: 1rem;
                    border-left: 4px solid #6366f1;">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <h4 style="color: #f1f5f9; margin: 0; flex: 1;">
                    {paper.get('title', 'Untitled')[:80]}{'...' if len(paper.get('title', '')) > 80 else ''}
                </h4>
                <span style="background: #6366f1; color: white; padding: 0.25rem 0.5rem; 
                            border-radius: 12px; font-size: 0.75rem; margin-left: 0.5rem;">
                    👍 {paper.get('upvotes', 0)}
                </span>
            </div>
            <p style="color: #94a3b8; font-size: 0.85rem; margin: 0.5rem 0;">
                来源: {paper.get('source', 'Unknown')} | 
                注释: {len(paper.get('annotations', []))} | 
                讨论: {len(paper.get('discussions', []))}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Expandable details
        with st.expander("📖 查看详情与讨论"):
            render_paper_detail(paper)


def render_paper_detail(paper: dict):
    """Render detailed paper view with annotations."""
    
    paper_id = paper.get("id", "")
    user_id = st.session_state.get("user_email", "guest")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Title and link
        st.markdown(f"### [{paper.get('title', '')}]({paper.get('url', '#')})")
        
        # Authors
        authors = paper.get("authors", [])
        if authors:
            st.markdown(f"**作者:** {', '.join(authors[:5])}")
        
        # Abstract
        st.markdown("**摘要:**")
        st.markdown(f">{paper.get('abstract', 'No abstract available.')[:500]}...")
        
        # Tags
        tags = paper.get("tags", [])
        if tags:
            tag_html = " ".join([f'<span style="background: #334155; padding: 0.2rem 0.5rem; border-radius: 8px; margin-right: 0.25rem; font-size: 0.8rem;">{t}</span>' for t in tags])
            st.markdown(f"**标签:** {tag_html}", unsafe_allow_html=True)
    
    with col2:
        # Reading status
        st.markdown("**📚 阅读状态**")
        current_status = paper.get("reading_status", {}).get(user_id, {}).get("status", "")
        
        status_options = {
            "want_to_read": "📌 想读",
            "reading": "📖 在读",
            "finished": "✅ 读完",
            "reviewed": "⭐ 精读"
        }
        
        selected_status = st.selectbox(
            "更新状态",
            options=list(status_options.keys()),
            format_func=lambda x: status_options[x],
            index=list(status_options.keys()).index(current_status) if current_status in status_options else 0,
            key=f"status_{paper_id}"
        )
        
        if st.button("更新", key=f"update_status_{paper_id}"):
            paper_annotations.update_reading_status(paper_id, user_id, selected_status)
            st.success("已更新！")
            st.rerun()
        
        # Upvote
        if st.button(f"👍 推荐 ({paper.get('upvotes', 0)})", key=f"upvote_{paper_id}"):
            paper_annotations.upvote_paper(paper_id, user_id)
            st.rerun()
    
    st.markdown("---")
    
    # Tabs for annotations and discussions
    detail_tabs = st.tabs(["💡 核心要点", "📝 注释笔记", "💬 交流讨论"])
    
    with detail_tabs[0]:
        render_key_takeaways(paper, paper_id, user_id)
    
    with detail_tabs[1]:
        render_annotations(paper, paper_id, user_id)
    
    with detail_tabs[2]:
        render_discussions(paper, paper_id, user_id)


def render_key_takeaways(paper: dict, paper_id: str, user_id: str):
    """Render key takeaways section."""
    
    st.markdown("### 💡 大家的核心收获")
    
    takeaways = paper.get("key_takeaways", [])
    
    if takeaways:
        for i, take in enumerate(takeaways):
            st.markdown(f"""
            <div style="background: #334155; padding: 0.75rem; border-radius: 8px; margin-bottom: 0.5rem;">
                <p style="margin: 0; color: #f1f5f9;">💡 {take.get('content', '')}</p>
                <p style="margin: 0.25rem 0 0 0; color: #64748b; font-size: 0.75rem;">
                    — {take.get('user_id', 'anonymous')[:20]} | 👍 {take.get('upvotes', 0)}
                </p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("还没有人分享要点，来添加第一个吧！")
    
    # Add new takeaway
    with st.form(f"takeaway_form_{paper_id}"):
        new_takeaway = st.text_area(
            "分享你的核心收获",
            placeholder="读完这篇论文，我最大的收获是...",
            key=f"new_takeaway_{paper_id}"
        )
        
        if st.form_submit_button("💡 分享"):
            if new_takeaway.strip():
                paper_annotations.add_key_takeaway(paper_id, user_id, new_takeaway)
                st.success("已分享！")
                st.rerun()
            else:
                st.warning("请输入内容")


def render_annotations(paper: dict, paper_id: str, user_id: str):
    """Render annotations section."""
    
    st.markdown("### 📝 注释与笔记")
    
    annotations = paper.get("annotations", [])
    
    # Filter by type
    ann_types = {
        "all": "全部",
        "note": "📝 笔记",
        "highlight": "🔍 重点",
        "question": "❓ 疑问",
        "insight": "💡 洞见"
    }
    
    filter_type = st.selectbox(
        "筛选类型",
        options=list(ann_types.keys()),
        format_func=lambda x: ann_types[x],
        key=f"filter_{paper_id}"
    )
    
    filtered = annotations if filter_type == "all" else [a for a in annotations if a.get("type") == filter_type]
    
    if filtered:
        for ann in filtered:
            icon = {"note": "📝", "highlight": "🔍", "question": "❓", "insight": "💡"}.get(ann.get("type", "note"), "📝")
            
            st.markdown(f"""
            <div style="background: #1e293b; padding: 0.75rem; border-radius: 8px; margin-bottom: 0.5rem;
                        border-left: 3px solid {'#22d3ee' if ann.get('type') == 'question' else '#6366f1'};">
                <p style="margin: 0; color: #94a3b8; font-size: 0.8rem;">
                    {icon} {ann.get('section', '全文')} | {ann.get('user_id', 'anonymous')[:15]}
                </p>
                <p style="margin: 0.5rem 0; color: #f1f5f9;">{ann.get('content', '')}</p>
                <p style="margin: 0; color: #64748b; font-size: 0.75rem;">
                    👍 {ann.get('upvotes', 0)} | {ann.get('created_at', '')[:10]}
                </p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("还没有注释，添加第一条吧！")
    
    # Add new annotation
    st.markdown("#### ✏️ 添加注释")
    
    with st.form(f"annotation_form_{paper_id}"):
        col1, col2 = st.columns(2)
        
        with col1:
            ann_type = st.selectbox(
                "类型",
                options=["note", "highlight", "question", "insight"],
                format_func=lambda x: ann_types[x],
                key=f"ann_type_{paper_id}"
            )
        
        with col2:
            section = st.selectbox(
                "章节",
                options=["全文", "摘要", "方法", "实验", "结论", "其他"],
                key=f"section_{paper_id}"
            )
        
        content = st.text_area(
            "内容",
            placeholder="写下你的笔记、问题或见解...",
            key=f"ann_content_{paper_id}"
        )
        
        if st.form_submit_button("📝 添加注释"):
            if content.strip():
                paper_annotations.add_annotation(paper_id, user_id, {
                    "type": ann_type,
                    "content": content,
                    "section": section
                })
                st.success("注释已添加！")
                st.rerun()
            else:
                st.warning("请输入内容")


def render_discussions(paper: dict, paper_id: str, user_id: str):
    """Render discussions section."""
    
    st.markdown("### 💬 交流讨论")
    
    discussions = paper.get("discussions", [])
    
    if discussions:
        for disc in discussions:
            st.markdown(f"""
            <div style="background: #1e293b; padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem;">
                <p style="margin: 0; color: #60a5fa; font-size: 0.85rem; font-weight: 600;">
                    💬 {disc.get('user_id', 'anonymous')[:20]}
                </p>
                <p style="margin: 0.5rem 0; color: #f1f5f9;">{disc.get('content', '')}</p>
                <p style="margin: 0; color: #64748b; font-size: 0.75rem;">
                    {disc.get('created_at', '')[:16]} | 👍 {disc.get('upvotes', 0)} | 
                    回复: {len(disc.get('replies', []))}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show replies
            for reply in disc.get("replies", []):
                st.markdown(f"""
                <div style="background: #334155; padding: 0.75rem; border-radius: 8px; 
                            margin: 0.25rem 0 0.5rem 2rem; border-left: 2px solid #6366f1;">
                    <p style="margin: 0; color: #94a3b8; font-size: 0.8rem;">
                        ↳ {reply.get('user_id', 'anonymous')[:15]}
                    </p>
                    <p style="margin: 0.25rem 0; color: #e2e8f0; font-size: 0.9rem;">
                        {reply.get('content', '')}
                    </p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("还没有讨论，开始第一个话题吧！")
    
    # Add new discussion
    with st.form(f"discussion_form_{paper_id}"):
        new_comment = st.text_area(
            "发表评论",
            placeholder="分享你的观点、提问或回答他人的问题...",
            key=f"new_disc_{paper_id}"
        )
        
        if st.form_submit_button("💬 发表"):
            if new_comment.strip():
                paper_annotations.add_discussion(paper_id, user_id, new_comment)
                st.success("评论已发表！")
                st.rerun()
            else:
                st.warning("请输入内容")


def render_my_reading_list():
    """Render user's reading list."""
    
    user_id = st.session_state.get("user_email", "guest")
    reading_list = paper_annotations.get_user_reading_list(user_id)
    
    st.markdown("### 📖 我的阅读列表")
    
    status_tabs = st.tabs(["📌 想读", "📖 在读", "✅ 读完", "⭐ 精读"])
    
    status_keys = ["want_to_read", "reading", "finished", "reviewed"]
    
    for i, status in enumerate(status_keys):
        with status_tabs[i]:
            papers = reading_list.get(status, [])
            if papers:
                for paper in papers:
                    render_paper_card(paper)
            else:
                st.info(f"这里还没有论文")


def render_latest_papers():
    """Render latest papers from arXiv etc."""
    
    st.markdown("### 🆕 最新热门论文")
    st.caption("从 arXiv, Hugging Face 等平台获取")
    
    if st.button("🔄 刷新论文列表"):
        with st.spinner("获取最新论文..."):
            papers_aggregator.get_latest_papers(force_refresh=True)
            st.success("已更新！")
    
    try:
        hot_papers = get_hot_papers()
        top_papers = hot_papers.get("top_papers", [])
        
        if top_papers:
            for paper in top_papers[:15]:
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        st.markdown(f"""
                        <div style="background: #1e293b; padding: 0.75rem; border-radius: 8px;">
                            <p style="margin: 0; color: #f1f5f9; font-weight: 500;">
                                {paper.get('title', '')[:100]}
                            </p>
                            <p style="margin: 0.25rem 0 0 0; color: #64748b; font-size: 0.8rem;">
                                {paper.get('source', '')} | {paper.get('published', '')[:10]} | 
                                {paper.get('category', '')}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        if st.button("➕ 添加", key=f"add_{paper.get('url', '')[:20]}"):
                            paper_id = paper_annotations.add_paper({
                                "title": paper.get("title", ""),
                                "url": paper.get("url", ""),
                                "abstract": paper.get("abstract", ""),
                                "authors": paper.get("authors", []),
                                "source": paper.get("source", ""),
                                "tags": [paper.get("category", "ML")],
                                "added_by": st.session_state.get("user_email", "guest")
                            })
                            st.success(f"已添加到阅读列表！")
                            st.rerun()
        else:
            st.info("没有获取到论文，点击刷新按钮获取")
    except Exception as e:
        st.error(f"获取论文失败: {e}")
        st.info("请点击刷新按钮重试")


def render_add_paper():
    """Render form to add a custom paper."""
    
    st.markdown("### ➕ 添加论文")
    st.caption("手动添加一篇论文到协作阅读列表")
    
    with st.form("add_paper_form"):
        title = st.text_input("论文标题 *", placeholder="Attention Is All You Need")
        url = st.text_input("论文链接 *", placeholder="https://arxiv.org/abs/...")
        abstract = st.text_area("摘要", placeholder="论文摘要...", max_chars=1000)
        authors = st.text_input("作者", placeholder="用逗号分隔: Author1, Author2")
        tags = st.text_input("标签", placeholder="用逗号分隔: LLM, Transformer, NLP")
        
        difficulty = st.select_slider(
            "难度",
            options=["easy", "medium", "hard", "expert"],
            value="medium",
            format_func=lambda x: {"easy": "🟢 入门", "medium": "🟡 中等", "hard": "🔴 困难", "expert": "⚫ 专家"}[x]
        )
        
        if st.form_submit_button("➕ 添加论文"):
            if title and url:
                paper_id = paper_annotations.add_paper({
                    "title": title,
                    "url": url,
                    "abstract": abstract,
                    "authors": [a.strip() for a in authors.split(",") if a.strip()],
                    "tags": [t.strip() for t in tags.split(",") if t.strip()],
                    "difficulty": difficulty,
                    "source": "User Added",
                    "added_by": st.session_state.get("user_email", "guest")
                })
                st.success(f"✅ 论文已添加！ID: {paper_id}")
                st.rerun()
            else:
                st.error("请填写标题和链接")


# For direct testing
if __name__ == "__main__":
    render_paper_reading()
