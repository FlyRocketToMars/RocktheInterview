"""
Resume Analyzer Component
AI-powered resume review, JD matching, and bullet point optimization.
"""
import streamlit as st
import sys
import re
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


# ============ Resume Data Store (Supabase + local fallback) ============
import json

LOCAL_RESUME_FILE = Path(__file__).parent.parent.parent / "data" / "user_resumes.json"

def _ensure_file():
    if not LOCAL_RESUME_FILE.exists():
        LOCAL_RESUME_FILE.write_text('{}', encoding='utf-8')

def save_resume(user_id: str, resume_text: str, analysis: dict = None):
    _ensure_file()
    data = json.loads(LOCAL_RESUME_FILE.read_text(encoding='utf-8'))
    data[user_id] = {
        "resume_text": resume_text,
        "analysis": analysis,
        "updated_at": datetime.now().isoformat()
    }
    LOCAL_RESUME_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')

def load_resume(user_id: str):
    _ensure_file()
    data = json.loads(LOCAL_RESUME_FILE.read_text(encoding='utf-8'))
    return data.get(user_id, {})


# ============ Analysis Engine ============

WEAK_VERBS = [
    "responsible for", "worked on", "helped", "assisted", "participated",
    "involved in", "contributed to", "did", "was part of", "used", "made",
    "handled", "managed", "dealt with"
]

STRONG_VERBS = [
    "Architected", "Engineered", "Spearheaded", "Pioneered", "Optimized",
    "Accelerated", "Automated", "Delivered", "Scaled", "Launched",
    "Reduced", "Increased", "Improved", "Designed", "Implemented",
    "Led", "Drove", "Transformed", "Built", "Deployed"
]

FAANG_KEYWORDS = {
    "ml_core": ["machine learning", "deep learning", "neural network", "model training",
                "feature engineering", "loss function", "gradient descent", "hyperparameter"],
    "mlops": ["mlops", "ci/cd", "deployment", "monitoring", "a/b test", "experiment",
              "pipeline", "data pipeline", "airflow", "kubeflow"],
    "systems": ["distributed", "scalable", "latency", "throughput", "real-time",
                "batch processing", "streaming", "microservice"],
    "impact": ["revenue", "cost", "engagement", "retention", "conversion",
               "accuracy", "precision", "recall", "auc", "f1"],
    "leadership": ["led", "mentored", "cross-functional", "stakeholder",
                   "roadmap", "strategy", "initiative", "ownership"],
    "tools": ["python", "tensorflow", "pytorch", "spark", "sql", "aws", "gcp",
              "docker", "kubernetes", "ray", "huggingface"]
}


def analyze_resume(resume_text: str, jd_text: str = "") -> dict:
    """Analyze resume and return structured feedback."""
    lines = [l.strip() for l in resume_text.split("\n") if l.strip()]
    bullets = [l for l in lines if l.startswith(("•", "-", "·", "*")) or 
               (len(l) > 20 and any(l.startswith(v) for v in STRONG_VERBS + [v.lower() for v in STRONG_VERBS]))]
    
    if not bullets:
        bullets = [l for l in lines if len(l) > 30]
    
    # 1. Weak verb detection
    weak_verb_issues = []
    for bullet in bullets:
        for wv in WEAK_VERBS:
            if wv.lower() in bullet.lower():
                weak_verb_issues.append({"bullet": bullet[:100], "weak_verb": wv})
                break
    
    # 2. Quantification check
    quantified = 0
    unquantified = []
    for bullet in bullets:
        if re.search(r'\d+[%xX]|\$\d|\d+\s*(users|customers|queries|requests|models|teams|engineers)', bullet):
            quantified += 1
        else:
            unquantified.append(bullet[:100])
    
    quant_rate = quantified / max(len(bullets), 1) * 100
    
    # 3. FAANG keyword coverage
    resume_lower = resume_text.lower()
    keyword_coverage = {}
    for cat, keywords in FAANG_KEYWORDS.items():
        found = [kw for kw in keywords if kw in resume_lower]
        keyword_coverage[cat] = {
            "found": found,
            "missing": [kw for kw in keywords if kw not in resume_lower],
            "coverage": len(found) / len(keywords) * 100
        }
    
    overall_keyword_score = sum(v["coverage"] for v in keyword_coverage.values()) / len(keyword_coverage)
    
    # 4. Bullet length analysis
    too_long = [b[:80] + "..." for b in bullets if len(b) > 150]
    too_short = [b for b in bullets if len(b) < 30]
    
    # 5. JD Matching
    jd_match = None
    if jd_text:
        jd_lower = jd_text.lower()
        jd_words = set(re.findall(r'\b[a-z]{3,}\b', jd_lower))
        resume_words = set(re.findall(r'\b[a-z]{3,}\b', resume_lower))
        
        # Extract likely JD requirements (important terms)
        jd_important = [w for w in jd_words if w not in {
            'the', 'and', 'for', 'with', 'you', 'are', 'our', 'will',
            'have', 'this', 'that', 'from', 'they', 'been', 'has', 'can',
            'able', 'work', 'team', 'about', 'would', 'their', 'should'
        }]
        
        matched = resume_words & set(jd_important)
        jd_match = {
            "match_rate": len(matched) / max(len(jd_important), 1) * 100,
            "matched_keywords": sorted(list(matched))[:30],
            "missing_from_resume": sorted([w for w in jd_important if w not in resume_words and len(w) > 4])[:20]
        }
    
    # 6. Overall Score
    scores = {
        "action_verbs": max(0, 100 - len(weak_verb_issues) * 10),
        "quantification": quant_rate,
        "keyword_coverage": overall_keyword_score,
        "bullet_quality": max(0, 100 - len(too_long) * 5 - len(too_short) * 5),
    }
    if jd_match:
        scores["jd_match"] = jd_match["match_rate"]
    
    overall_score = sum(scores.values()) / len(scores)
    
    return {
        "overall_score": round(overall_score),
        "scores": scores,
        "total_bullets": len(bullets),
        "weak_verb_issues": weak_verb_issues,
        "unquantified_bullets": unquantified[:10],
        "quantification_rate": round(quant_rate),
        "keyword_coverage": keyword_coverage,
        "too_long_bullets": too_long,
        "too_short_bullets": too_short,
        "jd_match": jd_match,
        "suggestions": _generate_suggestions(scores, weak_verb_issues, unquantified, keyword_coverage)
    }


def _generate_suggestions(scores, weak_verbs, unquantified, keywords):
    """Generate prioritized improvement suggestions."""
    suggestions = []
    
    if scores.get("action_verbs", 100) < 70:
        suggestions.append({
            "priority": "high",
            "category": "动词优化",
            "icon": "💪",
            "text": f"发现 {len(weak_verbs)} 处弱动词。将 'responsible for' → 'Led/Architected/Delivered'",
        })
    
    if scores.get("quantification", 100) < 50:
        suggestions.append({
            "priority": "high",
            "category": "量化数据",
            "icon": "📊",
            "text": f"只有 {scores.get('quantification', 0):.0f}% 的bullet有数字。目标: 80%+。添加: 提升X%, 处理Y万数据, 节省$Z"
        })
    
    for cat, info in keywords.items():
        if info["coverage"] < 30:
            cat_names = {
                "ml_core": "ML核心技术", "mlops": "MLOps/工程",
                "systems": "系统/架构", "impact": "量化Impact",
                "leadership": "领导力/协作", "tools": "技术栈"
            }
            suggestions.append({
                "priority": "medium",
                "category": f"关键词: {cat_names.get(cat, cat)}",
                "icon": "🔑",
                "text": f"缺少关键词: {', '.join(info['missing'][:5])}"
            })
    
    if not suggestions:
        suggestions.append({
            "priority": "low",
            "category": "整体评价",
            "icon": "✅",
            "text": "你的简历已经很强了！继续保持量化和强动词。"
        })
    
    return suggestions


# ============ UI ============

def render_resume_analyzer():
    """Main entry point for resume analyzer."""
    user_id = st.session_state.get("user_email", "guest")
    
    st.markdown("## 📄 简历分析 & 优化")
    st.markdown("*AI 帮你按 FAANG 标准评审简历，提供量化评分和具体优化建议。*")
    
    tabs = st.tabs(["📝 简历评审", "🎯 JD 匹配", "💪 Bullet 优化器", "📋 模板参考"])
    
    with tabs[0]:
        render_resume_review(user_id)
    
    with tabs[1]:
        render_jd_matcher(user_id)
    
    with tabs[2]:
        render_bullet_optimizer()
    
    with tabs[3]:
        render_templates()


def render_resume_review(user_id: str):
    """Resume review tab."""
    st.markdown("### 📝 上传/粘贴你的简历")
    
    # Load saved resume
    saved = load_resume(user_id)
    
    input_method = st.radio("输入方式", ["📋 粘贴文本", "📎 上传文件"], horizontal=True, key="resume_input_method")
    
    resume_text = ""
    
    if input_method == "📋 粘贴文本":
        resume_text = st.text_area(
            "粘贴简历全文",
            value=saved.get("resume_text", ""),
            height=300,
            placeholder="粘贴你的简历内容...\n\n支持纯文本格式，建议从Word/Google Docs中复制粘贴。"
        )
    else:
        uploaded = st.file_uploader("上传简历 (TXT/PDF)", type=["txt", "pdf"], key="resume_upload")
        if uploaded:
            if uploaded.name.endswith(".txt"):
                resume_text = uploaded.getvalue().decode("utf-8")
            elif uploaded.name.endswith(".pdf"):
                try:
                    from components.utils import parse_pdf
                    resume_text = parse_pdf(uploaded.getvalue())
                except:
                    st.error("PDF解析失败，请改用粘贴文本方式")
    
    if st.button("🔍 开始分析", type="primary", disabled=not resume_text):
        with st.spinner("AI 正在分析你的简历..."):
            analysis = analyze_resume(resume_text)
            save_resume(user_id, resume_text, analysis)
            st.session_state["resume_analysis"] = analysis
    
    # Show analysis
    analysis = st.session_state.get("resume_analysis") or saved.get("analysis")
    if analysis:
        _render_analysis(analysis)


def _render_analysis(analysis: dict):
    """Render analysis results."""
    
    # Overall score
    score = analysis["overall_score"]
    score_color = "#10b981" if score >= 80 else "#f59e0b" if score >= 60 else "#ef4444"
    grade = "A+" if score >= 90 else "A" if score >= 80 else "B" if score >= 70 else "C" if score >= 60 else "D"
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1e293b, #334155); padding: 1.5rem; border-radius: 16px;
                text-align: center; margin: 1rem 0;">
        <p style="margin: 0; color: #94a3b8; font-size: 1rem;">FAANG 简历评分</p>
        <p style="margin: 0; color: {score_color}; font-size: 3.5rem; font-weight: 800;">{score}/100</p>
        <p style="margin: 0; color: {score_color}; font-size: 1.2rem;">Grade: {grade}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Dimension scores
    scores = analysis.get("scores", {})
    dims = st.columns(len(scores))
    dim_names = {
        "action_verbs": ("💪", "动词力度"),
        "quantification": ("📊", "量化程度"),
        "keyword_coverage": ("🔑", "关键词"),
        "bullet_quality": ("📝", "格式质量"),
        "jd_match": ("🎯", "JD匹配")
    }
    
    for col, (key, val) in zip(dims, scores.items()):
        icon, name = dim_names.get(key, ("📌", key))
        color = "#10b981" if val >= 80 else "#f59e0b" if val >= 60 else "#ef4444"
        with col:
            st.markdown(f"""
            <div style="background: #1e293b; padding: 0.75rem; border-radius: 12px; text-align: center;">
                <p style="margin: 0; font-size: 1.5rem;">{icon}</p>
                <p style="margin: 0; color: {color}; font-size: 1.5rem; font-weight: 700;">{val:.0f}</p>
                <p style="margin: 0; color: #94a3b8; font-size: 0.8rem;">{name}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Suggestions
    st.markdown("### 🎯 优化建议（按优先级排序）")
    for sug in analysis.get("suggestions", []):
        priority_color = {"high": "#ef4444", "medium": "#f59e0b", "low": "#10b981"}
        st.markdown(f"""
        <div style="background: #1e293b; padding: 0.75rem; border-radius: 8px; margin-bottom: 0.5rem;
                    border-left: 3px solid {priority_color.get(sug['priority'], '#6366f1')};">
            <p style="margin: 0; color: #f1f5f9;">
                {sug['icon']} <strong>[{sug['category']}]</strong> {sug['text']}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Weak verbs
    if analysis.get("weak_verb_issues"):
        with st.expander(f"💪 弱动词问题 ({len(analysis['weak_verb_issues'])} 处)"):
            for issue in analysis["weak_verb_issues"]:
                st.markdown(f"- ❌ *\"{issue['weak_verb']}\"* → 建议替换为强动词 (Led, Built, Optimized...)")
                st.caption(f"  原文: {issue['bullet']}")
    
    # Unquantified bullets
    if analysis.get("unquantified_bullets"):
        with st.expander(f"📊 缺少量化的 Bullet ({len(analysis['unquantified_bullets'])} 处)"):
            for bullet in analysis["unquantified_bullets"]:
                st.markdown(f"- ⚠️ {bullet}")
            st.info("💡 添加数字：提升X%, 处理Y万条数据, 服务Z万用户, 节省$W/月")
    
    # Keyword coverage
    with st.expander("🔑 FAANG 关键词覆盖分析"):
        for cat, info in analysis.get("keyword_coverage", {}).items():
            cat_names = {"ml_core": "ML核心", "mlops": "MLOps", "systems": "系统架构", 
                        "impact": "Impact量化", "leadership": "领导力", "tools": "技术栈"}
            cov = info["coverage"]
            color = "#10b981" if cov >= 60 else "#f59e0b" if cov >= 30 else "#ef4444"
            st.markdown(f"**{cat_names.get(cat, cat)}** — <span style='color:{color}'>{cov:.0f}%</span>", unsafe_allow_html=True)
            if info["found"]:
                st.caption(f"  ✅ 已有: {', '.join(info['found'])}")
            if info["missing"]:
                st.caption(f"  ❌ 缺少: {', '.join(info['missing'][:5])}")


def render_jd_matcher(user_id: str):
    """JD matching tab."""
    st.markdown("### 🎯 简历 vs JD 匹配分析")
    st.caption("粘贴目标职位的 Job Description，AI 帮你分析简历和 JD 的匹配度。")
    
    saved = load_resume(user_id)
    resume_text = saved.get("resume_text", "")
    
    if not resume_text:
        st.warning("⚠️ 请先在「简历评审」中上传你的简历")
        return
    
    st.success(f"✅ 已加载你的简历 ({len(resume_text)} 字)")
    
    jd_text = st.text_area(
        "粘贴 Job Description",
        height=200,
        placeholder="粘贴目标职位的完整JD...\n\nExample: We are looking for a Machine Learning Engineer to..."
    )
    
    if st.button("🔍 分析匹配度", type="primary", disabled=not jd_text):
        with st.spinner("正在分析匹配度..."):
            analysis = analyze_resume(resume_text, jd_text)
            
            jd_match = analysis.get("jd_match", {})
            if jd_match:
                match_rate = jd_match["match_rate"]
                color = "#10b981" if match_rate >= 70 else "#f59e0b" if match_rate >= 50 else "#ef4444"
                verdict = "非常匹配 🎉" if match_rate >= 70 else "基本匹配" if match_rate >= 50 else "匹配度较低 ⚠️"
                
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #1e293b, #334155); padding: 1.5rem; 
                            border-radius: 16px; text-align: center; margin: 1rem 0;">
                    <p style="margin: 0; color: #94a3b8;">JD 匹配度</p>
                    <p style="margin: 0; color: {color}; font-size: 3rem; font-weight: 800;">{match_rate:.0f}%</p>
                    <p style="margin: 0; color: {color};">{verdict}</p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### ✅ 已匹配的关键词")
                    for kw in jd_match.get("matched_keywords", [])[:15]:
                        st.markdown(f"- ✅ {kw}")
                
                with col2:
                    st.markdown("#### ❌ 简历中缺少的关键词")
                    for kw in jd_match.get("missing_from_resume", [])[:15]:
                        st.markdown(f"- ❌ **{kw}** — 建议添加到简历中")


def render_bullet_optimizer():
    """Bullet point optimizer tab."""
    st.markdown("### 💪 Bullet Point 优化器")
    st.caption("输入你的简历 bullet point，AI 帮你重写成 FAANG 标准。")
    
    st.markdown("""
    > **好的 Bullet Point 公式**: `强动词` + `做了什么` + `量化结果` + `使用什么技术`
    > 
    > ❌ *Responsible for building recommendation models*
    > 
    > ✅ *Architected a two-tower recommendation system using TensorFlow, improving CTR by 15% and driving $2M incremental annual revenue*
    """)
    
    bullet_input = st.text_area(
        "输入你要优化的 Bullet Point",
        height=80,
        placeholder="例: Worked on the recommendation system to improve user engagement"
    )
    
    if bullet_input:
        # Quick analysis
        has_number = bool(re.search(r'\d', bullet_input))
        starts_strong = any(bullet_input.strip().startswith(v) for v in STRONG_VERBS + [v.lower() for v in STRONG_VERBS])
        has_weak = any(wv in bullet_input.lower() for wv in WEAK_VERBS)
        
        st.markdown("#### 当前评估:")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"{'✅' if starts_strong else '❌'} 强动词开头")
        with col2:
            st.markdown(f"{'✅' if has_number else '❌'} 包含量化数据")
        with col3:
            st.markdown(f"{'✅' if not has_weak else '❌'} 无弱动词")
        
        if has_weak or not starts_strong or not has_number:
            st.markdown("#### 💡 优化建议:")
            suggestions = []
            if has_weak:
                suggestions.append(f"替换弱动词，使用: **{', '.join(STRONG_VERBS[:8])}**")
            if not has_number:
                suggestions.append("添加数字: 提升**X%**, 处理**Y万**条数据, 服务**Z万**用户")
            if not starts_strong:
                suggestions.append(f"以强动词开头: **{', '.join(STRONG_VERBS[:5])}**...")
            
            for s in suggestions:
                st.info(f"💡 {s}")
            
            # Show example rewrites
            st.markdown("#### ✏️ 参考重写:")
            rewrites = [
                f"**Engineered** [你的工作] using [技术栈], **resulting in** [X% improvement] in [指标]",
                f"**Architected** and **deployed** [系统/模型], **reducing** [latency/cost] by [X%] while **serving** [Y] users",
                f"**Led** the development of [项目], **driving** [X%] increase in [business metric] across [Z] markets"
            ]
            for r in rewrites:
                st.markdown(f"- {r}")


def render_templates():
    """Resume template reference."""
    st.markdown("### 📋 FAANG MLE 简历模板参考")
    
    st.markdown("""
    #### 📌 结构建议 (1页)
    
    ```
    ┌──────────────────────────────────────────┐
    │              姓名 | 联系方式              │
    │   Email | LinkedIn | GitHub | Portfolio   │
    ├──────────────────────────────────────────┤
    │  EXPERIENCE                               │
    │  ─────────                               │
    │  Company A | Senior MLE | 2023-Present    │
    │  • Architected X using Y, improving Z%    │
    │  • Led team of N to deliver ...           │
    │  • Reduced latency by X% through ...      │
    │                                           │
    │  Company B | MLE | 2021-2023              │
    │  • Built ...                              │
    │  • Deployed ...                           │
    ├──────────────────────────────────────────┤
    │  EDUCATION                                │
    │  ─────────                               │
    │  MS in CS | University | 2021             │
    ├──────────────────────────────────────────┤
    │  SKILLS                                   │
    │  ─────                                   │
    │  Languages: Python, C++, SQL              │
    │  ML: PyTorch, TF, Spark, Ray              │
    │  Cloud: AWS/GCP, Docker, K8s              │
    ├──────────────────────────────────────────┤
    │  PUBLICATIONS / PROJECTS (optional)        │
    └──────────────────────────────────────────┘
    ```
    """)
    
    st.markdown("---")
    
    st.markdown("""
    #### 💡 MLE 简历 Golden Rules
    
    1. **一页纸** — 除非你有 10+ 年经验
    2. **每个 bullet 都要有数字** — 没有数字 = 没有 impact
    3. **以强动词开头** — Built, Architected, Led, Optimized, Deployed
    4. **技术栈要具体** — "PyTorch" 不是 "deep learning framework"
    5. **最重要的经历放前面** — 招聘经理只看前 6 秒
    6. **不要写 Objective/Summary** — 用 headline 替代
    7. **不需要 "References available upon request"**
    8. **项目要和 JD 对齐** — 每次投不同公司都要微调
    """)
    
    st.markdown("---")
    
    st.markdown("#### 🔥 高频强动词表")
    col1, col2, col3, col4 = st.columns(4)
    verbs_by_cat = {
        "构建": ["Architected", "Built", "Designed", "Engineered", "Implemented"],
        "领导": ["Led", "Spearheaded", "Drove", "Championed", "Mentored"],
        "优化": ["Optimized", "Improved", "Accelerated", "Streamlined", "Reduced"],
        "交付": ["Deployed", "Launched", "Delivered", "Shipped", "Released"]
    }
    for col, (cat, verbs) in zip([col1, col2, col3, col4], verbs_by_cat.items()):
        with col:
            st.markdown(f"**{cat}**")
            for v in verbs:
                st.markdown(f"- {v}")
