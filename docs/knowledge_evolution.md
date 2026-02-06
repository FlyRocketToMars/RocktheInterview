# 知识进化系统 (Knowledge Evolution System)

## 📚 概述

这是一个**自我进化的面试题库系统**，能够自动从最新的技术博客和论文中提取知识点，并生成相应的面试题目。

## 🎯 核心功能

### 1. 博客源集成

系统已集成以下高质量技术博客：

- **Alex Xu (ByteByteGo)** - 系统设计权威
- **Martin Fowler** - 软件架构大师
- **Netflix Tech Blog** - ML系统实践
- **Uber Engineering** - 大规模工程
- **Meta AI Blog** - AI研究前沿
- **OpenAI Blog** - LLM最新进展
- **Google AI Blog** - ML研究

### 2. 自动题目生成

系统会根据博客内容自动生成：

- **🏗️ 系统设计题** - 基于Alex Xu等博客的实际案例
- **🧠 理论题** - ML/LLM核心概念解析
- **💻 工程题** - 实际工程问题

### 3. 动态题库

所有自动生成的题目存储在 `data/dynamic_question_bank.json`，并自动集成到每日学习计划中。

## 🚀 使用方法

### 手动同步博客

```bash
# 运行同步脚本
python scripts/sync_blogs.py
```

这会：
1. 从所有配置的博客源抓取最新文章
2. 分析内容并生成面试题
3. 更新动态题库
4. 显示最新生成的题目

### 自动同步（推荐）

设置定时任务（如每天凌晨）自动同步：

**Windows (Task Scheduler):**
```powershell
# 创建每日任务
schtasks /create /tn "SyncBlogs" /tr "python d:\Interview\scripts\sync_blogs.py" /sc daily /st 02:00
```

**Linux/Mac (Cron):**
```bash
# 添加到 crontab
0 2 * * * cd /path/to/Interview && python scripts/sync_blogs.py
```

### 在每日计划中使用

系统会自动将最新的动态题目注入到每日学习计划中，显示为：

```
🔥 技术前沿: System Design (Alex Xu)
   └── 题目: 系统设计: How to Scale An API
   └── 来源: Alex Xu - System Design
   └── 描述: 基于 Alex Xu 的博客文章...
```

## 📂 文件结构

```
data/
├── blog_fetcher.py              # 博客抓取器
├── knowledge_evolver.py         # 知识进化引擎
├── dynamic_question_bank.json   # 动态题库
└── blog_cache.json             # 博客缓存（24小时）

scripts/
└── sync_blogs.py               # 手动同步脚本
```

## 🔧 配置

### 添加新的博客源

编辑 `data/blog_fetcher.py`，在 `sources` 字典中添加：

```python
"new_source": {
    "name": "Source Name",
    "url": "https://example.com/",
    "rss": "https://example.com/feed",
    "type": "system_design",  # or ml_research, llm, etc
    "priority": "high"
}
```

### 自定义题目生成规则

编辑 `data/knowledge_evolver.py` 中的生成函数：

- `_generate_alex_xu_question()` - Alex Xu 系统设计题
- `_generate_llm_question()` - LLM 理论题
- `_generate_ml_question()` - ML 工程题

## 📊 示例输出

运行 `python scripts/sync_blogs.py` 后：

```
🔄 Starting blog sync...
============================================================
Fetching from alex_xu...
Fetching from martin_fowler...
Fetching from netflix_tech...
...

✅ Sync complete! Generated 15 new questions.

📚 Latest questions in bank:
------------------------------------------------------------

1. [system_design] 系统设计: How to Scale An API
   Source: Alex Xu - System Design
   Added: 2026-02-05T22:24:56

2. [system_design] 系统设计: How Google Manages Trillions of Authorizations
   Source: Alex Xu - System Design
   Added: 2026-02-05T22:24:56
...
```

## 🎓 最佳实践

1. **每日同步**: 设置自动任务每天同步一次
2. **手动触发**: 在准备面试前手动运行一次，确保题库最新
3. **定期清理**: 每月检查 `dynamic_question_bank.json`，移除过时题目
4. **自定义规则**: 根据目标公司调整题目生成规则

## 🐛 故障排查

### RSS 抓取失败

如果某个源抓取失败，系统会使用缓存或跳过该源，不影响其他源。

### 题目重复

系统会自动检测并跳过已处理的博客文章（基于 URL）。

### 缓存问题

删除 `data/blog_cache.json` 强制重新抓取。

## 📈 未来改进

- [ ] 使用 LLM API 生成更高质量的题目描述
- [ ] 支持从 arXiv 抓取最新论文
- [ ] 添加难度评估算法
- [ ] 支持多语言题目生成
- [ ] 集成到 Streamlit UI 中手动触发同步

---

**现在你的面试准备系统真正"活"了起来！** 🚀
