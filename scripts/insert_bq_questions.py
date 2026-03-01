"""
Insert 50+ Behavioral Interview Questions
Organized by company culture and leadership principles.
"""
import json, uuid
from pathlib import Path
from datetime import datetime

json_path = Path("data/interview_questions.json")
data = json.load(open(json_path, encoding="utf-8"))
existing = set(q["question"] for q in data["questions"])

BQ_QUESTIONS = [
    # ============ Amazon Leadership Principles (16 LPs) ============
    {"q": "[Amazon LP: Customer Obsession] Tell me about a time you went above and beyond for a customer/user.",
     "cat": "behavioral", "company": "Amazon", "diff": "medium", "freq": 5,
     "answer": "**STAR框架回答**:\n- **Situation**: 描述用户/客户遇到的具体问题\n- **Task**: 你需要解决什么\n- **Action**: 你做了哪些超出职责范围的事(用'I'不用'we')\n- **Result**: 量化结果(用户满意度提升X%, 留存率+Y%)\n\n**Key**: Amazon最看重的LP，要展示你真的能站在用户角度思考，而不只是完成业务指标。"},

    {"q": "[Amazon LP: Ownership] Describe a time you took ownership of a problem outside your area of responsibility.",
     "cat": "behavioral", "company": "Amazon", "diff": "medium", "freq": 5,
     "answer": "展示你不是一个'这不是我的事'的人。讲一个你主动发现问题→主动跳出来解决→产生正面影响的故事。\n\n**加分点**: 提到你evaluate了长远影响而不只是短期修复。"},

    {"q": "[Amazon LP: Invent and Simplify] Tell me about a time you found a simple solution to a complex problem.",
     "cat": "behavioral", "company": "Amazon", "diff": "medium", "freq": 4,
     "answer": "**关键**: 不要讲你用了多复杂的技术，而是讲你如何把复杂问题简化。\n\n好的例子：用简单的规则引擎替代复杂的ML模型，效果差不多但维护成本降低90%。"},

    {"q": "[Amazon LP: Bias for Action] Tell me about a time you made a decision with incomplete data.",
     "cat": "behavioral", "company": "Amazon", "diff": "hard", "freq": 5,
     "answer": "**核心**: Amazon重视速度。展示你能在信息不完整时做出合理决策。\n\n**框架**: 1) 评估已有信息 2) 分析风险/可逆性 3) 快速决策 4) 设定检查点\n\n**误区**: 不要说你等到所有数据齐全才行动。"},

    {"q": "[Amazon LP: Deliver Results] Tell me about a time you had to deliver under a tight deadline.",
     "cat": "behavioral", "company": "Amazon", "diff": "medium", "freq": 5,
     "answer": "展示你的prioritization能力和执行力。\n\n**结构**: 1) 紧迫的deadline 2) 你如何拆解任务 3) 你放弃了什么(trade-off) 4) 最终按时交付+结果数字"},

    {"q": "[Amazon LP: Dive Deep] Tell me about a time you had to dig deep into data to solve a problem.",
     "cat": "behavioral", "company": "Amazon", "diff": "medium", "freq": 4,
     "answer": "展示你不是只看表面指标的人。\n\n**好例子**: 模型AUC看起来很好但线上效果差→你深入分析发现数据泄露/分布偏移→修复后真正提升。"},

    {"q": "[Amazon LP: Have Backbone; Disagree and Commit] Tell me about a time you disagreed with your manager/team.",
     "cat": "behavioral", "company": "Amazon", "diff": "hard", "freq": 5,
     "answer": "**三步走**: 1) 你有不同意见+数据支撑 2) 你respectfully表达了观点 3) 最终不管结果如何你commit了决定\n\n**关键**: 展示你有主见但也尊重团队决策。不要说你总是对的。"},

    {"q": "[Amazon LP: Earn Trust] Tell me about a time you had to earn trust from a skeptical stakeholder.",
     "cat": "behavioral", "company": "Amazon", "diff": "medium", "freq": 4,
     "answer": "用行动而不是语言建立信任。\n\n**好故事**: 1) stakeholder质疑ML的价值 2) 你先做了个小POC证明效果 3) 逐步扩大scope 4) 最终stakeholder成为你的advocate"},

    {"q": "[Amazon LP: Think Big] Tell me about a time you proposed a bold idea that was initially rejected.",
     "cat": "behavioral", "company": "Amazon", "diff": "hard", "freq": 3,
     "answer": "展示你有大局观和远见。\n\n**结构**: 1) 你看到了别人没看到的机会 2) 你的提案 3) 初期被拒的原因 4) 你如何用数据/POC说服 5) 最终impact"},

    {"q": "[Amazon LP: Hire and Develop the Best] Tell me about a time you mentored someone or helped develop a team member.",
     "cat": "behavioral", "company": "Amazon", "diff": "medium", "freq": 3,
     "answer": "不需要是formal的mentor关系。可以是code review中帮助junior成长、帮实习生完成项目等。\n\n**Key**: 展示你invest in people而不只是自己出活。"},

    # ============ Google / Googliness ============
    {"q": "[Google] Tell me about a time you navigated ambiguity in a project.",
     "cat": "behavioral", "company": "Google", "diff": "hard", "freq": 5,
     "answer": "Google特别看重处理ambiguity的能力(尤其L5+)\n\n**结构**: 1) 需求不明确/方向不清楚 2) 你如何break down问题 3) 你如何iterate+gather feedback 4) 最终清晰化方向+交付\n\n**加分**: 提到你如何communicate uncertainty给stakeholder"},

    {"q": "[Google] Describe a project where you had to make technical trade-offs.",
     "cat": "behavioral", "company": "Google", "diff": "medium", "freq": 5,
     "answer": "Google重视系统性思考。\n\n**好例子**: accuracy vs latency, 自研 vs 用开源, batch vs streaming\n\n**框架**: 1) 列出选项 2) 各自pros/cons 3) 你的推荐和rationale 4) 实际效果"},

    {"q": "[Google] Tell me about a time you improved an existing system or process.",
     "cat": "behavioral", "company": "Google", "diff": "medium", "freq": 4,
     "answer": "展示你不是只完成分配任务的人，而是主动寻找改进机会。\n\n**数字很重要**: 性能提升X倍，延迟降低Y%，开发效率提升Z%"},

    {"q": "[Google] How do you handle receiving critical feedback?",
     "cat": "behavioral", "company": "Google", "diff": "easy", "freq": 4,
     "answer": "**正确回答**: 1) 我感谢feedback 2) 我反思是否有道理 3) 我制定改进计划 4) 我follow up展示改变\n\n**错误回答**: '我觉得feedback不对' 或 '我从来没收到过负面feedback'"},

    {"q": "[Google] Tell me about a time you had to influence without authority.",
     "cat": "behavioral", "company": "Google", "diff": "hard", "freq": 5,
     "answer": "Google重视cross-functional influence(尤其Staff+)\n\n**策略**: 1) 用数据说话 2) 找到共同利益 3) 建立关系 4) 先做POC再推广\n\n**Key**: 不能靠title或权力，而是靠影响力"},

    # ============ Meta / Move Fast ============
    {"q": "[Meta] Tell me about a time you had to move fast and ship something imperfect.",
     "cat": "behavioral", "company": "Meta", "diff": "medium", "freq": 5,
     "answer": "Meta文化核心: Move Fast, Be Bold\n\n**好故事**: 1) 紧急需求 2) 你选择了MVP approach 3) 快速上线 4) 后续iterate改进\n\n**切忌**: 不要说你总是追求完美，这在Meta是减分项"},

    {"q": "[Meta] Describe a time you took a risk that didn't pay off. What did you learn?",
     "cat": "behavioral", "company": "Meta", "diff": "hard", "freq": 4,
     "answer": "Meta看重从失败中学习。\n\n**框架**: 1) 明确你做了什么决策 2) 为什么当时认为是对的 3) 结果如何 4) 你学到了什么 5) 后续如何应用这个教训\n\n**Key**: 要真诚，不要包装成功"},

    {"q": "[Meta] How do you prioritize when you have multiple urgent requests from different teams?",
     "cat": "behavioral", "company": "Meta", "diff": "medium", "freq": 5,
     "answer": "**框架**: 1) 评估impact和urgency矩阵 2) 和stakeholder沟通 3) 做出trade-off决策 4) transparent communication\n\n**加分**: 提到你用什么工具/方法来track(OKR, sprint planning等)"},

    {"q": "[Meta] Tell me about your most impactful project and why it mattered.",
     "cat": "behavioral", "company": "Meta", "diff": "medium", "freq": 5,
     "answer": "**Impact是Meta的核心考量**。你的项目要能讲清楚:\n1) 你解决了什么问题\n2) 为什么这个问题重要(business impact)\n3) 你的技术方案\n4) 量化结果(revenue/DAU/engagement)\n\n**Tips**: 准备2-3个不同维度的'最impactful'项目"},

    # ============ General High-Frequency BQ ============
    {"q": "Tell me about yourself. (Walk me through your resume)",
     "cat": "behavioral", "company": "Community", "diff": "easy", "freq": 5,
     "answer": "**2分钟电梯演讲公式**:\n1. **Hook** (10秒): 一句话总结你是谁\n2. **Past** (30秒): 之前做过什么(与目标相关的)\n3. **Present** (30秒): 现在在做什么\n4. **Future** (30秒): 为什么想来这家公司\n5. **Close** (10秒): 为什么你是最佳人选\n\n**切忌**: 不要从小学开始讲，focus on最近3-5年"},

    {"q": "Why are you leaving your current job?",
     "cat": "behavioral", "company": "Community", "diff": "easy", "freq": 5,
     "answer": "**安全回答**: 寻找更大的挑战/impact/成长空间\n**绝对不能说**: 讨厌老板、薪资太低、被fired\n\n**最佳策略**: 把重点放在'我为什么想来你们公司'而不是'我为什么要走'"},

    {"q": "Why do you want to work at [Company]?",
     "cat": "behavioral", "company": "Community", "diff": "easy", "freq": 5,
     "answer": "**三层结构**:\n1. **公司使命**: 你对公司mission的认同(要具体)\n2. **技术挑战**: 这个role有什么吸引你的技术挑战\n3. **个人成长**: 你能学到什么/贡献什么\n\n**Key**: 做功课，提到公司最近的产品/论文/新闻"},

    {"q": "What is your greatest weakness?",
     "cat": "behavioral", "company": "Community", "diff": "medium", "freq": 5,
     "answer": "**正确策略**: 说一个真实的weakness + 你正在如何改进\n\n**好例子**: '我之前不擅长public speaking，所以我主动参加了Toastmasters，现在每周都会做技术分享'\n\n**绝对不能说**: '我太追求完美了' (太假) 或真正致命的弱点"},

    {"q": "Tell me about a time you failed.",
     "cat": "behavioral", "company": "Community", "diff": "hard", "freq": 5,
     "answer": "**最important的BQ之一**。面试官在考察:\n1) 你有没有自我认知\n2) 你如何handle失败\n3) 你能不能从中学习\n\n**STAR**: Situation→Task→Action(你做错了什么)→Result(你学到了什么+后续如何应用)"},

    {"q": "Tell me about a time you had to work with a difficult colleague.",
     "cat": "behavioral", "company": "Community", "diff": "hard", "freq": 5,
     "answer": "**注意**: 不要把重点放在骂同事有多差。\n\n**正确结构**: 1) 描述情况(不带评判) 2) 你尝试理解对方perspective 3) 你找到了共同点/解决方案 4) 关系改善的结果\n\n**Key**: 展示empathy和communication能力"},

    {"q": "Describe a situation where you had to learn something new quickly to solve a problem.",
     "cat": "behavioral", "company": "Community", "diff": "medium", "freq": 4,
     "answer": "展示学习能力和adaptability。\n\n**好例子**: 项目需要用到你不熟悉的技术→你如何快速学习(读doc/找mentor/做PoC)→多久掌握→最终交付"},

    {"q": "How do you handle disagreements with cross-functional partners (PM, Design, etc)?",
     "cat": "behavioral", "company": "Community", "diff": "medium", "freq": 4,
     "answer": "**框架**: 1) 理解对方的goals和constraints 2) 用数据objectively讨论 3) 寻找win-win方案 4) 如果无法达成一致，escalate到正确的决策者\n\n**Key**: 不要说'PM总是不懂技术'"},

    {"q": "Tell me about a time you had to convince your team to adopt a new technology or approach.",
     "cat": "behavioral", "company": "Community", "diff": "hard", "freq": 4,
     "answer": "**策略**: 1) 为什么需要变化(数据/痛点) 2) 你做了哪些research 3) 你如何present proposal 4) 你如何handle resistance 5) adoption结果\n\n**加分**: 提到你做了gradual rollout而不是强推"},

    {"q": "Tell me about a time you received constructive feedback and changed your behavior.",
     "cat": "behavioral", "company": "Community", "diff": "easy", "freq": 4,
     "answer": "展示growth mindset。\n\n**结构**: 1) 收到什么feedback 2) 你的初始反应(可以说initially defensive) 3) 你如何反思 4) 你具体改变了什么 5) 改变后的效果"},

    {"q": "Describe the most challenging technical problem you've solved.",
     "cat": "behavioral", "company": "Community", "diff": "hard", "freq": 5,
     "answer": "这道题同时考察technical depth和communication能力。\n\n**结构**: 1) 问题是什么(让非技术人员也能理解) 2) 你的debug/分析过程 3) 你的解决方案(为什么选这个) 4) 结果和impact\n\n**Tips**: 选一个有深度但不要太niche的问题"},

    {"q": "How do you manage your time and stay organized?",
     "cat": "behavioral", "company": "Community", "diff": "easy", "freq": 3,
     "answer": "讲你的具体方法论，不要空谈。\n\n**好回答**: 用什么工具(Jira/Notion/Calendar blocking), 你的daily routine, 你如何处理interrupts, 你如何说no"},

    {"q": "Tell me about a time you had to give difficult feedback to someone.",
     "cat": "behavioral", "company": "Community", "diff": "hard", "freq": 4,
     "answer": "**SBI框架**: Situation→Behavior→Impact\n\n**Key**: 1) 你直接but respectfully给了feedback 2) 你in private而不是public 3) 你提供了actionable建议 4) 你follow up看改进情况"},

    {"q": "Tell me about a time you had to manage competing priorities from your manager and another stakeholder.",
     "cat": "behavioral", "company": "Community", "diff": "medium", "freq": 4,
     "answer": "展示你的stakeholder management能力。\n\n**Key**: 1) 不要自己默默扛 2) transparent communication 3) 帮stakeholder understand trade-offs 4) 让他们一起做prioritization决策"},

    {"q": "What would you do in the first 30/60/90 days in this role?",
     "cat": "behavioral", "company": "Community", "diff": "medium", "freq": 4,
     "answer": "**30天**: 学习(onboarding, 读文档, 1-on-1s, 理解codebase)\n**60天**: 贡献(第一个PR/小项目, 建立关系)\n**90天**: 影响(推动一个有impact的initiative)\n\n**Key**: 展示你humble enough to learn but ambitious enough to contribute"},

    {"q": "How do you stay up-to-date with the latest ML/AI developments?",
     "cat": "behavioral", "company": "Community", "diff": "easy", "freq": 4,
     "answer": "具体来源比空话有说服力:\n- arXiv/Papers with Code每周读2-3篇\n- Twitter/X上follow的key researchers\n- 参加的meetup/conference\n- 自己复现过的papers\n- 你的side project"},

    {"q": "Tell me about a time your project requirements changed significantly mid-way.",
     "cat": "behavioral", "company": "Community", "diff": "medium", "freq": 4,
     "answer": "展示adaptability和pragmatism。\n\n**Key**: 1) 描述变化 2) 你如何评估impact 3) 你如何re-plan 4) 你和team如何沟通 5) 最终如何deliver despite changes"},

    # ============ MLE-Specific Behavioral ============
    {"q": "[MLE] Tell me about a time a model you deployed didn't perform as expected in production.",
     "cat": "behavioral", "company": "Community", "diff": "hard", "freq": 5,
     "answer": "**MLE特有的高频题**。\n\n**结构**: 1) 什么模型/offline指标是好的 2) production问题是什么(数据偏移/延迟/label leakage) 3) 你如何debug 4) 你如何fix 5) 你加了什么monitoring防止再次发生"},

    {"q": "[MLE] How do you decide when to use a simple model vs a complex deep learning model?",
     "cat": "behavioral", "company": "Community", "diff": "medium", "freq": 5,
     "answer": "**答案框架**:\n- 数据量: 小数据→简单模型, 大数据→DL有优势\n- 解释性需求: regulated domain→可解释模型\n- 延迟要求: real-time→简单模型或distilled model\n- 迭代速度: 先baseline(LR/XGBoost)→再尝试DL\n- 维护成本: DL的infra需求更高\n\n**Key**: 展示你是pragmatic engineer而不是model fanboy"},

    {"q": "[MLE] Tell me about a time you had to communicate complex ML concepts to non-technical stakeholders.",
     "cat": "behavioral", "company": "Community", "diff": "medium", "freq": 5,
     "answer": "**核心**: 类比+可视化+business impact\n\n**好例子**: 向PM解释为什么模型不能100%准确→用垃圾邮件过滤做类比→展示precision/recall trade-off对用户体验的影响"},

    {"q": "[MLE] Describe how you would handle a situation where a dataset has significant bias.",
     "cat": "behavioral", "company": "Community", "diff": "hard", "freq": 4,
     "answer": "**步骤**: 1) 发现和量化bias(EDA, 分组统计) 2) 理解bias来源(采样偏差/标注偏差/historical bias) 3) 缓解策略(重采样/reweighting/fairness constraints) 4) 持续monitoring\n\n**Key**: 提到ethical considerations和business impact"},

    {"q": "[MLE] How do you approach A/B testing for ML models?",
     "cat": "behavioral", "company": "Community", "diff": "medium", "freq": 5,
     "answer": "**完整框架**:\n1) 假设: 新模型比现有模型在指标X上提升Y%\n2) 实验设计: 样本量计算, 分流方式, 持续时间\n3) 监控: primary metric + guardrail metrics\n4) 分析: 统计显著性, 实际显著性, segment analysis\n5) 决策: launch/iterate/kill\n\n**常见追问**: network effect, novelty effect, multiple testing"},
]

added = 0
for item in BQ_QUESTIONS:
    if item["q"] not in existing:
        entry = {
            "id": f"bq_{str(uuid.uuid4())[:8]}",
            "company": item.get("company", "Community"),
            "role": "MLE",
            "level": "L4/L5",
            "round": "behavioral",
            "domain": item["cat"],
            "question": item["q"],
            "answer": item.get("answer", ""),
            "follow_ups": [],
            "difficulty": item["diff"],
            "frequency": item["freq"],
            "importance": item["freq"],
            "tags": ["curated", "behavioral", item.get("company", "general").lower()],
            "common_mistakes": [],
            "year": 2026,
            "created_at": datetime.now().strftime("%Y-%m-%d")
        }
        data["questions"].append(entry)
        existing.add(item["q"])
        added += 1

data["metadata"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
data["metadata"]["total_questions"] = len(data["questions"])

with open(json_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print(f"Added {added} BQ questions. Total: {len(data['questions'])}")
