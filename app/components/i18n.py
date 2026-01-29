"""
Internationalization (i18n) Module
Multi-language support for the Interview Prep Platform
"""

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
        "nav_title": "🧭 导航",
        
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
        
        # Resume page
        "resume_title": "📄 输入你的简历",
        "resume_hint": "粘贴你的简历内容，我们将自动提取技能关键词",
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
        "target_duration": "分钟",
        
        # JD page
        "jd_title": "📋 输入职位描述 (JD)",
        "jd_placeholder": "粘贴职位描述...\n\n例如:\nWe are looking for a Software Engineer to join our team...\n\nRequirements:\n- 3+ years of experience\n- Experience with Python or Java...",
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
        "plan_phase3": "🏗️ 阶段3: System Design (1周)",
        "plan_phase4": "🗣️ 阶段4: Behavioral准备 (3-5天)",
        "plan_learn": "学习: {}",
        "plan_search": "搜索资料",
        
        # Stats
        "stats_skills": "📄 简历技能",
        "stats_company": "🎯 目标公司",
        "stats_gaps": "🔴 技能Gap",
        "stats_progress": "✅ 学习进度",
        "stats_not_selected": "未选择",
        
        # Features
        "features_title": "✨ 核心功能",
        "feature_gap_title": "🔍 Gap Analysis",
        "feature_gap_desc": "对比你的简历和目标JD，精准识别需要补齐的技能短板",
        "feature_company_title": "🏢 公司定制",
        "feature_company_desc": "针对Google/Meta/Amazon等公司的面试结构，定制化准备策略",
        "feature_plan_title": "📚 智能计划",
        "feature_plan_desc": "根据面试日期倒推，生成按轮次组织的学习计划",
        
        # Quick start
        "quickstart_title": "🚀 快速开始",
        "quickstart_btn": "开始准备面试 →",
        
        # Footer
        "footer": "Made with ❤️ for Job Seekers",
        
        # Progress steps
        "step_resume": "📄 简历",
        "step_target": "🎯 目标",
        "step_jd": "📋 JD",
        "step_analysis": "📊 分析",
        "step_plan": "📚 计划",
        
        # Settings
        "settings": "⚙️ 设置",
        "language": "🌐 语言",
    },
    
    "en": {
        # Navigation
        "nav_home": "🏠 Home",
        "nav_resume": "📄 Resume",
        "nav_target": "🎯 Target",
        "nav_jd": "📋 Job Description",
        "nav_analysis": "📊 Gap Analysis",
        "nav_plan": "📚 Study Plan",
        "nav_title": "🧭 Navigation",
        
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
