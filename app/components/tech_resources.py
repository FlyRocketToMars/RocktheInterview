"""
Tech Resources Library Component
Browse engineering blogs, papers, and learning resources from major tech companies
"""
import streamlit as st
import json
from pathlib import Path
from typing import Dict, List


def load_tech_resources() -> Dict:
    """Load tech resources from JSON file."""
    resources_file = Path(__file__).parent.parent.parent / "data" / "tech_resources.json"
    
    if resources_file.exists():
        with open(resources_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def render_tech_resources():
    """Render the tech resources library page."""
    
    st.markdown("## 📖 技术资源库")
    st.markdown("*各大公司技术博客、必读论文、学习课程*")
    
    # Load data
    data = load_tech_resources()
    companies = data.get("companies", {})
    learning = data.get("learning_resources", {})
    topic_mapping = data.get("topic_mapping", {})
    
    if not companies:
        st.warning("资源库暂无数据")
        return
    
    cutting_edge = data.get("cutting_edge_2024", {})
    
    # Tabs for different sections
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📰 博客聚合", "🔥 最新论文", "🏢 公司论文", "📖 公司博客", "📚 经典必读", "🎓 学习资源"
    ])
    
    # ============ Tab 0: Blog Aggregator ============
    with tab1:
        st.markdown("### 📰 面试准备博客聚合")
        st.markdown("*自动聚合顶级 ML/AI 面试准备博客的最新内容*")
        
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            from data.blog_aggregator import blog_aggregator, get_latest_articles, get_blog_sources
            
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🔄 刷新博客", key="refresh_blogs"):
                    with st.spinner("正在获取最新文章..."):
                        blog_aggregator.fetch_all(force_refresh=True)
                    st.success("已更新！")
                    st.rerun()
            
            # Show blog sources
            with st.expander("📚 收录的博客源", expanded=False):
                sources = get_blog_sources()
                cols = st.columns(3)
                for i, source in enumerate(sources):
                    with cols[i % 3]:
                        rating = "⭐" * source.get("quality_rating", 3)
                        st.markdown(f"""
                        **[{source.get('name')}]({source.get('url')})**  
                        作者: {source.get('author')}  
                        {rating}  
                        *{source.get('description', '')[:50]}...*
                        """)
            
            st.markdown("---")
            
            # Filter by topic
            categories = blog_aggregator.get_categories()
            selected_topic = st.selectbox(
                "按主题筛选",
                ["全部"] + list(categories.keys()),
                format_func=lambda x: categories.get(x, x) if x != "全部" else "📋 全部文章"
            )
            
            # Get articles
            if selected_topic == "全部":
                articles = get_latest_articles(limit=30)
            else:
                articles = blog_aggregator.get_by_topic(selected_topic)
            
            if articles:
                for idx_art, article in enumerate(articles[:20]):
                    import re, hashlib
                    # Sanitize summary - strip HTML tags
                    raw_summary = article.get('summary', '')
                    clean_summary = re.sub(r'<[^>]+>', '', raw_summary)[:150]
                    
                    art_hash = hashlib.md5(f"{article.get('url','')}{idx_art}".encode()).hexdigest()[:8]
                    
                    with st.container():
                        st.markdown(f"""
                        <div style="padding: 1rem; border-radius: 8px; background: #1e293b; margin-bottom: 0.5rem;">
                            <h4 style="margin: 0;">
                                <a href="{article.get('url', '#')}" target="_blank" style="color: #60a5fa; text-decoration: none;">
                                    {article.get('title', 'Untitled')}
                                </a>
                            </h4>
                            <p style="color: #94a3b8; font-size: 0.9rem; margin: 0.5rem 0;">
                                {clean_summary}
                            </p>
                            <p style="color: #64748b; font-size: 0.8rem; margin: 0;">
                                📝 {article.get('source_name', '')} · {article.get('published', '')[:10]}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("暂无文章，点击刷新获取最新内容")
                
        except Exception as e:
            st.error(f"加载博客聚合器失败: {e}")
            st.info("请确保已安装 feedparser: pip install feedparser")
    
    
    # ============ Tab 1: Latest Papers (Dynamic) ============
    with tab2:
        st.markdown("### 🔥 最新 ML/AI 论文")
        st.markdown("*实时从 arXiv、Hugging Face 获取最新研究*")
        
        # Import papers fetcher
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            from data.papers_fetcher import papers_aggregator, get_hot_papers
            
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🔄 刷新论文"):
                    with st.spinner("正在获取最新论文..."):
                        papers_aggregator.get_latest_papers(force_refresh=True)
                    st.success("已更新！")
                    st.rerun()
            
            # Get latest papers
            with st.spinner("加载最新论文..."):
                latest_data = papers_aggregator.get_latest_papers()
            
            last_updated = latest_data.get("last_updated", "")
            if last_updated:
                st.caption(f"📅 上次更新: {last_updated[:19]}")
            
            # arXiv papers by category
            arxiv_data = latest_data.get("sources", {}).get("arxiv", {})
            
            for cat_name, papers in arxiv_data.items():
                if papers:
                    st.markdown(f"#### 📚 {cat_name}")
                    
                    for paper in papers[:5]:  # Show top 5 per category
                        with st.expander(f"📄 {paper.get('title', 'Untitled')[:80]}..."):
                            st.markdown(f"**📅 发布日期**: {paper.get('published', 'N/A')}")
                            st.markdown(f"**👥 作者**: {', '.join(paper.get('authors', [])[:3])}")
                            st.markdown(f"🔗 [arXiv 链接]({paper.get('url', '#')})")
                            st.markdown("**摘要:**")
                            st.caption(paper.get("abstract", "")[:300] + "...")
                    
                    st.markdown("---")
            
            # Hugging Face Daily Papers
            hf_papers = latest_data.get("sources", {}).get("huggingface", [])
            if hf_papers:
                st.markdown("#### 🤗 Hugging Face 今日热门")
                
                for paper in hf_papers[:10]:
                    with st.expander(f"🔥 {paper.get('title', 'Untitled')[:80]}"):
                        st.markdown(f"👍 **点赞**: {paper.get('upvotes', 0)}")
                        st.markdown(f"🔗 [查看论文]({paper.get('url', '#')})")
                        if paper.get("abstract"):
                            st.caption(paper.get("abstract", "")[:200] + "...")
        
        except Exception as e:
            st.warning(f"无法加载最新论文: {e}")
            st.info("显示经典论文列表...")
            
            # Fallback to static cutting edge papers
            st.markdown("#### 🎯 生成式推荐 (Generative Recommendation)")
            for paper in cutting_edge.get("generative_recommendation", []):
                with st.expander(f"📄 **{paper['title']}** ({paper.get('year', '')})"):
                    st.markdown(f"🔗 [{paper['url']}]({paper['url']})")
                    st.markdown(f"📝 {paper.get('description', '')}")
    
    
    # ============ Tab 2: Company Papers ============
    with tab3:
        st.markdown("### 🏢 公司最新论文")
        st.markdown("*追踪各大科技公司的最新研究成果*")
        
        try:
            from data.company_papers import company_papers, get_company_research_links
            
            # Get research links
            research_links = get_company_research_links()
            
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🔄 刷新公司论文"):
                    with st.spinner("正在获取最新论文..."):
                        company_papers.fetch_all_company_papers(force_refresh=True)
                    st.success("已更新！")
                    st.rerun()
            
            # Company selector
            company_list = list(research_links.keys())
            selected = st.selectbox(
                "选择公司",
                ["全部"] + company_list,
                format_func=lambda x: "全部公司" if x == "全部" else f"{research_links[x]['icon']} {research_links[x]['name']}"
            )
            
            st.markdown("---")
            
            if selected == "全部":
                display_links = research_links.items()
            else:
                display_links = [(selected, research_links[selected])]
            
            for company_id, info in display_links:
                st.markdown(f"### {info['icon']} {info['name']}")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f"[📝 研究博客]({info.get('research_blog', '#')})")
                with col2:
                    st.markdown(f"[📚 论文库]({info.get('publications', '#')})")
                with col3:
                    st.markdown(f"[🔍 arXiv 搜索]({info.get('arxiv_search', '#')})")
                with col4:
                    st.markdown(f"[💻 GitHub]({info.get('github', '#')})")
                
                # Fetch recent papers from arXiv
                with st.spinner(f"获取 {info['name']} 最新论文..."):
                    papers = company_papers.fetch_arxiv_by_affiliation(company_id, max_results=3)
                
                if papers:
                    for paper in papers:
                        with st.expander(f"📄 {paper.get('title', 'Untitled')[:70]}..."):
                            st.markdown(f"**发布日期**: {paper.get('published', 'N/A')}")
                            st.markdown(f"**作者**: {', '.join(paper.get('authors', [])[:3])}")
                            st.markdown(f"🔗 [arXiv 链接]({paper.get('url', '#')})")
                            st.caption(paper.get("abstract", "")[:250] + "...")
                else:
                    st.caption("暂无最新论文，请点击上方链接访问官方页面")
                
                st.markdown("---")
        
        except Exception as e:
            st.warning(f"加载公司论文失败: {e}")
            st.info("请访问各公司官方研究页面查看最新论文")
    
    # ============ Tab 3: Company Blogs ============
    with tab4:
        st.markdown("### 📖 技术博客导航")
        st.markdown("*点击链接直接访问各公司工程博客*")
        
        # Company selection
        company_names = {k: v["name"] for k, v in companies.items()}
        selected_company = st.selectbox(
            "选择公司",
            ["全部"] + list(company_names.keys()),
            format_func=lambda x: "全部公司" if x == "全部" else company_names.get(x, x)
        )
        
        st.markdown("---")
        
        if selected_company == "全部":
            display_companies = companies.items()
        else:
            display_companies = [(selected_company, companies[selected_company])]
        
        for company_id, company_data in display_companies:
            company_name = company_data.get("name", company_id)
            
            st.markdown(f"#### 🏢 {company_name}")
            
            # Blog links
            for blog in company_data.get("blogs", []):
                topics_str = ", ".join([topic_mapping.get(t, t) for t in blog.get("topics", [])])
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**[{blog['name']}]({blog['url']})**")
                    st.caption(blog.get("description", ""))
                with col2:
                    st.caption(f"📌 {topics_str}")
            
            st.markdown("---")
    
    # ============ Tab 4: Must-Read Papers ============
    with tab5:
        st.markdown("### 📚 必读论文 & 文章")
        st.markdown("*MLE 面试高频引用的经典论文*")
        
        # Topic filter
        all_topics = set()
        for company_data in companies.values():
            for article in company_data.get("must_read_articles", []):
                all_topics.update(article.get("topics", []))
        
        col1, col2 = st.columns(2)
        with col1:
            selected_topic = st.selectbox(
                "按主题筛选",
                ["全部"] + sorted(list(all_topics)),
                format_func=lambda x: "全部主题" if x == "全部" else topic_mapping.get(x, x),
                key="paper_topic_filter"
            )
        with col2:
            selected_company_paper = st.selectbox(
                "按公司筛选",
                ["全部"] + list(company_names.keys()),
                format_func=lambda x: "全部公司" if x == "全部" else company_names.get(x, x),
                key="paper_company_filter"
            )
        
        st.markdown("---")
        
        # Collect and display papers
        all_papers = []
        for company_id, company_data in companies.items():
            for article in company_data.get("must_read_articles", []):
                article["company"] = company_data.get("name", company_id)
                article["company_id"] = company_id
                all_papers.append(article)
        
        # Sort by year descending
        all_papers = sorted(all_papers, key=lambda x: x.get("year", 0), reverse=True)
        
        # Apply filters
        if selected_topic != "全部":
            all_papers = [p for p in all_papers if selected_topic in p.get("topics", [])]
        if selected_company_paper != "全部":
            all_papers = [p for p in all_papers if p.get("company_id") == selected_company_paper]
        
        st.markdown(f"*共 {len(all_papers)} 篇必读文章*")
        
        for paper in all_papers:
            with st.expander(f"📄 **{paper['title']}** ({paper.get('year', 'N/A')})"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"🏢 **来源**: {paper.get('company', 'Unknown')}")
                    st.markdown(f"🔗 **链接**: [{paper['url']}]({paper['url']})")
                    
                    topics_str = " ".join([f"`{topic_mapping.get(t, t)}`" for t in paper.get("topics", [])])
                    st.markdown(f"🏷️ **主题**: {topics_str}")
                
                with col2:
                    st.info(f"💡 {paper.get('relevance', '')}")
    
    # ============ Tab 5: Learning Resources ============
    with tab6:
        st.markdown("### 🎓 学习资源")
        
        # Courses
        st.markdown("#### 📺 推荐课程")
        
        courses = learning.get("courses", [])
        for course in courses:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**[{course['name']}]({course['url']})**")
            with col2:
                st.caption(course.get("provider", ""))
            with col3:
                level_icons = {"beginner": "🟢", "intermediate": "🟡", "advanced": "🔴"}
                st.caption(f"{level_icons.get(course.get('level', ''), '⚪')} {course.get('level', '').title()}")
        
        st.markdown("---")
        
        # Books
        st.markdown("#### 📚 推荐书籍")
        
        books = learning.get("books", [])
        for book in books:
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**[{book['name']}]({book['url']})**")
                    st.caption(f"作者: {book.get('author', 'Unknown')}")
                with col2:
                    st.info(f"💡 {book.get('relevance', '')}")
        
        st.markdown("---")
        
        # YouTube Channels
        st.markdown("#### 🎬 YouTube 频道")
        
        channels = learning.get("youtube_channels", [])
        for channel in channels:
            col1, col2 = st.columns([2, 2])
            with col1:
                st.markdown(f"**[{channel['name']}]({channel['url']})**")
            with col2:
                st.caption(channel.get("relevance", ""))
        
        st.markdown("---")
        
        # Influential Personal Blogs
        st.markdown("#### ✍️ 大牛个人博客")
        
        blogs = data.get("influential_blogs", [])
        for blog in blogs:
            with st.expander(f"📝 **{blog['name']}** - {blog.get('author', '')}"):
                st.markdown(f"🔗 [{blog['url']}]({blog['url']})")
                st.markdown(f"🎯 **专长**: {blog.get('specialty', '')}")
                if blog.get("must_read"):
                    st.markdown("**必读文章:**")
                    for article in blog.get("must_read", []):
                        st.markdown(f"- {article}")
        
        st.markdown("---")
        
        # AI Conferences
        st.markdown("#### 🎓 重要 AI 会议")
        
        conferences = data.get("ai_conferences", {})
        
        conf_col1, conf_col2 = st.columns(2)
        
        with conf_col1:
            st.markdown("**🏆 顶级会议**")
            for conf in conferences.get("top_tier", []):
                st.markdown(f"- [{conf['name']}]({conf['url']}) ({conf.get('timing', '')})")
            
            st.markdown("**📚 NLP/LLM 会议**")
            for conf in conferences.get("nlp_and_llm", []):
                st.markdown(f"- [{conf['name']}]({conf['url']}) ({conf.get('timing', '')})")
        
        with conf_col2:
            st.markdown("**🎯 应用 ML 会议**")
            for conf in conferences.get("applied_ml", []):
                st.markdown(f"- [{conf['name']}]({conf['url']}) - {conf.get('relevance', '')}")
            
            st.markdown("**👁️ 计算机视觉会议**")
            for conf in conferences.get("computer_vision", []):
                st.markdown(f"- [{conf['name']}]({conf['url']}) ({conf.get('timing', '')})")
    
    # ============ Quick Access Section ============
    st.markdown("---")
    st.markdown("### 💰 职业资源 & 薪酬数据")
    
    career = data.get("career_resources", {})
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**💵 薪酬数据**")
        for site in career.get("salary_data", []):
            st.markdown(f"- [{site['name']}]({site['url']})")
            if site.get("description"):
                st.caption(site['description'])
    
    with col2:
        st.markdown("**📊 就业市场**")
        for site in career.get("job_market", []):
            st.markdown(f"- [{site['name']}]({site['url']})")
            if site.get("description"):
                st.caption(site['description'])
    
    with col3:
        st.markdown("**🏢 公司级别对照**")
        levels = career.get("company_levels", {})
        for company, info in levels.items():
            st.markdown(f"**{company.upper()}**: {', '.join(info.get('levels', []))}")
            st.caption(f"[薪酬详情]({info.get('levels_fyi_url', '')})")
    
    st.markdown("---")
    st.markdown("### ⚡ 快速访问")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🔥 热门博客**")
        st.markdown("""
        - [Lilian Weng](https://lilianweng.github.io/)
        - [Jay Alammar](https://jalammar.github.io/)
        - [Eugene Yan](https://eugeneyan.com/)
        """)
    
    with col2:
        st.markdown("**📖 2024 必读论文**")
        st.markdown("""
        - [Generative Rec Survey](https://arxiv.org/abs/2405.00318)
        - [RAG Survey](https://arxiv.org/abs/2312.10997)
        - [Llama 3](https://ai.meta.com/llama/)
        """)
    
    with col3:
        st.markdown("**💰 薪酬 & 就业**")
        st.markdown("""
        - [levels.fyi](https://www.levels.fyi/)
        - [layoffs.fyi](https://layoffs.fyi/)
        - [Blind](https://www.teamblind.com/)
        """)

