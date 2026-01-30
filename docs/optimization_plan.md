# 🎯 MLE 面试题库优化执行计划

**执行时间**: 2026-01-29 22:10 - 次日
**目标**: 打造业界最专业的 MLE 面试准备平台

---

## 📊 竞品分析 & 我们的差异化优势

### 主流面试平台分析

| 平台 | 优势 | 不足 |
|------|------|------|
| **LeetCode** | 算法题海量、OJ 系统 | 缺乏 ML 专项系统设计、无个性化推荐 |
| **InterviewQuery** | MLE 专项、真题多 | 付费门槛高、缺乏中文支持 |
| **Exponent** | ML System Design 课程好 | 视频为主、不够交互 |
| **Blind** | 真实面经、匿名 | 信息碎片化、不成体系 |
| **一亩三分地** | 华人面经详细 | 搜索困难、广告多 |
| **Educative** | Grokking 系列经典 | 纯阅读、无实践 |

### 我们的差异化定位

1. **全流程覆盖** - 从 Gap Analysis 到学习计划到题库一站式
2. **个性化推荐** - 基于用户技能 Gap 智能推荐题目
3. **MLE 专精** - 深入 ML 领域的系统设计和理论
4. **中英双语** - 服务全球华人 MLE 求职者
5. **每日推送** - 保持学习节奏

---

## 🔧 优化执行计划

### Phase 1: 题库分类重构 (进行中)

#### 1.1 新分类体系

**按面试轮次 (Interview Rounds)**
- `phone_screen` - 电话筛选
- `coding` - 编程轮
- `ml_coding` - ML 编程实现
- `ml_theory` - ML 理论深度
- `ml_system_design` - ML 系统设计
- `general_system_design` - 通用系统设计
- `behavioral` - 行为面试
- `case_study` - 案例分析

**按 ML 知识领域 (ML Domains)**
- `fundamentals` - 机器学习基础 (Bias-Variance, Regularization, Cross-validation)
- `deep_learning` - 深度学习 (CNN, RNN, Transformer, Attention)
- `nlp` - 自然语言处理 (BERT, GPT, Embeddings)
- `cv` - 计算机视觉 (Object Detection, Segmentation)
- `recsys` - 推荐系统 (Collaborative Filtering, Two-Tower)
- `ranking` - 搜索排序 (Learning to Rank, CTR Prediction)
- `llm` - 大语言模型 (Fine-tuning, RAG, Prompt Engineering)
- `mlops` - ML 工程化 (Pipeline, Serving, Monitoring)
- `experimentation` - 实验平台 (A/B Testing, Causal Inference)

**按难度和级别**
- `L3/E3` - 入门级 (0-2 年经验)
- `L4/E4` - 初级 (2-4 年经验)
- `L5/E5` - 中级 (4-7 年经验)
- `L6/E6` - 高级 (7-10 年经验)
- `L7/E7/Staff` - 专家级 (10+ 年经验)

#### 1.2 题目质量维度

每道题目增加:
- `frequency` - 高频程度 (1-5)
- `importance` - 重要程度 (1-5)
- `year` - 出题年份 (追踪趋势)
- `follow_ups` - 追问列表
- `related_topics` - 关联知识点
- `solution_approach` - 解题思路
- `common_mistakes` - 常见错误
- `interview_tips` - 面试技巧

### Phase 2: 题库内容扩充

#### 2.1 必刷核心题目 (100 道)

**ML 基础理论 (20 道)**
- Bias-Variance Tradeoff
- Overfitting/Underfitting 识别与解决
- 正则化方法 (L1, L2, Dropout, Early Stopping)
- 优化器选择 (SGD, Adam, AdaGrad)
- Loss Function 设计
- Evaluation Metrics (Precision, Recall, F1, AUC)
- Feature Engineering 方法论
- Imbalanced Data 处理

**深度学习 (20 道)**
- Transformer 架构详解
- Attention Mechanism 原理
- BatchNorm vs LayerNorm
- CNN 架构演进
- RNN/LSTM/GRU 对比
- Residual Connection 作用
- Position Encoding 设计
- Multi-head Attention 优势

**ML 系统设计 (30 道)**
- 推荐系统 (YouTube, Netflix, TikTok)
- 搜索排序 (Google Search, E-commerce)
- 广告系统 (Click Prediction, Bid Optimization)
- 欺诈检测 (Real-time, Feature Store)
- 内容审核 (Harmful Content Detection)
- Feed 排序 (Facebook, Instagram)
- 语义搜索 (Vector DB, Embedding)
- 图片搜索 (Visual Search)
- 对话系统 (Chatbot, LLM Serving)
- 实时特征服务 (Feature Platform)

**LLM 专项 (15 道)** - 2024 热点
- RAG 架构设计
- Fine-tuning vs Prompting
- LLM Serving & Scaling
- Vector Database 选型
- Chunking 策略
- Hallucination 处理
- Multi-modal LLM

**Coding 实现 (15 道)**
- KNN from scratch
- Logistic Regression from scratch
- Decision Tree from scratch
- K-Means from scratch
- Gradient Descent 实现
- Attention 实现
- Word2Vec 实现

### Phase 3: 前端优化

#### 3.1 新增功能页面
- **题目详情页** - 完整的题解、代码、讨论
- **模拟面试** - 计时答题模式
- **学习路径** - 按 Level/公司的推荐路径
- **进度追踪** - 已做/收藏/错题本

#### 3.2 UI 增强
- 题目卡片视觉优化
- 代码高亮显示
- 答案折叠/展开优化
- 移动端适配

### Phase 4: 智能化功能

#### 4.1 个性化推荐
- 基于 Gap Analysis 推荐薄弱题目
- 基于目标公司推荐高频题目
- 基于错题推荐巩固题目

#### 4.2 AI 辅助
- AI 生成题目解析
- AI 模拟面试官
- AI 代码评审

---

## ✅ 执行进度

### 今晚完成 (Phase 1-2) ✅
- [x] 分析竞品
- [x] 重构题库数据结构 (新增 round, domain, level, frequency, importance 等字段)
- [x] 扩充核心题目到 30 道 (覆盖 9 大知识领域)
- [x] 按新分类体系组织
- [x] 更新前端展示 (新增筛选器、高频标识、学习路径)

### 后续迭代 (Phase 3-4)
- [ ] 题目详情页
- [ ] 模拟面试功能
- [ ] 个性化推荐
- [ ] AI 辅助功能

---

## 📝 备注

本计划基于以下资源:
- Chip Huyen's "Introduction to ML Interviews" (200+ 题目)
- InterviewQuery 题型分析
- Exponent ML System Design 方法论
- 一亩三分地/Blind 真实面经
- 个人 MLE 面试经验 (Google, Meta, Amazon, 字节等)
