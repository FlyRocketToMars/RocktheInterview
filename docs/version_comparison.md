# 🎯 新旧版本对比指南

## 快速开始

### 运行新版本（推荐）
```bash
python -m streamlit run app/main_v2.py --server.port 8502
```
访问: http://localhost:8502

### 运行旧版本（备份）
```bash
python -m streamlit run app/main.py --server.port 8501
```
访问: http://localhost:8501

---

## 核心差异

| 特性 | 旧版本 (main.py) | 新版本 (main_v2.py) |
|------|------------------|---------------------|
| **页面数量** | 12+ Tabs | 3 核心页面 |
| **首页** | 通用欢迎页 | AI Daily Briefing |
| **每日任务** | 分散在多个Tab | 集中在Today页 |
| **AI角色** | 无 | AI Coach主动推荐 |
| **进度追踪** | 分散 | 统一Progress页 |
| **认知负担** | 高 | 低 |
| **上手时间** | 5-10分钟 | 30秒 |

---

## 新版本核心功能

### 1. 🏠 Today 页面（主战场）

**你会看到:**
- 🤖 **AI Daily Briefing**: 每天早上AI生成的个性化简报
  - 距离面试还有多少天
  - 今天应该focus什么
  - AI分析你的强弱项
  - 最新技术动态（Alex Xu新文章等）
  - 连续打卡天数

- 🎯 **Today's Missions**: 今天必做的3件事
  - 任务1: 针对你最弱的领域（如System Design）
  - 任务2: 目标公司相关（如Google特色题）
  - 任务3: 最新trending话题
  - 每个任务都有checkbox，完成后打勾

- 📊 **Quick Progress**: 一眼看出进度
  - Coding: 67% ████████░░
  - System Design: 45% ████░░░░░░
  - ML Theory: 82% ████████░░
  - Streak: 7🔥

- ⚡ **Quick Actions**: 快捷操作
  - 🎤 Mock Interview
  - 📝 Add Question
  - 🔥 Trending Topics
  - 📊 Full Progress

### 2. 📊 Progress 页面（深度分析）

**即将上线:**
- 🗺️ Knowledge Map: 知识图谱可视化
- 🔥 Weak Points Heatmap: 弱点热力图
- 📈 Timeline: 倒计时进度曲线

### 3. ⚙️ Settings 页面（一次性设置）

**设置内容:**
- Target Company (Google, Meta, OpenAI...)
- Target Role (MLE, SWE, Research Scientist...)
- Interview Date
- Daily Study Hours
- Focus Areas (Weak Points)

---

## AI Coach 如何工作

### 每天早上
```python
# AI 分析你的进度
progress = {
    "coding": 67%,
    "system_design": 45%,  # 最弱！
    "ml_theory": 82%
}

# AI 决定今天的重点
focus = "System Design + Coding"

# AI 生成3个任务
missions = [
    "🏗️ System Design: Netflix Recommendation",  # 针对弱点
    "💻 Coding: LeetCode 146",                   # 巩固
    "🔥 Trending: Alex Xu新文章"                 # 前沿
]
```

### 智能推荐逻辑
1. **找弱点**: 分析哪个领域完成度最低
2. **看目标**: 根据目标公司（如Google）推荐相关题
3. **抓热点**: 从Alex Xu等博客抓取最新内容

---

## 使用建议

### 面试准备的"面神"工作流

**每天早上（5分钟）:**
1. 打开 Today 页面
2. 阅读 AI Briefing
3. 看清楚今天的3个任务
4. 开始执行

**执行任务（2-3小时）:**
1. 专注完成任务1
2. 打勾 ✅
3. 完成任务2
4. 打勾 ✅
5. 完成任务3
6. 打勾 ✅

**每周回顾（10分钟）:**
1. 进入 Progress 页面
2. 查看知识图谱
3. 调整 Settings 中的 Focus Areas

---

## 为什么重构？

### 问题：信息过载
旧版本有太多Tab，用户不知道该看哪个：
- 🏠 Home
- 📄 Resume
- 🎯 Target
- 📋 JD
- 📊 Gap Analysis
- 📚 Study Plan
- 📈 Trends
- 🎤 Mock Interview
- 💼 Job Match
- 📖 Resources
- 📄 Papers
- 👥 Community
- 👤 Profile
- 🔔 Notifications

**结果**: 用户花5分钟找功能，而不是学习。

### 解决方案：极简主义
新版本只有3个页面：
- 🏠 Today: 今天做什么
- 📊 Progress: 我进展如何
- ⚙️ Settings: 一次性设置

**结果**: 用户30秒上手，立即开始学习。

---

## 技术架构

### 新增组件

```
app/
├── main_v2.py                  # 新版主入口
├── components/
│   └── ai_coach.py             # AI教练引擎
└── ...

docs/
└── redesign_v2.md              # 重构文档
```

### AI Coach 核心方法

```python
class AICoach:
    def generate_daily_briefing(user_id, profile):
        """生成每日AI简报"""
        
    def generate_daily_missions(user_id, profile):
        """生成今日3个任务"""
        
    def _analyze_progress(user_id):
        """分析用户进度"""
        
    def _determine_focus_area(progress):
        """决定今天focus什么"""
```

---

## 迁移路径

### 现在（Phase 1）
- ✅ 新版本骨架完成
- ✅ AI Coach 引擎完成
- ✅ Today 页面核心功能
- ⏳ Progress 页面（开发中）

### 下一步（Phase 2）
- [ ] 连接真实用户数据
- [ ] Progress 页面可视化
- [ ] 任务完成状态持久化
- [ ] 知识图谱

### 未来（Phase 3）
- [ ] AI对话功能
- [ ] 自动mock interview
- [ ] 社区分享

---

## 常见问题

### Q: 旧版本会被删除吗？
A: 不会。旧版本保留在 `main.py`，你可以随时切换回去。

### Q: 数据会丢失吗？
A: 不会。新旧版本共享同一套数据文件。

### Q: 如何切换回旧版本？
A: 停止新版本，运行 `python -m streamlit run app/main.py --server.port 8501`

### Q: AI Coach 需要联网吗？
A: 目前不需要。AI Coach 是基于规则的智能推荐，未来可能集成真正的LLM。

---

## 反馈与改进

如果你有任何建议，请：
1. 在 GitHub 提 Issue
2. 或直接修改代码并提 PR

**记住**: Less is More. Focus is Power. 🎯

---

**现在就试试新版本吧！**
```bash
python -m streamlit run app/main_v2.py --server.port 8502
```
