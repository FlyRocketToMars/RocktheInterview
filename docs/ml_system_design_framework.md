# ML System Design Interview Framework
## Based on 20+ Years of Industry Experience

---

## 🎯 核心理念

> "A well-designed ML system is 90% understanding the problem, 10% choosing the model."

面试官不是在考你能不能背出 Transformer 架构，而是在考你能不能**像一个 Staff+ 工程师一样思考问题**。

---

## 📋 Phase 1: Clarifying Questions (5-10 min)

在画任何架构图之前，**必须**先问清楚这些问题。这不仅展示你的 maturity，也避免你走偏方向。

### 1.1 Business Understanding

| 问题 | 为什么重要 |
|------|-----------|
| What is the primary business goal? | CTR vs Revenue vs Engagement 会导致完全不同的设计 |
| Who are the users? | B2B vs B2C，新用户 vs 老用户 |
| What's the success metric? | Offline metric (AUC) vs Online metric (A/B test) |
| What are the constraints? (Legal, ethical) | GDPR, fairness, explainability |

### 1.2 Scale & Requirements

| 问题 | 为什么重要 |
|------|-----------|
| How many users/requests per day? | 1M vs 1B 是完全不同的架构 |
| What's the latency requirement? | <10ms vs <100ms vs <1s |
| How fresh does the model need to be? | Real-time vs hourly vs daily |
| What's the budget? (Compute, team size) | GPU cluster vs Cloud APIs |

### 1.3 Data Understanding

| 问题 | 为什么重要 |
|------|-----------|
| What data is available? | 决定 feature engineering 方向 |
| How is it labeled? (Human, implicit) | Label quality 直接影响模型上限 |
| Is there class imbalance? | 0.1% positive 需要特殊处理 |
| Any privacy concerns? | PII, cross-device tracking |

---

## 🏗️ Phase 2: High-Level Design (10-15 min)

### 2.1 Standard ML System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        DATA LAYER                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Raw Data │→│ ETL/DQ   │→│ Feature  │→│ Training │   │
│  │ Sources  │  │ Pipeline │  │ Store    │  │ Data     │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                       MODEL LAYER                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Training │→│ Eval &   │→│ Model    │→│ A/B Test │   │
│  │ Pipeline │  │ Validation│  │ Registry │  │ Framework│   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      SERVING LAYER                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Feature  │→│ Model    │→│ Business │→│ Logging  │   │
│  │ Retrieval│  │ Inference│  │ Logic    │  │ & Monitor│   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Two-Stage Architecture (推荐系统/搜索)

几乎所有大规模推荐/搜索系统都是这个架构：

```
Candidates (Millions) → Retrieval (Hundreds) → Ranking (Tens) → User
```

**Retrieval (召回)**:
- 目标: High Recall, 快速筛选
- 方法: ANN (FAISS, ScaNN), Two-Tower, Content-based
- 延迟: <10ms

**Ranking (排序)**:
- 目标: High Precision, 精准排序
- 方法: Deep Learning, Multi-task, Cross-features
- 延迟: <50ms

---

## 🔧 Phase 3: Deep Dive (15-20 min)

根据面试官的追问深入某个模块。常见方向：

### 3.1 Feature Engineering
- User features: Demographics, history, preferences
- Item features: Content, metadata, embeddings
- Context features: Time, device, location
- Cross features: User-Item interaction history

### 3.2 Model Architecture
- 推荐: Two-Tower, Wide & Deep, DCN, DIN
- NLP: BERT, T5, LLM-based
- CV: ResNet, ViT, Multimodal

### 3.3 Training Pipeline
- Offline: Batch training on historical data
- Online: Incremental updates, real-time learning
- Negative sampling: In-batch, hard negatives

### 3.4 Serving & Latency
- Model optimization: Quantization, distillation
- Caching: Embedding cache, result cache
- Load balancing: A/B traffic split

### 3.5 Monitoring & Iteration
- **Data Quality**: Schema drift, feature distribution
- **Model Performance**: Prediction drift, accuracy decay
- **Business Metrics**: CTR, revenue, user satisfaction
- **Alerting**: Statistical tests (KS, PSI), anomaly detection

---

## 📊 Phase 4: Trade-offs & Extensions (5 min)

展示你思考全面，不只是技术，还有业务：

### 常见 Trade-offs
| Trade-off | 选择 A | 选择 B |
|-----------|--------|--------|
| Accuracy vs Latency | Complex model | Simple model + caching |
| Freshness vs Stability | Real-time update | Periodic batch |
| Explore vs Exploit | More diversity | More relevance |
| Personalization vs Privacy | Rich user data | Federated/On-device |

### Extensions (如果有时间)
- Cold start 问题怎么解决?
- 如何处理 position bias?
- 如何做 A/B test?
- Long-term vs short-term optimization?

---

## 📚 学习路径 (8 周计划)

### Week 1-2: 基础框架
- [ ] 读 Chip Huyen《Designing Machine Learning Systems》Chapter 1-4
- [ ] 理解 ML lifecycle: Data → Model → Deploy → Monitor
- [ ] 练习 3 道 System Design (YouTube/Netflix/TikTok 推荐)

### Week 3-4: 推荐与搜索
- [ ] 深入 Two-Tower, Wide & Deep
- [ ] 理解 Feature Store (Feast, Tecton)
- [ ] 练习: Amazon Search, Uber Eats, Spotify

### Week 5-6: 生成式 AI 系统
- [ ] RAG 架构设计
- [ ] LLM Serving (vLLM, TensorRT-LLM)
- [ ] Prompt Engineering & Guardrails
- [ ] 练习: Enterprise Q&A Bot, AI Assistant

### Week 7-8: MLOps & Production
- [ ] CI/CD for ML
- [ ] Model Monitoring (Evidently, WhyLabs)
- [ ] A/B Testing frameworks
- [ ] 练习: ML Platform Design, Feature Store

---

## 🎤 面试 Tips

1. **画图**: 一定要画架构图，不要只讲
2. **数字**: 用具体数字说话 (QPS, latency, data size)
3. **Trade-off**: 主动提出并解释选择
4. **Check-in**: 每 5-10 分钟问面试官 "Is this the direction you want me to go?"
5. **不要过早优化**: 先讲 MVP，再讲 optimization

---

*Last updated: 2026-01-30*
