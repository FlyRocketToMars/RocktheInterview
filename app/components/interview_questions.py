"""
Interview Questions Browser Component v2.0
Enhanced UI with professional MLE categorization and community answers
"""
import streamlit as st
import json
import hashlib
from pathlib import Path
from typing import Dict, List
from datetime import datetime
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def load_question_answers(question_id: str) -> Dict:
    """Load community answers for a specific question."""
    answers_file = Path(__file__).parent.parent.parent / "data" / "question_answers.json"
    
    if answers_file.exists():
        try:
            with open(answers_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("questions", {}).get(question_id, {"answers": [], "stats": {}})
        except:
            pass
    return {"answers": [], "stats": {"views": 0, "total_answers": 0}}


def save_question_answer(question_id: str, answer: Dict):
    """Save a community answer for a question."""
    answers_file = Path(__file__).parent.parent.parent / "data" / "question_answers.json"
    
    # Load existing data
    data = {"questions": {}}
    if answers_file.exists():
        try:
            with open(answers_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            pass
    
    # Initialize question if not exists
    if question_id not in data["questions"]:
        data["questions"][question_id] = {"answers": [], "stats": {"views": 0, "total_answers": 0}}
    
    # Add answer
    data["questions"][question_id]["answers"].append(answer)
    data["questions"][question_id]["stats"]["total_answers"] += 1
    
    # Save
    with open(answers_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def vote_answer(question_id: str, answer_id: str, is_upvote: bool = True):
    """Vote on an answer."""
    answers_file = Path(__file__).parent.parent.parent / "data" / "question_answers.json"
    
    if not answers_file.exists():
        return
    
    with open(answers_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if question_id in data["questions"]:
        for ans in data["questions"][question_id]["answers"]:
            if ans.get("id") == answer_id:
                if is_upvote:
                    ans["upvotes"] = ans.get("upvotes", 0) + 1
                else:
                    ans["downvotes"] = ans.get("downvotes", 0) + 1
                break
        
        with open(answers_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


def get_question_id(question: Dict) -> str:
    """Generate a unique ID for a question."""
    content = f"{question.get('company', '')}{question.get('question', '')[:50]}"
    return hashlib.md5(content.encode()).hexdigest()[:12]


def render_community_answers(question_id: str, question_text: str, context_key: str = ""):
    """Render community answers section for a question."""
    
    # Load existing answers
    qa_data = load_question_answers(question_id)
    answers = qa_data.get("answers", [])
    
    st.markdown("### 👥 社区回答")
    
    if answers:
        # Sort by upvotes
        answers = sorted(answers, key=lambda x: x.get("upvotes", 0) - x.get("downvotes", 0), reverse=True)
        
        for ans in answers:
            with st.container():
                col1, col2 = st.columns([1, 9])
                
                with col1:
                    upvotes = ans.get("upvotes", 0)
                    downvotes = ans.get("downvotes", 0)
                    score = upvotes - downvotes
                    
                    if st.button("👍", key=f"up_{context_key}_{question_id}_{ans['id']}"):
                        vote_answer(question_id, ans["id"], True)
                        st.rerun()
                    
                    st.markdown(f"**{score}**")
                    
                    if st.button("👎", key=f"down_{context_key}_{question_id}_{ans['id']}"):
                        vote_answer(question_id, ans["id"], False)
                        st.rerun()
                
                with col2:
                    author = ans.get("author", "匿名")
                    created_at = ans.get("created_at", "")[:10]
                    st.caption(f"👤 {author} | 🕐 {created_at}")
                    st.markdown(ans.get("content", ""))
                
                st.markdown("---")
    else:
        st.info("暂无社区回答，成为第一个回答者吧！")
    
    # Add answer form
    st.markdown("### ✍️ 我来回答")
    
    with st.form(f"answer_form_{context_key}_{question_id}"):
        user_answer = st.text_area(
            "你的回答",
            height=150,
            placeholder="分享你的解题思路、面试经验或补充内容...",
            key=f"answer_input_{context_key}_{question_id}"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            author_name = st.text_input("你的昵称", value=st.session_state.get("username", ""), key=f"author_{context_key}_{question_id}")
        with col2:
            anonymous = st.checkbox("匿名提交", key=f"anon_{context_key}_{question_id}")
        
        submitted = st.form_submit_button("📝 提交回答", type="primary")
        
        if submitted and user_answer:
            answer = {
                "id": hashlib.md5(f"{user_answer}{datetime.now()}".encode()).hexdigest()[:12],
                "content": user_answer,
                "author": "匿名用户" if anonymous else (author_name or "匿名用户"),
                "created_at": datetime.now().isoformat(),
                "upvotes": 0,
                "downvotes": 0
            }
            save_question_answer(question_id, answer)
            st.success("回答提交成功！感谢你的贡献 🎉")
            st.rerun()




def load_interview_questions() -> Dict:
    """Load interview questions from JSON file."""
    questions_file = Path(__file__).parent.parent.parent / "data" / "interview_questions.json"
    
    if questions_file.exists():
        with open(questions_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"questions": [], "metadata": {}, "categories": {}}


def render_mle_questions():
    """Render the MLE interview questions browser."""
    
    # Custom CSS
    st.markdown("""
    <style>
    .question-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #3b82f6;
    }
    .frequency-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .freq-5 { background: #dc2626; color: white; }
    .freq-4 { background: #f59e0b; color: black; }
    .freq-3 { background: #10b981; color: white; }
    .stats-card {
        background: linear-gradient(135deg, #312e81 0%, #4c1d95 100%);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("## 📚 MLE 面试题库")
    st.markdown("*专为 Machine Learning Engineer 打造的高质量面试题库*")
    
    # Load data
    data = load_interview_questions()
    questions = data.get("questions", [])
    
    if not questions:
        st.warning("题库暂无数据")
        return
        
    metadata = data.get("metadata", {})
    categories = data.get("categories", {})
        
    # Get user profile setting for targeting
    try:
        from components.auth import get_current_user
        from data.daily_learning import daily_learning
        user_email = get_current_user()
        user_targets = ["全部"]
        user_level = "全部"
        if user_email:
            profile_data = daily_learning.get_user_profile(user_email)
            if profile_data and "profile" in profile_data:
                # Handle both string (old) and list (new) formats for target_company
                tc = profile_data["profile"].get("target_company")
                if isinstance(tc, list):
                    user_targets = tc
                elif isinstance(tc, str):
                    user_targets = [tc]
                user_level = profile_data["profile"].get("target_level", "全部")
    except:
        user_targets = ["全部"]
        user_level = "全部"

    # ============ Stats Dashboard ============
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 题目总数", len(questions))
    with col2:
        hard_count = len([q for q in questions if q.get("difficulty") == "hard"])
        st.metric("🔴 高难度题", hard_count)
    with col3:
        high_freq = len([q for q in questions if q.get("frequency", 0) >= 4])
        st.metric("🔥 高频题", high_freq)
    with col4:
        companies = len(set(q.get("company", "") for q in questions))
        st.metric("🏢 覆盖公司", companies)
    
    st.markdown(f"*🕐 更新时间: {metadata.get('last_updated', 'N/A')}*")
    st.markdown("---")
    
    # ============ 🗂️ 四大战区 Tabs ============
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 锁定目标 (Targeted)", 
        "🌐 面经雷达 (Market Intel)", 
        "💻 算法手撕 (Code Mastery)",
        "✏️ 我的题库 (My Questions)"
    ])
    
    # ============ TAB 1: TARGETED PREP ============
    with tab1:
        st.markdown("### 🎯 专属靶向锁定")
        if "全部" in user_targets:
            st.info("你尚未在「目标与能力评估」中设置具体的目标公司。目前显示全库高频精选原题。")
            targeted_qs = [q for q in questions if "community-scraped" not in q.get("tags", [])]
        else:
            st.success(f"已自动为你过滤并锁定 **{', '.join(user_targets)}** (级别: {user_level}) 的核心考察点！")
            targeted_qs = [q for q in questions if q.get("company") in user_targets]
            if not targeted_qs:
                st.warning("目前题库中暂无你所选定公司的专属原题。已为你回退显示通用大厂面经。")
                targeted_qs = [q for q in questions if "community-scraped" not in q.get("tags", [])]
                
        # Sort by frequency
        targeted_qs = sorted(targeted_qs, key=lambda x: (x.get("frequency", 0), x.get("importance", 0)), reverse=True)
        
        # ---- Sub-tabs by category ----
        CATEGORY_MAP = {
            "📗 ML 基础": lambda q: q.get("domain") == "fundamentals" and q.get("round") != "ml_coding",
            "🔮 深度学习": lambda q: q.get("domain") == "deep_learning" and q.get("round") != "ml_coding",
            "🏗️ ML 系统设计": lambda q: q.get("round") == "ml_system_design",
            "🎯 推荐/排序": lambda q: q.get("domain") in ("recsys", "ranking") and q.get("round") != "ml_system_design",
            "📝 NLP": lambda q: q.get("domain") == "nlp",
            "👁️ CV": lambda q: q.get("domain") == "cv",
            "🤖 LLM": lambda q: q.get("domain") == "llm",
            "⚙️ MLOps/数据": lambda q: q.get("domain") in ("mlops", "ml_ops", "experimentation"),
            "💻 ML Coding": lambda q: q.get("round") == "ml_coding",
            "🗣️ Behavioral": lambda q: q.get("round") == "behavioral",
            "📚 全部": lambda q: True,
        }
        
        sub_tab_names = list(CATEGORY_MAP.keys())
        sub_tabs = st.tabs(sub_tab_names)
        
        for sub_tab, (cat_name, filter_fn) in zip(sub_tabs, CATEGORY_MAP.items()):
            with sub_tab:
                cat_qs = [q for q in targeted_qs if filter_fn(q)]
                if cat_qs:
                    st.caption(f"共 {len(cat_qs)} 道题")
                    render_question_list(cat_qs, page_key=f"target_{cat_name}")
                else:
                    st.info(f"「{cat_name}」分类下暂无题目")

    # ============ TAB 2: MARKET INTEL ============
    with tab2:
        st.markdown("### 🌐 全网最新面经雷达")
        st.markdown("*每天从 Reddit, 一亩三分地等社区自动为您抓取并由 AI 解析的最新面经动向。不要留有信息差！*")
        
        # Filter only auto-scraped questions
        scraped_qs = [q for q in questions if "community-scraped" in q.get("tags", [])]
        
        if not scraped_qs:
            st.info("爬虫机器人正在努力搜集中，目前暂无社区面经数据。")
        else:
            # Sort by newest first (assuming appended at front means newer)
            render_question_list(scraped_qs, page_key="market_intel_page")

    # ============ TAB 3: NEETCODE ============
    with tab3:
        render_neetcode_tracker()
        
    # ============ TAB 4: USER SUBMITTED ============
    with tab4:
        st.markdown("### ✏️ 我的自定义题库")
        st.markdown("*你可以在这里添加自己收集到的面经题目，系统会自动标记为「用户自创」。*")
        
        # Show existing user-submitted questions
        user_qs = [q for q in questions if "user-submitted" in q.get("tags", [])]
        if user_qs:
            st.markdown(f"**你已添加 {len(user_qs)} 道自创题目**")
            render_question_list(user_qs, page_key="user_submitted_page")
        
        st.markdown("---")
        st.markdown("#### ➕ 添加新题目")
        
        with st.form("add_user_question_form", clear_on_submit=True):
            new_question = st.text_area("📝 题目内容", placeholder="例如：Explain the difference between batch normalization and layer normalization...")
            new_answer = st.text_area("💡 参考答案（可选，留空后续补充）", placeholder="你的答案或笔记...")
            
            fc1, fc2, fc3 = st.columns(3)
            with fc1:
                new_company = st.text_input("🏢 公司", value="Community", placeholder="e.g. Google, Meta...")
            with fc2:
                new_domain = st.selectbox("🧠 领域", ["fundamentals", "deep_learning", "nlp", "cv", "recsys", "ranking", "llm", "mlops", "experimentation"])
            with fc3:
                new_difficulty = st.selectbox("⭐ 难度", ["easy", "medium", "hard"])
            
            fc4, fc5 = st.columns(2)
            with fc4:
                new_round = st.selectbox("📋 轮次", ["ml_theory", "ml_coding", "phone_screen", "coding", "ml_system_design", "system_design", "behavioral"])
            with fc5:
                new_freq = st.slider("🔥 高频度", 1, 5, 3)
            
            submitted = st.form_submit_button("🚀 提交题目", use_container_width=True)
            
            if submitted and new_question.strip():
                import uuid as _uuid
                new_entry = {
                    "id": f"user_{str(_uuid.uuid4())[:8]}",
                    "company": new_company.strip() or "Community",
                    "role": "MLE",
                    "level": "L4/L5",
                    "round": new_round,
                    "domain": new_domain,
                    "question": new_question.strip(),
                    "answer": new_answer.strip() if new_answer.strip() else "ℹ️ 答案待补充",
                    "follow_ups": [],
                    "difficulty": new_difficulty,
                    "frequency": new_freq,
                    "importance": new_freq,
                    "tags": ["user-submitted", new_domain],
                    "common_mistakes": [],
                    "year": datetime.now().year
                }
                
                # Save to JSON
                questions_file = Path(__file__).parent.parent.parent / "data" / "interview_questions.json"
                file_data = load_interview_questions()
                file_data["questions"].append(new_entry)
                if "metadata" in file_data:
                    file_data["metadata"]["total_questions"] = len(file_data["questions"])
                    file_data["metadata"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
                with open(questions_file, "w", encoding="utf-8") as f:
                    json.dump(file_data, f, indent=4, ensure_ascii=False)
                    
                st.success("🎉 题目已成功添加到你的自定义题库！")
                st.rerun()
            elif submitted:
                st.warning("题目内容不能为空哦！")
    
    st.markdown("---")
    
    # ============ Learning Path Suggestion ============
    st.markdown("### 📚 推荐学习路径")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🎯 MLE 面试准备顺序**
        
        1. **ML 基础** (1-2 周)
           - Bias-Variance, Regularization
           - Cross-validation, Metrics
        
        2. **深度学习** (1-2 周)
           - Transformer, Attention
           - Normalization, Optimization
        
        3. **ML 系统设计** (2-3 周)
           - 推荐系统, 排序系统
           - 广告点击预估
        
        4. **LLM 专项** (1 周)
           - RAG, Fine-tuning
           - Prompt Engineering
        """)
    
    with col2:
        st.markdown("""
        **🏢 按公司准备策略**
        
        - **Google**: 重视 ML 理论深度 + Coding
        - **Meta**: 强调系统设计 + 实验能力
        - **Amazon**: LP 行为面试 + 系统设计
        - **ByteDance**: 推荐/排序系统 + Coding
        - **OpenAI**: LLM 理论 + 系统设计
        """)


def render_neetcode_tracker():
    """Render the Neetcode 150 coding practice tracker."""
    st.markdown("### 💻 Neetcode 算法高频 150")
    st.markdown("*精选互联网大厂最常考的 150 道算法题，分门别类，针对性刷题。*")
    
    # Load data for Neetcode categories
    nc_file = Path(__file__).parent.parent.parent / "data" / "neetcode_questions.json"
    categories = []
    if nc_file.exists():
        with open(nc_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            categories = data.get("categories", [])
            
    # Load user progress
    try:
        from components.auth import get_current_user
        from data.daily_learning import daily_learning
        user_email = get_current_user()
        profile_data = None
        if user_email:
            profile_data = daily_learning.get_user_profile(user_email)
        completed_set = set()
        if profile_data and "progress" in profile_data:
            completed_set = set(profile_data["progress"].get("completed_questions", []))
    except Exception as e:
        completed_set = set()
        user_email = None

    # Top progress bar
    total_q = sum(len(c.get("questions", [])) for c in categories)
    completed_q = sum(1 for c in categories for q in c.get("questions", []) if q["id"] in completed_set)
    progress_pct = int((completed_q / total_q) * 100) if total_q > 0 else 0
    
    st.markdown(f"**整体进度: {completed_q} / {total_q} ({progress_pct}%)**")
    st.progress(progress_pct / 100.0)
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    for i, cat in enumerate(categories):
        cat_total = len(cat.get("questions", []))
        cat_completed = sum(1 for q in cat.get("questions", []) if q["id"] in completed_set)
        
        with (col1 if i % 2 == 0 else col2):
            with st.expander(f"📁 {cat['name']} ({cat_completed}/{cat_total})", expanded=(i == 0)):
                for q in cat.get("questions", []):
                    # Checkbox
                    is_done = q["id"] in completed_set
                    
                    diff_color = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}.get(q.get("difficulty", "easy"), "⚪")
                    
                    def toggle_completion(qid=q["id"]):
                        if not user_email:
                            st.error("请先登录！")
                            return
                        # reload profile_data to avoid stale state
                        try:
                            from data.daily_learning import daily_learning
                            pd = daily_learning.get_user_profile(user_email)
                            if pd and "progress" in pd:
                                current_completed = pd["progress"].get("completed_questions", [])
                                if qid in current_completed:
                                    current_completed.remove(qid)
                                else:
                                    current_completed.append(qid)
                                pd["progress"]["completed_questions"] = current_completed
                                daily_learning._save_user_data(user_email, pd)
                        except Exception as e:
                            st.error(f"Save failed: {e}")

                    # Render link + checkbox
                    cols = st.columns([1, 8])
                    with cols[0]:
                        st.checkbox("", value=is_done, key=f"cb_{q['id']}", on_change=toggle_completion, kwargs={"qid": q["id"]})
                    with cols[1]:
                        st.markdown(f"[{diff_color} {q['name']}]({q['url']})")


def render_question_list(questions_list, page_key="page"):
    """Helper function to render a paginated list of questions with full detail."""
    if not questions_list:
        st.info("没有符合条件的题目")
        return
        
    st.markdown(f"**共 {len(questions_list)} 道题目**")
    
    # Pagination Setup
    questions_per_page = 10
    total_pages = max(1, (len(questions_list) - 1) // questions_per_page + 1)
    
    if page_key not in st.session_state:
        st.session_state[page_key] = 1
        
    if st.session_state[page_key] > total_pages:
        st.session_state[page_key] = 1
        
    current_page = st.session_state[page_key]
    start_idx = (current_page - 1) * questions_per_page
    end_idx = start_idx + questions_per_page
    
    current_page_questions = questions_list[start_idx:end_idx]
    
    for i, q in enumerate(current_page_questions):
        freq = q.get("frequency", 0)
        freq_badge = "🔥" * min(freq, 5)
        
        difficulty_colors = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}
        diff_icon = difficulty_colors.get(q.get("difficulty", ""), "⚪")
        
        domain_icons = {
            "fundamentals": "📗", "deep_learning": "🔮", "nlp": "📝",
            "cv": "👁️", "recsys": "🎯", "ranking": "📈",
            "llm": "🤖", "mlops": "⚙️", "experimentation": "🧪"
        }
        domain_icon = domain_icons.get(q.get("domain", ""), "📚")
        
        with st.expander(
            f"{freq_badge} {diff_icon} [{q.get('company', 'Unknown')}] **{q.get('question', '')[:70]}{'...' if len(q.get('question', '')) > 70 else ''}**",
            expanded=i < 2
        ):
            # Meta info row
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.markdown(f"🏢 **{q.get('company', '')}**")
            with col2:
                st.markdown(f"📊 **{q.get('level', '')}**")
            with col3:
                st.markdown(f"{domain_icon} **{q.get('domain', '').replace('_', ' ').title()}**")
            with col4:
                st.markdown(f"🔥 高频度: **{freq}/5**")
            with col5:
                added_date = q.get("created_at", "")[:10] or str(q.get("year", ""))
                st.markdown(f"📅 **{added_date}**")
            
            st.markdown("---")
            
            # Full question
            st.markdown("### 📝 题目")
            st.markdown(q.get("question", ""))
            
            # Round type
            round_names = {
                "phone_screen": "📞 Phone Screen",
                "coding": "💻 Coding",
                "ml_coding": "🐍 ML Coding 实现",
                "ml_theory": "📖 ML 理论深度",
                "ml_system_design": "🏗️ ML 系统设计",
                "system_design": "🌐 通用系统设计",
                "behavioral": "🗣️ 行为面试"
            }
            st.markdown(f"**轮次**: {round_names.get(q.get('round', ''), q.get('round', ''))}")
            
            # Answer
            st.markdown("### 💡 参考答案 / 面经摘要")
            answer = q.get("answer", "")
            if isinstance(answer, list):
                if len(answer) > 0 and answer[0].startswith("```python") and answer[-1].endswith("```"):
                    answer_text = "\n".join(answer[1:-1])
                    st.code(answer_text, language="python")
                else:
                    answer_text = "\n".join(answer)
                    st.markdown(answer_text)
            elif isinstance(answer, str) and answer.startswith("```"):
                st.code(answer.replace("```python", "").replace("```", ""), language="python")
            else:
                st.markdown(str(answer))
            
            # Follow-ups
            if q.get("follow_ups"):
                st.markdown("### 🔄 常见追问")
                for fu in q.get("follow_ups", []):
                    st.markdown(f"- {fu}")
            
            # Common mistakes
            if q.get("common_mistakes"):
                st.markdown("### ⚠️ 常见错误")
                for cm in q.get("common_mistakes", []):
                    st.error(f"❌ {cm}")
            
            # Tags
            if q.get("tags"):
                tags_str = " ".join([f"`{tag}`" for tag in q.get("tags", [])])
                st.markdown(f"**🏷️ 标签**: {tags_str}")
            
            # Review Progress
            st.markdown("---")
            question_id = get_question_id(q)
            st.markdown("### 📈 复习记录")
            user_id = st.session_state.get("user_email", "guest")
            
            try:
                from data.review_records import get_review_stats, record_question_review
                user_reviews = get_review_stats(user_id)
                q_record = user_reviews.get("details", {}).get(question_id, {})
                mastery = q_record.get("mastery_score", 0)
                
                if mastery >= 80:
                    status_text = "🟢 已掌握"
                elif mastery >= 40:
                    status_text = "🟡 需复习"
                elif q_record.get("history"):
                    status_text = "🔴 不熟练"
                else:
                    status_text = "⚪ 未复习"
                    
                st.caption(f"当前熟练度: {status_text} (Score: {mastery})")
                
                col_a, col_b, col_c = st.columns(3)
                q_title = q.get('question', '')[:50]
                if col_a.button("🟢 掌握", key=f"rev_e_{page_key}_{question_id}"):
                    record_question_review(user_id, question_id, "easy", q_title)
                    st.success("已标记！")
                    st.rerun()
                if col_b.button("🟡 复习", key=f"rev_m_{page_key}_{question_id}"):
                    record_question_review(user_id, question_id, "medium", q_title)
                    st.warning("进入待复习！")
                    st.rerun()
                if col_c.button("🔴 重刷", key=f"rev_h_{page_key}_{question_id}"):
                    record_question_review(user_id, question_id, "hard", q_title)
                    st.error("标记为难点！")
                    st.rerun()
            except ImportError:
                pass
                
            # Community
            st.markdown("---")
            qa_data = load_question_answers(question_id)
            num_answers = len(qa_data.get("answers", []))
            
            with st.expander(f"💬 社区讨论/笔记 ({num_answers})", expanded=False):
                render_community_answers(question_id, q.get("question", ""), context_key=page_key)
        
    # Render Pagination Controls
    if total_pages > 1:
        st.markdown("---")
        c1, c2, c3 = st.columns([1, 2, 1])
        
        with c1:
            if st.button("⬅️ 上一页", disabled=(current_page == 1), use_container_width=True, key=f"prev_{page_key}"):
                st.session_state[page_key] -= 1
                st.rerun()
                
        with c2:
            st.markdown(f"<div style='text-align: center; padding-top: 8px;'>第 <b>{current_page}</b> 页 / 共 <b>{total_pages}</b> 页</div>", unsafe_allow_html=True)
            
        with c3:
            if st.button("下一页 ➡️", disabled=(current_page == total_pages), use_container_width=True, key=f"next_{page_key}"):
                st.session_state[page_key] += 1
                st.rerun()


def render_interview_questions():
    """Main entry for Interview Questions module. Delegates to render_mle_questions which handles the 3-tab layout."""
    st.markdown("## 📚 面试题库大厅")
    render_mle_questions()
