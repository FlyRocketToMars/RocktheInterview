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


def render_community_answers(question_id: str, question_text: str):
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
                    
                    if st.button("👍", key=f"up_{question_id}_{ans['id']}"):
                        vote_answer(question_id, ans["id"], True)
                        st.rerun()
                    
                    st.markdown(f"**{score}**")
                    
                    if st.button("👎", key=f"down_{question_id}_{ans['id']}"):
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
    
    with st.form(f"answer_form_{question_id}"):
        user_answer = st.text_area(
            "你的回答",
            height=150,
            placeholder="分享你的解题思路、面试经验或补充内容...",
            key=f"answer_input_{question_id}"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            author_name = st.text_input("你的昵称", value=st.session_state.get("username", ""), key=f"author_{question_id}")
        with col2:
            anonymous = st.checkbox("匿名提交", key=f"anon_{question_id}")
        
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
    metadata = data.get("metadata", {})
    categories = data.get("categories", {})
    
    if not questions:
        st.warning("题库暂无数据")
        return
    
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
    
    # ============ Filters ============
    st.markdown("### 🔍 智能筛选")
    
    col1, col2, col3 = st.columns(3)
    
    # Get unique values
    companies_list = sorted(set(q.get("company", "") for q in questions))
    domains_list = categories.get("domains", [])
    rounds_list = categories.get("rounds", [])
    levels_list = categories.get("levels", [])
    
    # Get user target company for default selection
    try:
        from components.auth import get_current_user
        from data.daily_learning import daily_learning
        user_email = get_current_user()
        user_target = "全部"
        user_level = "全部"
        if user_email:
            profile_data = daily_learning.get_user_profile(user_email)
            if profile_data and "profile" in profile_data:
                user_target = profile_data["profile"].get("target_company", "全部")
                user_level = profile_data["profile"].get("target_level", "全部")
    except:
        user_target = "全部"
        user_level = "全部"
        
    company_options = ["全部"] + companies_list
    default_company_index = 0
    if user_target in company_options:
        default_company_index = company_options.index(user_target)
        
    level_options = ["全部"] + levels_list
    default_level_index = 0
    
    # Try to match the user's exact level strings, e.g., "L5" with "L5/Senior"
    if user_level != "全部":
        for i, lvl in enumerate(level_options):
            if str(lvl).lower().startswith(str(user_level).lower()):
                default_level_index = i
                break
    
    with col1:
        selected_company = st.selectbox(
            "🏢 目标公司",
            company_options,
            index=default_company_index,
            key="filter_company_v2"
        )
        
        selected_domain = st.selectbox(
            "🧠 知识领域",
            ["全部"] + domains_list,
            format_func=lambda x: {
                "全部": "全部领域",
                "fundamentals": "📗 ML 基础",
                "deep_learning": "🔮 深度学习",
                "nlp": "📝 NLP",
                "cv": "👁️ 计算机视觉",
                "recsys": "🎯 推荐系统",
                "ranking": "📈 搜索排序",
                "llm": "🤖 大语言模型",
                "mlops": "⚙️ MLOps",
                "experimentation": "🧪 实验平台"
            }.get(x, x),
            key="filter_domain"
        )
    
    with col2:
        selected_round = st.selectbox(
            "📋 面试轮次",
            ["全部"] + rounds_list,
            format_func=lambda x: {
                "全部": "全部轮次",
                "phone_screen": "📞 Phone Screen",
                "coding": "💻 Coding",
                "ml_coding": "🐍 ML Coding",
                "ml_theory": "📖 ML 理论",
                "ml_system_design": "🏗️ ML 系统设计",
                "system_design": "🌐 通用系统设计",
                "behavioral": "🗣️ 行为面试"
            }.get(x, x),
            key="filter_round_v2"
        )
        
        selected_level = st.selectbox(
            "📊 目标级别",
            level_options,
            index=default_level_index,
            key="filter_level"
        )
    
    with col3:
        selected_difficulty = st.selectbox(
            "⭐ 难度",
            ["全部", "easy", "medium", "hard"],
            format_func=lambda x: {
                "全部": "全部难度",
                "easy": "🟢 Easy (入门)",
                "medium": "🟡 Medium (标准)",
                "hard": "🔴 Hard (挑战)"
            }.get(x, x),
            key="filter_difficulty_v2"
        )
        
        min_frequency = st.slider(
            "🔥 最低高频度",
            min_value=1, max_value=5, value=1,
            help="筛选高频题目 (5=必考)"
        )
    
    # Apply filters
    filtered = questions
    if selected_company != "全部":
        filtered = [q for q in filtered if q.get("company") == selected_company]
    if selected_domain != "全部":
        filtered = [q for q in filtered if q.get("domain") == selected_domain]
    if selected_round != "全部":
        filtered = [q for q in filtered if q.get("round") == selected_round]
    if selected_level != "全部":
        filtered = [q for q in filtered if q.get("level") == selected_level]
    if selected_difficulty != "全部":
        filtered = [q for q in filtered if q.get("difficulty") == selected_difficulty]
    filtered = [q for q in filtered if q.get("frequency", 0) >= min_frequency]
    
    st.markdown(f"**筛选结果: {len(filtered)} 道题目**")
    st.markdown("---")
    
    # ============ Questions List ============
    if not filtered:
        st.info("没有符合条件的题目，请调整筛选条件")
        return
    
    # Sort by frequency then importance
    filtered = sorted(filtered, key=lambda x: (x.get("frequency", 0), x.get("importance", 0)), reverse=True)
    
    for i, q in enumerate(filtered):
        # Question header with badges
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
            f"{freq_badge} {diff_icon} **{q.get('question', '')[:70]}{'...' if len(q.get('question', '')) > 70 else ''}**",
            expanded=i < 2
        ):
            # Meta info row
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"🏢 **{q.get('company', '')}**")
            with col2:
                st.markdown(f"📊 **{q.get('level', '')}**")
            with col3:
                st.markdown(f"{domain_icon} **{q.get('domain', '').replace('_', ' ').title()}**")
            with col4:
                st.markdown(f"🔥 高频度: **{freq}/5**")
            
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
            st.markdown("### 💡 参考答案")
            answer = q.get("answer", "")
            if isinstance(answer, list):
                if len(answer) > 0 and answer[0].startswith("```python") and answer[-1].endswith("```"):
                    answer = "\n".join(answer[1:-1])
                    st.code(answer, language="python")
                else:
                    answer = "\n".join(answer)
                    st.markdown(answer)
            elif answer.startswith("```"):
                st.code(answer.replace("```python", "").replace("```", ""), language="python")
            else:
                st.markdown(answer)
            
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
            
            # ========== Review Progress Section ==========
            st.markdown("---")
            question_id = get_question_id(q)
            
            # Simple Review UI
            st.markdown("### 📈 复习记录")
            user_id = st.session_state.get("user_email", "guest")
            
            # Try to get existing mastery level
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
                if col_a.button("🟢 简单 (掌握)", key=f"rev_e_{question_id}"):
                    record_question_review(user_id, question_id, "easy", q_title)
                    st.success("已标记为需要较少复习！")
                    st.rerun()
                if col_b.button("🟡 中等 (复习)", key=f"rev_m_{question_id}"):
                    record_question_review(user_id, question_id, "medium", q_title)
                    st.warning("已添加进待复习列表！")
                    st.rerun()
                if col_c.button("🔴 困难 (重刷)", key=f"rev_h_{question_id}"):
                    record_question_review(user_id, question_id, "hard", q_title)
                    st.error("已标记为重点难点！")
                    st.rerun()
            except ImportError:
                pass
            
            # ========== Community Answers Section ==========
            st.markdown("---")
            qa_data = load_question_answers(question_id)
            num_answers = len(qa_data.get("answers", []))
            
            with st.expander(f"💬 社区回答 ({num_answers})", expanded=False):
                render_community_answers(question_id, q.get("question", ""))
    
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
    """Render the Neetcode 250 coding practice tracker."""
    st.markdown("### 💻 Neetcode 算法高频 250")
    st.markdown("*精选互联网大厂最常考的 250 道算法题，分门别类，针对性刷题。*")
    
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


def render_interview_questions():
    """Main entry for Interview Questions module."""
    st.markdown("## 📚 面试题库大厅")
    
    tab1, tab2 = st.tabs(["🧠 MLE 专业系统设计题库", "💻 算法代码区 (Neetcode)"])
    
    with tab1:
        render_mle_questions()
        
    with tab2:
        render_neetcode_tracker()
