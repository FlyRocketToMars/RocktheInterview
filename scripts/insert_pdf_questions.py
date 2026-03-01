import json, uuid
from pathlib import Path
from datetime import datetime

json_path = Path("data/interview_questions.json")
data = json.load(open(json_path, encoding="utf-8"))
existing = set(q["question"] for q in data["questions"])

# ============ From ML Preparation 2024.pdf ============
PREP_2024_QUESTIONS = [
    # ML Technical Assessment questions from the PDF
    {"q": "Explain overfitting and regularization (FAANG高频)", "cat": "fundamentals", "round": "ml_theory", "diff": "easy", "freq": 5,
     "answer": "**Overfitting** 是模型在训练集上表现极好但在测试集上表现差的现象，本质是模型学习了训练数据中的噪声而非规律。\n\n**Regularization** 是防止过拟合的核心手段，通过在 loss function 中添加惩罚项来约束模型复杂度：\n- **L1 (Lasso)**: 添加 λΣ|w|，倾向产生稀疏解（feature selection）\n- **L2 (Ridge)**: 添加 λΣw²，倾向让权重均匀变小\n- **Dropout**: 训练时随机丢弃神经元\n- **Early Stopping**: 监控验证集loss，在开始上升时停止\n- **Data Augmentation**: 增加训练数据多样性"},

    {"q": "Explain Gradient Descent and Stochastic Gradient Descent. Which one would you prefer?", "cat": "fundamentals", "round": "ml_theory", "diff": "medium", "freq": 5,
     "answer": "**Gradient Descent (GD)**: 每次用全部训练数据计算梯度，更新参数。优点是梯度方向稳定，缺点是计算慢、内存需求大。\n\n**Stochastic GD (SGD)**: 每次只用一个样本计算梯度。优点是速度快，能跳出局部最优；缺点是梯度噪声大。\n\n**Mini-batch SGD** 是实践中最常用的折中方案（batch_size=32~256）。\n\n实践中更推荐 **Adam Optimizer**，它结合了 Momentum 和 RMSProp 的优点。"},

    {"q": "[Difficult] Can you derive gradient descent for Logistic Regression?", "cat": "fundamentals", "round": "ml_theory", "diff": "hard", "freq": 4,
     "answer": "Logistic Regression 的推导过程：\n1. **假设**: P(y=1|x) = σ(wᵀx + b)，其中 σ(z) = 1/(1+e⁻ᶻ)\n2. **Loss**: Binary Cross Entropy = -[y·log(ŷ) + (1-y)·log(1-ŷ)]\n3. **梯度推导**: ∂L/∂w = (ŷ - y)·x，其中 ŷ = σ(wᵀx)\n4. **更新**: w ← w - α·∂L/∂w\n\n关键性质：σ(z)的导数 = σ(z)·(1-σ(z))，这使得推导非常简洁。"},

    {"q": "[Difficult] What do eigenvalues and eigenvectors mean in PCA?", "cat": "fundamentals", "round": "ml_theory", "diff": "hard", "freq": 3,
     "answer": "在 PCA 中：\n- **协方差矩阵的特征向量 (Eigenvectors)** 代表数据中方差最大的方向（即主成分 Principal Components）\n- **特征值 (Eigenvalues)** 代表对应主成分方向上的方差大小\n- 特征值越大，对应的主成分越重要，保留的信息越多\n\n**PCA 步骤**: 标准化 → 计算协方差矩阵 → 求特征值/向量 → 按特征值降序排列 → 选择前 k 个主成分\n\n**解释方差比**: 前 k 个特征值之和 / 所有特征值之和 = 保留了多少信息"},

    {"q": "[Difficult] Explain different Optimizers — How is Adam different from RMSProp?", "cat": "deep_learning", "round": "ml_theory", "diff": "hard", "freq": 5,
     "answer": "**核心区别**：\n- **Momentum**: delta = -lr * gradient + previous_delta * decay_rate，累积梯度方向的动量\n- **AdaGrad**: 追踪梯度平方和，自适应调整学习率。问题：学习率单调递减，后期过小\n- **RMSProp**: 修复 AdaGrad 的问题，用 exponential decay 代替简单累加\n- **Adam = Momentum + RMSProp**: 同时追踪梯度的一阶矩(均值)和二阶矩(方差)\n\nAdam 公式：\n- m = β1*m + (1-β1)*gradient [Momentum部分]\n- v = β2*v + (1-β2)*gradient² [RMSProp部分]\n- w -= lr * m / sqrt(v + ε)\n\n**面试Tips**: 要能手写 Adam 的更新公式，同时知道 β1=0.9, β2=0.999 是常用默认值"},

    {"q": "[Difficult] Different types of activation functions and the vanishing gradient problem", "cat": "deep_learning", "round": "ml_theory", "diff": "hard", "freq": 5,
     "answer": "**Sigmoid**: σ(x) = 1/(1+e⁻ˣ), 输出[0,1]。问题：梯度最大0.25，多层连乘导致**梯度消失**\n**Tanh**: tanh(x), 输出[-1,1]。比Sigmoid好但仍有梯度消失\n**ReLU**: max(0,x)。解决了梯度消失，但有 **dying ReLU** 问题（负数区梯度=0）\n**Leaky ReLU**: max(0.01x, x)。解决dying ReLU\n**GELU/SiLU**: 现代Transformer常用，平滑版ReLU\n\n**梯度消失原因**: 反向传播时梯度连乘，当每层梯度<1时，深层梯度趋近于0"},

    # System Design questions from PDF
    {"q": "Design a Feed Recommendation System (FAANG高频系统设计)", "cat": "recsys", "round": "ml_system_design", "diff": "hard", "freq": 5,
     "answer": "**Clarify**: 用户规模、实时性要求、优化目标(engagement/relevance)\n\n**架构**: Candidate Generation → Ranking → Re-ranking → Blending\n\n**召回层**: Two-Tower模型(user/item embedding), 协同过滤, 内容相似度, 图模型\n**排序层**: Wide&Deep/DCN, 多目标优化(like, share, comment, dwell_time)\n**重排序**: 多样性(MMR), 新鲜度提升, 广告插入\n\n**Feature**: User历史行为序列, Item属性, Context(时间/设备), Social Graph\n**实时性**: 近线计算(streaming), Feature Store, 增量更新\n**Metrics**: Offline(AUC/NDCG), Online(DAU, 时长, CTR)\n\n**面试Tips**: 一定要画架构图，讲清楚每层的延迟预算"},

    {"q": "Design YouTube/Video Recommendation System (Google高频)", "cat": "recsys", "round": "ml_system_design", "diff": "hard", "freq": 5,
     "answer": "**经典论文**: Deep Neural Networks for YouTube Recommendations (2016)\n\n**Two-Stage架构**:\n1. **Candidate Generation**: 从百万视频中召回几百个候选\n   - User历史观看 → Embedding → ANN检索\n   - 多路召回：协同过滤、内容相似、热门、订阅\n2. **Ranking**: 精排几百个候选\n   - 输入：视频特征 + 用户特征 + 上下文\n   - 模型：DNN预测expected watch time\n   - 技巧：用weighted logistic regression近似\n\n**关键设计决策**:\n- Age feature处理训练/服务不一致\n- 负采样策略\n- 位置偏差校正\n- Explore vs Exploit平衡"},

    {"q": "Design Google Contact Ranking (Google)", "cat": "ranking", "round": "ml_system_design", "diff": "hard", "freq": 3,
     "answer": "**问题**: 用户在通讯录搜索时，按相关性排序联系人\n\n**Feature Engineering**:\n- 通讯频率(邮件/电话/消息)\n- 最近联系时间\n- 社交图谱距离\n- 组织结构关系\n- 搜索query与联系人名字的匹配度\n\n**模型**: LambdaMART 或 简单的 LR (低延迟要求)\n**Metrics**: MRR (Mean Reciprocal Rank), NDCG\n**关键考虑**: 隐私保护、冷启动、跨设备同步"},

    {"q": "Design an Item Replacement Recommendation System (Instacart)", "cat": "recsys", "round": "ml_system_design", "diff": "hard", "freq": 3,
     "answer": "**场景**: 用户下单的商品缺货，推荐替代品\n\n**召回**: 同品类/品牌/价格区间的商品, 协同过滤(买了A的人也买了B)\n**排序**: 考虑品牌偏好、价格敏感度、历史替换接受率\n**Feature**: 商品属性相似度、价格差异、用户历史偏好、营养成分(食品)\n**特殊考虑**: 过敏原/禁忌、有机/非有机偏好、包装规格\n**Metrics**: 替换接受率、用户满意度、订单完成率"},

    {"q": "Design an ML System to Optimize Coupon Distribution with a Set Budget (Netflix)", "cat": "recsys", "round": "ml_system_design", "diff": "hard", "freq": 3,
     "answer": "**问题**: 固定预算下最大化优惠券的ROI\n\n**建模**: Uplift Modeling — 预测发券 vs 不发券的增量效果\n**方法**: Two-Model approach, Causal Forest, Meta-learner\n**优化**: 约束优化(Knapsack problem) — 在预算约束下最大化总uplift\n**Feature**: 用户活跃度、流失风险、消费历史、价格敏感度\n**评估**: 需要 A/B test 验证因果效果\n**关键**: 避免给本来就会续费的用户发券(deadweight loss)"},
]

# ============ From ML System Design.pdf ============
SYS_DESIGN_QUESTIONS = [
    {"q": "ML System Design Framework: 如何构建完整的ML系统设计面试答案？(7步法)", "cat": "mlops", "round": "ml_system_design", "diff": "medium", "freq": 5,
     "answer": "**7步法框架**:\n1. **Clarifying Requirements**: 业务目标、用户画像、规模量级\n2. **Defining Metrics**: Offline(AUC/logloss) + Online(A/B engagement) + Component vs End-to-end\n3. **Architecting for Scale**: Funnel approach — 每层处理更少的候选\n4. **Offline Model Building**: 数据生成 → Feature Engineering → 模型训练 → 离线评估\n5. **Online Execution**: 部署 → 实时serving → 在线evaluation\n6. **Iterative Improvement**: Debug offline/online性能差异\n7. **Performance & Capacity**: 训练/推理复杂度、SLA"},

    {"q": "Training Data Generation: Human labeled vs User interaction data的优劣对比", "cat": "mlops", "round": "ml_system_design", "diff": "medium", "freq": 4,
     "answer": "**Human Labeled Data**:\n- 优点：标注质量高、标签精确\n- 缺点：成本高、速度慢、标注者偏差\n- 适用：NLP任务、需要专家知识的场景\n\n**User Interaction Data (Implicit Feedback)**:\n- 优点：数据量极大、实时获取、无额外成本\n- 缺点：噪声大、存在position bias、缺乏负样本\n- 适用：推荐系统、搜索排序、广告点击预测\n\n**关键考虑**: Label是否能准确代表真实用户满意度？点击≠满意"},

    {"q": "Performance and Capacity Considerations: Training/Evaluation/Sample complexity对比", "cat": "mlops", "round": "ml_system_design", "diff": "hard", "freq": 4,
     "answer": "**三种复杂度**:\n1. **Training Complexity**: 训练模型所需时间\n2. **Evaluation Complexity**: 推理时处理单条数据的时间\n3. **Sample Complexity**: 学习目标函数所需的训练样本量\n\n**模型对比** (n=样本数, f=特征数):\n- **Linear Regression**: Train O(nf²), Eval O(f) — 最快\n- **MART/GBDT**: Train O(n·f·d·n_trees), Eval O(d·n_trees) — 中等\n- **DNN**: Train O(e·n·Σnl·nl+1), Eval O(Σnl·nl+1) — 最慢但最强\n\n**实践选择**: 搜索广告(低延迟)→LR/GBDT; 推荐(可容忍延迟)→DNN"},

    {"q": "Funnel Approach in Large Scale ML Systems: 为什么需要多级漏斗架构？", "cat": "recsys", "round": "ml_system_design", "diff": "medium", "freq": 5,
     "answer": "**问题**: 搜索引擎匹配到1亿文档，不可能每个都跑复杂模型\n\n**漏斗架构**:\n- **L1 粗筛 (Millions→Thousands)**: 倒排索引/ANN, <1ms/doc\n- **L2 精排 (Thousands→Hundreds)**: 轻量级LR/GBDT, <10μs/doc\n- **L3 重排 (Hundreds→Tens)**: 复杂DNN, <1ms/doc\n\n**SLA举例**: 100M文档，要求500ms内返回结果\n- 快速模型1μs/doc → 100M × 1μs = 100s (太慢!)\n- 解决：1000台机器分布式 → 100s/1000 = 100ms ✓\n- 或者先简单模型筛到1000个，再用复杂模型精排\n\n**面试Tips**: 必须能估算具体延迟数字(QPS, latency per doc)"},

    {"q": "Online Model Execution: A/B Testing和模型部署的最佳实践", "cat": "mlops", "round": "ml_system_design", "diff": "medium", "freq": 4,
     "answer": "**部署策略**:\n1. **Shadow Mode**: 新模型并行运行但不影响用户\n2. **Canary Release**: 先给小流量(1-5%)，监控关键指标\n3. **A/B Test**: 随机分流，统计显著性检验\n\n**A/B测试要点**:\n- 样本量：用统计功效分析计算最小样本量\n- 时长：至少1-2周，覆盖周末效应\n- 指标：primary(核心业务指标) + guardrail(安全指标)\n- 分流：用户级别分流，避免contamination\n\n**Offline/Online不一致调试**:\n- 训练/服务数据分布差异(Data Skew)\n- Feature不一致(Training-Serving Skew)\n- 时间穿越(Label Leakage)"},

    {"q": "Design a Search Ranking System (搜索排序系统设计)", "cat": "ranking", "round": "ml_system_design", "diff": "hard", "freq": 5,
     "answer": "**问题定义**: 给定query，从海量文档中返回最相关的结果\n\n**架构**:\n1. **Query理解**: 分词、纠错、意图识别、query改写\n2. **文档召回**: 倒排索引(BM25) + 语义检索(向量化ANN)\n3. **排序**: Learning to Rank (LambdaMART/DNN)\n4. **重排**: 多样性、新鲜度、个性化\n\n**Feature**: Query-Doc匹配(BM25/TF-IDF), Doc质量(PageRank), 用户行为(CTR), 语义相似度(BERT embedding)\n**Loss**: Pairwise(RankNet) 或 Listwise(ListMLE)\n**Metrics**: NDCG@k, MRR, MAP\n\n**面试Tips**: 一定要讲清楚每层的候选数量和延迟预算"},

    {"q": "Iterative Model Improvement: 模型上线后如何持续优化？", "cat": "mlops", "round": "ml_system_design", "diff": "medium", "freq": 4,
     "answer": "**Debug Pipeline**:\n1. **Data问题**: 标签噪声、数据泄露、分布偏移\n2. **Feature问题**: 线上线下特征不一致、缺失值处理\n3. **Model问题**: 过拟合、欠拟合、模型容量不足\n\n**持续优化方向**:\n- 增加训练数据量/质量\n- 特征工程：添加cross features、sequence features\n- 模型升级：LR→GBDT→DNN→Multi-task\n- 负采样策略优化：hard negative mining\n- 多目标优化：MMOE、PLE\n\n**监控**: 模型性能漂移检测(PSI/KS)、数据质量监控、业务指标告警"},
]

added = 0
for item in PREP_2024_QUESTIONS + SYS_DESIGN_QUESTIONS:
    if item["q"] not in existing:
        entry = {
            "id": f"doc_{str(uuid.uuid4())[:8]}",
            "company": "Community",
            "role": "MLE",
            "level": "L4/L5",
            "round": item["round"],
            "domain": item["cat"],
            "question": item["q"],
            "answer": item.get("answer", "ℹ️ 答案待补充"),
            "follow_ups": [],
            "difficulty": item["diff"],
            "frequency": item["freq"],
            "importance": item["freq"],
            "tags": ["curated", "from-docs", item["cat"]],
            "common_mistakes": [],
            "year": 2026
        }
        data["questions"].append(entry)
        existing.add(item["q"])
        added += 1

data["metadata"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
data["metadata"]["total_questions"] = len(data["questions"])

with open(json_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print(f"Added {added} questions from PDFs. Total: {len(data['questions'])}")
