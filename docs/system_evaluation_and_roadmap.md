# 🎯 RocktheInterview 系统评估与重构计划

> 由 20 年经验面试官/求职者视角出发的专业评估
> 评估日期: 2026-01-31

---

## 📊 当前系统评分

| 模块 | 完成度 | 质量 | 优先级 | 备注 |
|------|--------|------|--------|------|
| 📝 简历分析 | 70% | ⭐⭐⭐ | 高 | 需要更智能的 AI 解析 |
| 🎯 技能匹配 | 60% | ⭐⭐⭐ | 高 | JD 解析需要增强 |
| 📅 学习计划 | 80% | ⭐⭐⭐⭐ | 高 | 刚完成，需测试迭代 |
| 📚 题库系统 | 75% | ⭐⭐⭐⭐ | 高 | 内容不错，需要更多真题 |
| 🎤 AI 模拟面试 | 50% | ⭐⭐ | 极高 | **最核心功能，需大幅加强** |
| 📰 博客聚合 | 85% | ⭐⭐⭐⭐ | 中 | RSS 抓取已完成 |
| 💬 社区问答 | 40% | ⭐⭐ | 中 | 需要更多用户才有价值 |
| 👤 用户系统 | 70% | ⭐⭐⭐ | 高 | Supabase 已接入 |
| 🏆 游戏化 | 60% | ⭐⭐⭐ | 中 | 徽章系统需完善 |
| 📧 通知推送 | 30% | ⭐⭐ | 低 | 基础功能，暂时够用 |

**总体评分: 6.5/10** - 有潜力，但核心功能需加强

---

## 🚨 最大的差距 (Critical Gaps)

### 1. AI 模拟面试 - 当前只有骨架，没有灵魂

**现状问题:**
- 只是简单的问答，没有真实的面试体验
- 没有追问 (Follow-up) 逻辑
- 没有评分和反馈系统
- 没有语音交互

**理想状态 (参考 Pramp, Interviewing.io):**
```
用户回答 → AI 评估 → 追问深入 → 评分反馈 → 改进建议
```

**需要实现:**
- [ ] 多轮追问逻辑 (根据回答质量决定追问方向)
- [ ] 结构化评分 (Communication, Technical, Problem Solving)
- [ ] 语音转文字 + 文字转语音
- [ ] 面试回放与自我复盘
- [ ] 常见错误检测 ("你说了太多 um/ah")

### 2. 真实面试题库 - 数量和深度不够

**现状问题:**
- 只有 ~30 道题，太少
- 没有按公司/职级分类详细
- 缺少真实面试反馈

**理想状态:**
- 500+ 真实面试题 (来自 Blind, Glassdoor, 一亩三分地)
- 每道题有：标准答案 + 常见错误 + 评分标准
- 用户可以贡献和评价题目

### 3. 编程练习 - 完全缺失

**面试必考项目缺失:**
- LeetCode 算法题练习/追踪
- ML 算法实现 (从零实现 KMeans, Decision Tree)
- SQL 题目
- 系统设计白板

---

## 🔧 重构建议

### 阶段 1: 核心功能优化 (2 周)

#### 1.1 AI 模拟面试升级
```python
# 目标架构
class MockInterviewV2:
    def __init__(self):
        self.rounds = ["behavioral", "ml_theory", "coding", "system_design"]
        self.difficulty_adjuster = DifficultyAdjuster()
        self.evaluator = InterviewEvaluator()
    
    def conduct_round(self, round_type):
        question = self.get_question(round_type)
        answer = self.get_user_answer()  # 支持语音
        
        # 评估回答质量
        evaluation = self.evaluator.evaluate(question, answer)
        
        # 决定是否追问
        if evaluation.needs_followup:
            followup = self.generate_followup(question, answer, evaluation)
            return followup
        
        # 生成反馈
        return self.generate_feedback(evaluation)
```

#### 1.2 题库扩充
- 爬取 Glassdoor、Blind 的 MLE 面试题
- 添加用户贡献入口
- 题目难度动态调整

### 阶段 2: 编程练习集成 (2 周)

#### 2.1 集成 LeetCode 跟踪
```python
class LeetCodeTracker:
    def __init__(self):
        self.tagged_questions = {
            "Google": ["#1", "#2", "#3"],
            "Meta": ["#4", "#5", "#6"],
        }
    
    def get_daily_problem(self, user_level, target_company):
        # 根据用户水平和目标公司推荐题目
        pass
```

#### 2.2 在线代码执行
- 集成 Judge0 或 Piston API
- 支持 Python, SQL 代码运行
- 自动测试用例

### 阶段 3: 个性化与智能化 (2 周)

#### 3.1 智能简历分析
```python
class SmartResumeAnalyzer:
    def analyze(self, resume_text, target_jd):
        # 使用 LLM 提取关键信息
        skills = self.extract_skills(resume_text)
        experience = self.extract_experience(resume_text)
        
        # 与 JD 匹配
        match_score = self.calculate_match(skills, experience, target_jd)
        
        # 生成改进建议
        suggestions = self.generate_suggestions(resume_text, target_jd)
        
        return {
            "match_score": match_score,
            "strengths": [...],
            "weaknesses": [...],
            "suggestions": suggestions
        }
```

#### 3.2 自适应学习路径
- 根据模拟面试表现动态调整学习计划
- 弱项自动加强
- 强项快速跳过

### 阶段 4: 社区与激励 (1 周)

#### 4.1 面试经验分享
- 面试时间线 (Interview Timeline)
- 匿名薪资分享
- 公司评价

#### 4.2 游戏化完善
- 每日挑战
- 排行榜 (周/月)
- 成就系统

---

## 📁 建议的文件结构重构

```
RocktheInterview/
├── app/
│   ├── main.py                    # 主入口
│   ├── components/
│   │   ├── mock_interview_v2.py   # ⭐ 重写
│   │   ├── resume_analyzer.py     # ⭐ 智能分析
│   │   ├── coding_practice.py     # ⭐ 新增
│   │   ├── learning_plan.py       # ✅ 已完成
│   │   └── ...
│   └── services/
│       ├── ai_evaluator.py        # ⭐ 面试评估服务
│       ├── speech_service.py      # ⭐ 语音服务
│       └── code_executor.py       # ⭐ 代码执行
├── data/
│   ├── questions/
│   │   ├── ml_theory.json         # 分类题库
│   │   ├── system_design.json
│   │   ├── behavioral.json
│   │   └── coding.json
│   ├── companies/
│   │   ├── google.json            # 公司特定准备
│   │   ├── meta.json
│   │   └── ...
│   └── ...
└── docs/
    ├── ml_system_design_framework.md  # ✅ 已完成
    └── ...
```

---

## 🎯 优先级排序 (What to Build Next)

| 优先级 | 功能 | 影响 | 工作量 | ROI |
|--------|------|------|--------|-----|
| 🔴 P0 | AI 模拟面试 V2 | 极高 | 大 | ⭐⭐⭐⭐⭐ |
| 🔴 P0 | 题库扩充到 200+ | 高 | 中 | ⭐⭐⭐⭐⭐ |
| 🟡 P1 | 编程练习集成 | 高 | 大 | ⭐⭐⭐⭐ |
| 🟡 P1 | 智能简历分析 | 中 | 中 | ⭐⭐⭐⭐ |
| 🟢 P2 | 语音面试 | 中 | 大 | ⭐⭐⭐ |
| 🟢 P2 | 面试经验社区 | 低 | 中 | ⭐⭐ |

---

## 💡 竞品对比

| 功能 | RocktheInterview | Pramp | Interviewing.io | Exponent |
|------|------------------|-------|-----------------|----------|
| AI 模拟面试 | 🟡 基础 | ❌ | ❌ | ✅ |
| 真人模拟 | ❌ | ✅ | ✅ | ❌ |
| 题库 | 🟡 30题 | ❌ | ❌ | ✅ 500+ |
| 学习计划 | ✅ | ❌ | ❌ | ✅ |
| 中文支持 | ✅ | ❌ | ❌ | ❌ |
| 免费 | ✅ | 🟡 | 🟡 | ❌ |

**我们的差异化优势:**
1. 🇨🇳 中文支持 (唯一)
2. 🤖 AI 模拟面试 (持续改进)
3. 📅 结构化学习计划
4. 💰 完全免费

---

## ✅ 下一步行动 (This Week)

1. **[ ] AI 模拟面试 V2 设计文档**
   - 定义评分标准
   - 设计追问逻辑
   - 选择语音服务

2. **[ ] 题库扩充**
   - 从 Glassdoor 抓取 100 道真题
   - 添加答案和评分标准

3. **[ ] 用户反馈收集**
   - 添加反馈按钮
   - 收集使用痛点

---

## 🏆 成功指标

| 指标 | 当前 | 目标 (3个月) |
|------|------|-------------|
| 日活用户 | ~5 | 100+ |
| 完成模拟面试次数 | ~10 | 500+ |
| 题库数量 | 30 | 300+ |
| 用户留存率 (7日) | ? | 40%+ |
| NPS 评分 | ? | 50+ |

---

*评估人: 资深面试官/求职者视角*  
*日期: 2026-01-31*
