"""
My Story Bank Component
UI for users to manage their personal experiences/stories for behavioral & project interviews.
Uses STAR format (Situation, Task, Action, Result).
Supports AI-powered story optimization and Supabase persistence.
"""
import streamlit as st
import sys
import os
from pathlib import Path
from typing import Dict

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from data.user_story_bank import user_story_bank, STORY_CATEGORIES, COMMON_BQ_QUESTIONS


# ============ AI Story Optimizer ============

def ai_optimize_story(story: Dict) -> Dict:
    """Use Gemini to polish a STAR story for interview delivery."""
    try:
        import google.generativeai as genai
        api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", "")
        if not api_key:
            return {"error": "未配置 GEMINI_API_KEY"}
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        prompt = f"""你是一位顶级面试教练，擅长帮助候选人优化 Behavioral Interview 的 STAR 故事。

请根据以下用户输入的原始经历，优化成面试中可以直接使用的高质量 STAR 格式回答。

要求:
1. 用第一人称 "I"，不用 "we" (除非描述团队背景)
2. 每个部分都要具体、有数字、有细节
3. Action 部分是重点，要展示你的个人贡献和思考过程
4. Result 部分必须有量化数据
5. 整体控制在 2-3 分钟口述长度 (约 300-500 字英文)
6. 语言专业但不要太正式，像在和面试官对话
7. 如果原文是中文，请同时提供中文优化版和英文面试版

用户原始输入:
- 标题: {story.get('title', '')}
- 公司/角色: {story.get('company', '')} / {story.get('role', '')}
- Situation: {story.get('situation', '(未填写)')}
- Task: {story.get('task', '(未填写)')}
- Action: {story.get('action', '(未填写)')}
- Result: {story.get('result', '(未填写)')}
- Key Metrics: {story.get('metrics', '(未填写)')}
- 备注: {story.get('notes', '')}

请用以下格式返回:

## 🌍 Situation (优化版)
[优化后的内容]

## 🎯 Task (优化版)
[优化后的内容]

## ⚡ Action (优化版)
[优化后的内容，用编号列出关键步骤]

## 🏆 Result (优化版)
[优化后的内容，突出量化数据]

## 📊 建议的 Key Metrics
[提炼出最impactful的数字]

## 💡 面试 Tips
- [针对这个故事的面试建议]
- [可能的追问及准备方向]

## 🇺🇸 English Version (面试用)
[完整的英文面试版本]
"""
        
        response = model.generate_content(prompt)
        return {"success": True, "optimized_text": response.text}
    
    except Exception as e:
        return {"error": str(e)}


# ============ Main UI ============

def render_story_bank():
    """Main entry point for the story bank page."""
    
    user_id = st.session_state.get("user_email", "guest")
    
    st.markdown("## 📖 我的故事库 (My Story Bank)")
    st.markdown("*用 STAR 格式整理你的个人经历，AI 帮你优化成面试可用的高质量回答。所有内容存储在你的个人数据库中。*")
    
    # Stats
    stats = user_story_bank.get_stats(user_id)
    cols = st.columns(4)
    with cols[0]:
        st.metric("📖 故事总数", stats["total"])
    with cols[1]:
        st.metric("📂 覆盖分类", len(stats["categories"]))
    with cols[2]:
        st.metric("🏢 涉及公司", len(stats["companies"]))
    with cols[3]:
        coverage = min(100, int(len(stats["categories"]) / len(STORY_CATEGORIES) * 100))
        st.metric("✅ 覆盖率", f"{coverage}%")
    
    st.markdown("---")
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs([
        "📝 添加故事", 
        "📂 我的故事 (查看/编辑/AI优化)", 
        "🎯 BQ 题库 & 匹配"
    ])
    
    with tab1:
        render_add_story(user_id)
    
    with tab2:
        render_my_stories(user_id)
    
    with tab3:
        render_bq_matcher(user_id)


def render_add_story(user_id: str):
    """Render the add story form with STAR format."""
    
    st.markdown("### ✏️ 用 STAR 格式记录你的经历")
    st.markdown("""
    > **S**ituation（背景）→ **T**ask（任务）→ **A**ction（行动）→ **R**esult（结果）
    > 
    > 💡 先粗略写下来，之后可以用 AI 帮你优化成面试标准版本！
    """)
    
    with st.form("add_story_form", clear_on_submit=True):
        # Basic info
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("🏷️ 故事标题 *", placeholder="例: 重构推荐系统提升CTR 15%")
            company = st.text_input("🏢 公司", placeholder="例: Google, 某创业公司")
        with col2:
            category = st.selectbox("📂 分类 *", 
                options=list(STORY_CATEGORIES.keys()),
                format_func=lambda x: STORY_CATEGORIES[x]
            )
            role = st.text_input("💼 你的角色", placeholder="例: Tech Lead, Senior MLE")
        
        st.markdown("---")
        st.markdown("#### ⭐ STAR 格式 (先写草稿，后续可 AI 优化)")
        
        situation = st.text_area(
            "🌍 **S**ituation（背景/情境）",
            placeholder="描述当时的背景、团队情况、面临的挑战...\n\n例: 我们团队负责的推荐系统 CTR 持续下降了 3 个月，DAU 从 500 万降到了 400 万...",
            height=100
        )
        
        task = st.text_area(
            "🎯 **T**ask（你的任务/目标）",
            placeholder="你具体需要完成什么任务？你的职责是什么？\n\n例: 作为 Tech Lead，我需要在 6 周内找到 CTR 下降的根因并提出解决方案...",
            height=80
        )
        
        action = st.text_area(
            "⚡ **A**ction（你的具体行动）",
            placeholder="你做了什么？（用第一人称 'I'）\n\n例: 1. 我首先分析了 3 个月的数据日志...\n2. 我提出了新的 feature engineering 方案...",
            height=120
        )
        
        result = st.text_area(
            "🏆 **R**esult（成果/结果）",
            placeholder="量化的结果是什么？有什么影响？\n\n例: CTR 提升了 15%，DAU 回升到 550 万...",
            height=80
        )
        
        metrics = st.text_input(
            "📊 关键数字 (Key Metrics)",
            placeholder="例: CTR +15%, 延迟 -40%, DAU +10%, 节省 $200K/月"
        )
        
        st.markdown("---")
        
        tags = st.text_input("🏷️ 标签", placeholder="用逗号分隔: ML, 推荐系统, 性能优化")
        
        applicable = st.multiselect(
            "🎯 可回答哪些 BQ 题目？",
            options=COMMON_BQ_QUESTIONS,
            help="选择这个故事可以用来回答的常见 Behavioral Questions"
        )
        
        notes = st.text_area("📝 额外备注", placeholder="面试时要注意的点，容易被追问的地方...", height=60)
        
        if st.form_submit_button("💾 保存故事", type="primary"):
            if title and (situation or action):
                story_data = {
                    "title": title,
                    "category": category,
                    "company": company,
                    "role": role,
                    "situation": situation,
                    "task": task,
                    "action": action,
                    "result": result,
                    "metrics": metrics,
                    "tags": [t.strip() for t in tags.split(",") if t.strip()],
                    "applicable_questions": applicable,
                    "notes": notes,
                }
                story_id = user_story_bank.add_story(user_id, story_data)
                st.success(f"✅ 故事已保存！去「我的故事」Tab 可以用 AI 优化它。（ID: {story_id}）")
                st.balloons()
            else:
                st.error("请至少填写标题和 Situation/Action 中的一项")


def render_my_stories(user_id: str):
    """Render the user's saved stories with edit and AI optimize."""
    
    st.markdown("### 📂 我的故事库")
    st.caption("点击任意故事展开 → 可以编辑、删除、或让 AI 帮你优化。")
    
    stories = user_story_bank.get_all_stories(user_id)
    
    if not stories:
        st.info("📭 你的故事库还是空的！去「添加故事」Tab 录入你的第一个经历吧。")
        st.markdown("""
        **💡 建议**: 每个人至少准备 **8-10 个** 覆盖不同维度的故事：
        - 2-3 个项目经历（含一个最自豪的）
        - 1-2 个领导力/推动变革的故事
        - 1 个失败并从中学习的故事
        - 1 个冲突/分歧解决的故事
        - 1-2 个时间压力/模糊场景的故事
        """)
        return
    
    st.caption(f"共 {len(stories)} 个故事")
    
    for idx, story in enumerate(stories):
        _render_story_card_with_actions(story, user_id, idx)


def _render_story_card_with_actions(story: Dict, user_id: str, idx: int):
    """Render a story card with edit, delete, and AI optimize actions."""
    cat_icon = STORY_CATEGORIES.get(story.get("category", "other"), "📁").split(" ")[0]
    story_id = story.get("id", f"idx_{idx}")
    
    with st.expander(
        f"{cat_icon} **{story.get('title', 'Untitled')}** — {story.get('company', '')} ({story.get('role', '')})",
        expanded=False
    ):
        # Metrics highlight
        if story.get("metrics"):
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #065f46, #047857); padding: 0.5rem 1rem; 
                        border-radius: 8px; margin-bottom: 0.75rem;">
                <p style="margin: 0; color: #a7f3d0; font-size: 0.8rem;">📊 KEY METRICS</p>
                <p style="margin: 0; color: #ecfdf5; font-weight: 600;">{story.get('metrics')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # STAR sections
        for label, icon, key, color in [
            ("Situation", "🌍", "situation", "#3b82f6"),
            ("Task", "🎯", "task", "#f59e0b"),
            ("Action", "⚡", "action", "#8b5cf6"),
            ("Result", "🏆", "result", "#10b981"),
        ]:
            content = story.get(key, "")
            if content:
                st.markdown(f"""
                <div style="border-left: 3px solid {color}; padding-left: 0.75rem; margin-bottom: 0.5rem;">
                    <p style="margin: 0; color: {color}; font-size: 0.8rem; font-weight: 600;">{icon} {label}</p>
                    <p style="margin: 0.25rem 0; color: #e2e8f0;">{content}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # AI optimized version (if exists)
        if story.get("ai_optimized"):
            st.markdown("---")
            st.markdown("#### 🤖 AI 优化版本")
            st.markdown(story["ai_optimized"])
        
        # Tags
        if story.get("tags"):
            tag_html = " ".join([f'<span style="background: #334155; padding: 0.15rem 0.5rem; border-radius: 8px; font-size: 0.75rem; margin-right: 0.25rem;">{t}</span>' for t in story["tags"]])
            st.markdown(f"🏷️ {tag_html}", unsafe_allow_html=True)
        
        if story.get("applicable_questions"):
            st.markdown("**🎯 可回答的 BQ:**")
            for q in story["applicable_questions"]:
                st.markdown(f"- {q}")
        
        if story.get("notes"):
            st.info(f"📝 **备注:** {story['notes']}")
        
        st.caption(f"创建: {story.get('created_at', '')[:16]} | 更新: {story.get('updated_at', '')[:16]}")
        
        st.markdown("---")
        
        # ============ Action Buttons ============
        col_ai, col_edit, col_delete = st.columns(3)
        
        with col_ai:
            if st.button("🤖 AI 优化", key=f"ai_opt_{story_id}", type="primary", use_container_width=True):
                with st.spinner("AI 正在分析并优化你的故事... (约 10 秒)"):
                    result = ai_optimize_story(story)
                    if result.get("success"):
                        user_story_bank.update_story(user_id, story_id, {
                            "ai_optimized": result["optimized_text"]
                        })
                        st.success("✅ AI 优化完成！")
                        st.rerun()
                    else:
                        st.error(f"优化失败: {result.get('error', 'Unknown')}")
        
        with col_edit:
            if st.button("✏️ 编辑", key=f"edit_btn_{story_id}", use_container_width=True):
                st.session_state[f"editing_{story_id}"] = True
                st.rerun()
        
        with col_delete:
            if st.button("🗑️ 删除", key=f"del_btn_{story_id}", use_container_width=True):
                st.session_state[f"confirm_delete_{story_id}"] = True
                st.rerun()
        
        # ============ Delete Confirmation ============
        if st.session_state.get(f"confirm_delete_{story_id}"):
            st.warning(f"⚠️ 确定要删除「{story.get('title')}」吗？此操作不可撤销！")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ 确认删除", key=f"confirm_del_{story_id}"):
                    user_story_bank.delete_story(user_id, story_id)
                    del st.session_state[f"confirm_delete_{story_id}"]
                    st.success("已删除！")
                    st.rerun()
            with c2:
                if st.button("❌ 取消", key=f"cancel_del_{story_id}"):
                    del st.session_state[f"confirm_delete_{story_id}"]
                    st.rerun()
        
        # ============ Edit Form ============
        if st.session_state.get(f"editing_{story_id}"):
            st.markdown("#### ✏️ 编辑故事")
            with st.form(f"edit_form_{story_id}"):
                edit_title = st.text_input("标题", value=story.get("title", ""), key=f"et_{story_id}")
                
                e_col1, e_col2 = st.columns(2)
                with e_col1:
                    edit_company = st.text_input("公司", value=story.get("company", ""), key=f"ec_{story_id}")
                with e_col2:
                    edit_role = st.text_input("角色", value=story.get("role", ""), key=f"er_{story_id}")
                
                edit_situation = st.text_area("Situation", value=story.get("situation", ""), height=80, key=f"es_{story_id}")
                edit_task = st.text_area("Task", value=story.get("task", ""), height=60, key=f"etk_{story_id}")
                edit_action = st.text_area("Action", value=story.get("action", ""), height=100, key=f"ea_{story_id}")
                edit_result = st.text_area("Result", value=story.get("result", ""), height=60, key=f"erl_{story_id}")
                edit_metrics = st.text_input("Key Metrics", value=story.get("metrics", ""), key=f"em_{story_id}")
                edit_notes = st.text_area("备注", value=story.get("notes", ""), height=60, key=f"en_{story_id}")
                
                e_submit, e_cancel = st.columns(2)
                with e_submit:
                    if st.form_submit_button("💾 保存修改", type="primary"):
                        updates = {
                            "title": edit_title,
                            "company": edit_company,
                            "role": edit_role,
                            "situation": edit_situation,
                            "task": edit_task,
                            "action": edit_action,
                            "result": edit_result,
                            "metrics": edit_metrics,
                            "notes": edit_notes,
                        }
                        user_story_bank.update_story(user_id, story_id, updates)
                        del st.session_state[f"editing_{story_id}"]
                        st.success("✅ 已保存修改！")
                        st.rerun()


def render_bq_matcher(user_id: str):
    """Show common BQ questions and match them with user's stories."""
    
    st.markdown("### 🎯 BQ 题库 & 故事匹配")
    st.markdown("*常见 Behavioral Questions，检查你的故事库是否覆盖了这些高频题。*")
    
    stories = user_story_bank.get_all_stories(user_id)
    
    # Build reverse index: question -> stories
    question_story_map = {}
    for s in stories:
        for q in s.get("applicable_questions", []):
            if q not in question_story_map:
                question_story_map[q] = []
            question_story_map[q].append(s)
    
    covered = 0
    total = len(COMMON_BQ_QUESTIONS)
    
    for q in COMMON_BQ_QUESTIONS:
        matched = question_story_map.get(q, [])
        if matched:
            covered += 1
            st.markdown(f"""
            <div style="background: #1e293b; padding: 0.75rem; border-radius: 8px; margin-bottom: 0.5rem;
                        border-left: 3px solid #10b981;">
                <p style="margin: 0; color: #f1f5f9;"><strong>✅ {q}</strong></p>
                <p style="margin: 0.25rem 0 0 0; color: #6ee7b7; font-size: 0.8rem;">
                    已匹配 {len(matched)} 个故事: {', '.join(s.get('title', '')[:30] for s in matched)}
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background: #1e293b; padding: 0.75rem; border-radius: 8px; margin-bottom: 0.5rem;
                        border-left: 3px solid #ef4444;">
                <p style="margin: 0; color: #f1f5f9;"><strong>❌ {q}</strong></p>
                <p style="margin: 0.25rem 0 0 0; color: #fca5a5; font-size: 0.8rem;">
                    ⚠️ 尚无匹配故事 — 建议去「添加故事」补充！
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    # Coverage summary
    pct = int(covered / total * 100) if total else 0
    color = "#10b981" if pct >= 80 else "#f59e0b" if pct >= 50 else "#ef4444"
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1e293b, #334155); padding: 1rem; border-radius: 12px; 
                margin-top: 1rem; text-align: center;">
        <p style="margin: 0; color: #94a3b8; font-size: 0.9rem;">BQ 覆盖率</p>
        <p style="margin: 0; color: {color}; font-size: 2rem; font-weight: 700;">{pct}%</p>
        <p style="margin: 0; color: #64748b;">{covered}/{total} 个常见问题已准备故事</p>
    </div>
    """, unsafe_allow_html=True)
