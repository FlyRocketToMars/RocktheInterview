"""
Internationalization (i18n) Module
Multi-language support for the Interview Prep Platform
"""
import streamlit as st

# Supported languages
LANGUAGES = {
    "zh": "中文",
    "en": "English",
    "ja": "日本語",
    "ko": "한국어"
}

# Translations
TRANSLATIONS = {
    "zh": {
        # Navigation
        "nav_home": "🏠 首页",
        "nav_resume": "📄 输入简历",
        "nav_target": "🎯 选择目标",
        "nav_jd": "📋 输入JD",
        "nav_analysis": "📊 Gap分析",
        "nav_plan": "📚 学习计划",
        "nav_questions": "📖 面试题库",
        "nav_mock": "🤖 模拟面试",
        "nav_jobs": "💼 职位匹配",
        "nav_resources": "📝 技术资源",
        "nav_community": "💬 问答社区",
        "nav_profile": "👤 个人中心",
        "nav_notifications": "🔔 通知设置",
        "nav_title": "🧭 导航",
        "nav_select": "选择页面",
        
        # Sidebar
        "sidebar_guest": "👤 访客模式",
        "sidebar_guest_hint": "登录后可保存进度",
        "sidebar_logout": "🚪 退出登录",
        "sidebar_stats": "📊 快速统计",
        
        # Hero
        "hero_title": "🎯 Interview Prep Platform",
        "hero_subtitle": "基于 Gap Analysis 的个性化面试准备平台 - 支持SDE/MLE/PM/DS等多种角色",
        
        # Auth
        "auth_title": "🔐 用户登录",
        "auth_subtitle": "登录后可保存你的学习进度",
        "auth_login": "🔑 登录",
        "auth_register": "📝 注册",
        "auth_email": "📧 邮箱",
        "auth_password": "🔒 密码",
        "auth_confirm_password": "🔒 确认密码",
        "auth_login_btn": "登录",
        "auth_register_btn": "注册",
        "auth_guest": "👤 以访客身份继续",
        "auth_or": "或者",
        "auth_guest_mode": "👤 访客模式",
        "auth_guest_hint": "登录后可保存进度",
        "auth_logout": "🚪 退出登录",
        
        # Community
        "community_title": "💬 面试问答社区",
        "community_subtitle": "提问 → AI 先答 → 社区补充 → 共同成长",
        "community_browse": "📋 浏览问题",
        "community_ask": "✍️ 我要提问",
        "community_search": "🔍 搜索",
        "community_answers": "👥 社区回答",
        "community_submit": "📝 提交回答",
        
        # Profile
        "profile_title": "👤 个人中心",
        "profile_subtitle": "查看你的成就、积分和排名",
        "profile_my_profile": "📊 我的资料",
        "profile_leaderboard": "🏆 排行榜",
        "profile_achievements": "🎯 成就进度",
        "profile_points": "⭐ 积分",
        "profile_streak": "🔥 连续",
        "profile_answers": "📝 回答",
        "profile_questions": "❓ 提问",
        "profile_badges": "🏆 徽章收藏",
        
        # Resources
        "resources_latest": "🔥 最新论文",
        "resources_company": "🏢 公司论文",
        "resources_blogs": "📖 公司博客",
        "resources_must_read": "📚 经典必读",
        "resources_learning": "🎓 学习资源",
        
        # Jobs
        "jobs_match": "🤖 AI 职位分析",
        "jobs_daily": "📅 每日新职位",
        "jobs_resume_match": "📄 简历匹配",
        
        # Common
        "loading": "加载中...",
        "success": "成功！",
        "error": "出错了",
        "save": "保存",
        "cancel": "取消",
        "submit": "提交",
        "refresh": "刷新",
        "back": "返回",
        "next": "下一步",
        "previous": "上一步",
        "anonymous": "匿名用户",
        
        # Resume page
        "resume_title": "📄 输入你的简历",
        "resume_hint": "粘贴你的简历内容，我们将自动提取技能关键词",
        "resume_label": "简历内容",
        "resume_placeholder": "粘贴你的简历内容...\n\n例如:\nSenior Software Engineer with 5 years of experience...\n\nSkills: Python, Java, Kubernetes, AWS...",
        "resume_extract_btn": "提取技能 →",
        "resume_success": "成功提取 {} 个技能!",
        "resume_error": "请先输入简历内容",
        
        # Target page
        "target_title": "🎯 选择目标公司和职位",
        "target_company": "目标公司",
        "target_role": "目标角色",
        "target_level": "目标级别",
        "target_rounds": "📋 面试结构",
        "target_confirm_btn": "确认目标 →",
        
        # JD page
        "jd_title": "📋 输入职位描述 (JD)",
        "jd_label": "JD内容",
        "jd_placeholder": "粘贴职位描述...\n\n例如:\nWe are looking for a Software Engineer...",
        "jd_analyze_btn": "分析JD →",
        "jd_success": "从JD中提取 {} 个技能要求!",
        "jd_error": "请先输入JD内容",
        
        # Analysis page
        "analysis_title": "📊 Gap Analysis",
        "analysis_warning": "请先完成简历和JD的输入",
        "analysis_gaps": "🔴 需要补齐",
        "analysis_strengths": "🟢 已具备",
        "analysis_extra": "🔵 额外技能",
        "analysis_generate_btn": "生成学习计划 →",
        
        # Plan page
        "plan_title": "📚 个性化学习计划",
        "plan_no_gaps": "你没有明显的技能Gap，可以专注于面试模拟练习！",
        "plan_phases": "📅 学习阶段",
        "plan_phase1": "📖 阶段1: 技能补齐 (1-2周)",
        "plan_phase2": "💻 阶段2: Coding练习 (1-2周)",
        "plan_phase3": "🏗️ 阶段3: ML System Design (1周)",
        "plan_phase4": "🗣️ 阶段4: Behavioral准备 (3-5天)",
        "plan_learn": "学习: {}",
        "plan_search": "搜索资料",
        
        # Home page
        "home_features": "✨ 核心功能",
        "home_gap_title": "🔍 Gap Analysis",
        "home_gap_desc": "对比你的简历和目标JD，精准识别需要补齐的技能短板",
        "home_company_title": "🏢 公司定制",
        "home_company_desc": "针对Google/Meta/Amazon等公司的面试结构，定制化准备策略",
        "home_plan_title": "📚 智能计划",
        "home_plan_desc": "根据面试日期倒推，生成按轮次组织的学习计划",
        "home_quickstart": "🚀 快速开始",
        "home_start_btn": "开始准备面试 →",
        
        # Settings
        "settings": "⚙️ 设置",
        "language": "🌐 语言",
        
        # Footer
        "footer": "Made with ❤️ for Job Seekers",
    },
    
    "en": {
        # Navigation
        "nav_home": "🏠 Home",
        "nav_resume": "📄 Resume",
        "nav_target": "🎯 Target",
        "nav_jd": "📋 Job Description",
        "nav_analysis": "📊 Gap Analysis",
        "nav_plan": "📚 Study Plan",
        "nav_questions": "📖 Questions",
        "nav_mock": "🤖 Mock Interview",
        "nav_jobs": "💼 Job Match",
        "nav_resources": "📝 Resources",
        "nav_community": "💬 Community",
        "nav_profile": "👤 Profile",
        "nav_notifications": "🔔 Notifications",
        "nav_title": "🧭 Navigation",
        "nav_select": "Select Page",
        
        # Sidebar
        "sidebar_guest": "👤 Guest Mode",
        "sidebar_guest_hint": "Sign in to save progress",
        "sidebar_logout": "🚪 Log Out",
        "sidebar_stats": "📊 Quick Stats",
        
        # Hero
        "hero_title": "🎯 Interview Prep Platform",
        "hero_subtitle": "Personalized interview preparation based on Gap Analysis - Supports SDE/MLE/PM/DS roles",
        
        # Auth
        "auth_title": "🔐 Sign In",
        "auth_subtitle": "Sign in to save your progress",
        "auth_login": "🔑 Sign In",
        "auth_register": "📝 Sign Up",
        "auth_email": "📧 Email",
        "auth_password": "🔒 Password",
        "auth_confirm_password": "🔒 Confirm Password",
        "auth_login_btn": "Sign In",
        "auth_register_btn": "Sign Up",
        "auth_guest": "👤 Continue as Guest",
        "auth_or": "or",
        "auth_guest_mode": "👤 Guest Mode",
        "auth_guest_hint": "Sign in to save progress",
        "auth_logout": "🚪 Log Out",
        
        # Community
        "community_title": "💬 Interview Q&A Community",
        "community_subtitle": "Ask → AI Answers → Community Contributes → Grow Together",
        "community_browse": "📋 Browse",
        "community_ask": "✍️ Ask",
        "community_search": "🔍 Search",
        "community_answers": "👥 Community Answers",
        "community_submit": "📝 Submit Answer",
        
        # Profile
        "profile_title": "👤 Profile",
        "profile_subtitle": "View your achievements, points and rank",
        "profile_my_profile": "📊 My Profile",
        "profile_leaderboard": "🏆 Leaderboard",
        "profile_achievements": "🎯 Achievements",
        "profile_points": "⭐ Points",
        "profile_streak": "🔥 Streak",
        "profile_answers": "📝 Answers",
        "profile_questions": "❓ Questions",
        "profile_badges": "🏆 Badges",
        
        # Resources
        "resources_latest": "🔥 Latest Papers",
        "resources_company": "🏢 Company Papers",
        "resources_blogs": "📖 Company Blogs",
        "resources_must_read": "📚 Must Read",
        "resources_learning": "🎓 Learning",
        
        # Jobs
        "jobs_match": "🤖 AI Job Match",
        "jobs_daily": "📅 Daily Jobs",
        "jobs_resume_match": "📄 Resume Match",
        
        # Common
        "loading": "Loading...",
        "success": "Success!",
        "error": "Error",
        "save": "Save",
        "cancel": "Cancel",
        "submit": "Submit",
        "refresh": "Refresh",
        "back": "Back",
        "next": "Next",
        "previous": "Previous",
        "anonymous": "Anonymous",
        
        # Hero
        "hero_title": "🎯 Interview Prep Platform",
        "hero_subtitle": "Personalized interview preparation based on Gap Analysis - Supports SDE/MLE/PM/DS roles",
        
        # Auth
        "auth_title": "🔐 Sign In",
        "auth_subtitle": "Sign in to save your progress",
        "auth_login": "🔑 Sign In",
        "auth_register": "📝 Sign Up",
        "auth_email": "📧 Email",
        "auth_password": "🔒 Password",
        "auth_confirm_password": "🔒 Confirm Password",
        "auth_login_btn": "Sign In",
        "auth_register_btn": "Sign Up",
        "auth_guest": "👤 Continue as Guest",
        "auth_or": "or",
        "auth_guest_mode": "👤 Guest Mode",
        "auth_guest_hint": "Sign in to save progress",
        "auth_logout": "🚪 Log Out",
        
        # Resume page
        "resume_title": "📄 Enter Your Resume",
        "resume_hint": "Paste your resume content, we'll automatically extract skills",
        "resume_label": "Resume Content",
        "resume_placeholder": "Paste your resume content...\n\nExample:\nSenior Software Engineer with 5 years of experience...\n\nSkills: Python, Java, Kubernetes, AWS...",
        "resume_extract_btn": "Extract Skills →",
        "resume_success": "Successfully extracted {} skills!",
        "resume_error": "Please enter resume content first",
        
        # Target page
        "target_title": "🎯 Select Target Company & Role",
        "target_company": "Target Company",
        "target_role": "Target Role",
        "target_level": "Target Level",
        "target_rounds": "📋 Interview Structure",
        "target_confirm_btn": "Confirm Target →",
        "target_duration": "min",
        
        # JD page
        "jd_title": "📋 Enter Job Description",
        "jd_label": "JD Content",
        "jd_placeholder": "Paste job description...\n\nExample:\nWe are looking for a Software Engineer to join our team...\n\nRequirements:\n- 3+ years of experience\n- Experience with Python or Java...",
        "jd_analyze_btn": "Analyze JD →",
        "jd_success": "Extracted {} skill requirements from JD!",
        "jd_error": "Please enter JD content first",
        
        # Analysis page
        "analysis_title": "📊 Gap Analysis",
        "analysis_warning": "Please complete resume and JD input first",
        "analysis_gaps": "🔴 Skills to Learn",
        "analysis_strengths": "🟢 Already Have",
        "analysis_extra": "🔵 Extra Skills",
        "analysis_generate_btn": "Generate Study Plan →",
        
        # Plan page
        "plan_title": "📚 Personalized Study Plan",
        "plan_no_gaps": "No obvious skill gaps! Focus on interview practice!",
        "plan_phases": "📅 Study Phases",
        "plan_phase1": "📖 Phase 1: Skill Building (1-2 weeks)",
        "plan_phase2": "💻 Phase 2: Coding Practice (1-2 weeks)",
        "plan_phase3": "🏗️ Phase 3: System Design (1 week)",
        "plan_phase4": "🗣️ Phase 4: Behavioral Prep (3-5 days)",
        "plan_learn": "Learn: {}",
        "plan_search": "Search Resources",
        
        # Home page
        "home_features": "✨ Key Features",
        "home_gap_title": "🔍 Gap Analysis",
        "home_gap_desc": "Compare your resume with target JD to identify skill gaps",
        "home_company_title": "🏢 Company Tailored",
        "home_company_desc": "Customized prep strategies for Google/Meta/Amazon interview structures",
        "home_plan_title": "📚 Smart Planning",
        "home_plan_desc": "Generate study plans organized by interview rounds",
        "home_quickstart": "🚀 Quick Start",
        "home_start_btn": "Start Interview Prep →",
        
        # Stats
        "stats_skills": "📄 Resume Skills",
        "stats_company": "🎯 Target Company",
        "stats_gaps": "🔴 Skill Gaps",
        "stats_progress": "✅ Progress",
        "stats_not_selected": "Not Selected",
        
        # Features
        "features_title": "✨ Key Features",
        "feature_gap_title": "🔍 Gap Analysis",
        "feature_gap_desc": "Compare your resume with target JD to identify skill gaps",
        "feature_company_title": "🏢 Company Tailored",
        "feature_company_desc": "Customized prep strategies for Google/Meta/Amazon interview structures",
        "feature_plan_title": "📚 Smart Planning",
        "feature_plan_desc": "Generate study plans organized by interview rounds",
        
        # Quick start
        "quickstart_title": "🚀 Quick Start",
        "quickstart_btn": "Start Interview Prep →",
        
        # Footer
        "footer": "Made with ❤️ for Job Seekers",
        
        # Progress steps
        "step_resume": "📄 Resume",
        "step_target": "🎯 Target",
        "step_jd": "📋 JD",
        "step_analysis": "📊 Analysis",
        "step_plan": "📚 Plan",
        
        # Settings
        "settings": "⚙️ Settings",
        "language": "🌐 Language",
    },
    
    "ja": {
        "nav_home": "🏠 ホーム",
        "nav_resume": "📄 履歴書",
        "nav_target": "🎯 目標",
        "nav_jd": "📋 求人情報",
        "nav_analysis": "📊 ギャップ分析",
        "nav_plan": "📚 学習計画",
        "nav_title": "🧭 ナビゲーション",
        "hero_title": "🎯 Interview Prep Platform",
        "hero_subtitle": "ギャップ分析に基づくパーソナライズされた面接準備プラットフォーム",
        "auth_logout": "🚪 ログアウト",
        "settings": "⚙️ 設定",
        "language": "🌐 言語",
        # Add more translations as needed...
    },
    
    "ko": {
        "nav_home": "🏠 홈",
        "nav_resume": "📄 이력서",
        "nav_target": "🎯 목표",
        "nav_jd": "📋 채용공고",
        "nav_analysis": "📊 갭 분석",
        "nav_plan": "📚 학습 계획",
        "nav_title": "🧭 네비게이션",
        "hero_title": "🎯 Interview Prep Platform",
        "hero_subtitle": "갭 분석 기반 맞춤형 면접 준비 플랫폼",
        "auth_logout": "🚪 로그아웃",
        "settings": "⚙️ 설정",
        "language": "🌐 언어",
        # Add more translations as needed...
    }
}


def get_text(key: str, lang: str = "zh") -> str:
    """Get translated text for a given key."""
    if lang not in TRANSLATIONS:
        lang = "zh"
    
    translations = TRANSLATIONS[lang]
    
    # Fall back to Chinese if key not found in target language
    if key not in translations:
        return TRANSLATIONS["zh"].get(key, key)
    
    return translations[key]


def t(key: str, lang: str = "zh") -> str:
    """Shorthand for get_text"""
    return get_text(key, lang)
