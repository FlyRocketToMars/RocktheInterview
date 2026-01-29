"""
Daily Content Generator
Generates personalized study content based on user's study plan
"""
import json
from pathlib import Path
from datetime import datetime, timedelta
import random


# Sample study topics organized by category
STUDY_TOPICS = {
    "coding": {
        "name": "Coding",
        "tasks": [
            "LeetCode #1 Two Sum (Easy) - 复习 Hash Map",
            "LeetCode #53 Maximum Subarray (Medium) - 动态规划入门",
            "LeetCode #200 Number of Islands (Medium) - BFS/DFS",
            "LeetCode #146 LRU Cache (Medium) - 设计题",
            "LeetCode #23 Merge k Sorted Lists (Hard) - 堆",
            "LeetCode #297 Serialize and Deserialize Binary Tree (Hard)",
            "复习排序算法: QuickSort, MergeSort, HeapSort",
            "练习图算法: Dijkstra, Bellman-Ford",
            "复习字符串处理: KMP, Rabin-Karp",
        ]
    },
    "ml_theory": {
        "name": "ML Theory",
        "tasks": [
            "复习: Bias-Variance Tradeoff",
            "复习: Regularization (L1, L2, Dropout)",
            "复习: Gradient Descent 变体 (SGD, Adam, AdaGrad)",
            "复习: Attention Mechanism 原理",
            "复习: Transformer 架构",
            "复习: BERT vs GPT 区别",
            "复习: Loss Functions (Cross-Entropy, Focal Loss)",
            "复习: Batch Normalization vs Layer Normalization",
            "复习: CNN 架构演进 (LeNet → ResNet → ViT)",
        ]
    },
    "system_design": {
        "name": "ML System Design",
        "tasks": [
            "设计: 推荐系统 (YouTube/Netflix)",
            "设计: 搜索排序系统 (Google Search)",
            "设计: 广告点击率预估系统",
            "设计: 欺诈检测系统",
            "设计: 内容审核系统",
            "设计: 实时特征服务",
            "设计: A/B Testing 平台",
            "设计: 模型训练 Pipeline",
            "设计: 模型部署和监控系统",
        ]
    },
    "behavioral": {
        "name": "Behavioral",
        "tasks": [
            "准备 STAR 故事: 攻克技术难题",
            "准备 STAR 故事: 团队协作经历",
            "准备 STAR 故事: 项目失败教训",
            "准备 STAR 故事: 推动变革",
            "复习: Amazon Leadership Principles",
            "练习: Tell me about yourself",
            "练习: Why this company?",
            "练习: 描述一个你最骄傲的项目",
        ]
    }
}

TIPS = [
    "面试前一天好好休息，保持清醒的头脑比多刷一题更重要！",
    "每道题先理清思路再写代码，和面试官多沟通！",
    "System Design 没有标准答案，展示你的思考过程最重要。",
    "Behavioral 面试要具体，用数据说话！",
    "每天进步一点点，量变引起质变。",
    "不要只背答案，理解原理才能举一反三。",
    "模拟面试很重要，找朋友互相面试！",
    "保持自信，你比你想象的更厉害！",
]


def generate_daily_content() -> dict:
    """Generate personalized daily study content."""
    today = datetime.now()
    day_of_week = today.weekday()
    
    # Rotate categories based on day of week
    categories = list(STUDY_TOPICS.keys())
    primary_category = categories[day_of_week % len(categories)]
    secondary_category = categories[(day_of_week + 1) % len(categories)]
    
    # Select tasks
    primary_tasks = random.sample(STUDY_TOPICS[primary_category]["tasks"], min(2, len(STUDY_TOPICS[primary_category]["tasks"])))
    secondary_tasks = random.sample(STUDY_TOPICS[secondary_category]["tasks"], min(1, len(STUDY_TOPICS[secondary_category]["tasks"])))
    
    all_tasks = primary_tasks + secondary_tasks
    
    # Select tip
    tip = random.choice(TIPS)
    
    # Generate message for Telegram
    message_lines = [f"📅 *{today.strftime('%Y年%m月%d日')}*\n"]
    message_lines.append(f"📌 今日重点: *{STUDY_TOPICS[primary_category]['name']}*\n")
    message_lines.append("📚 *今日任务:*")
    
    for i, task in enumerate(all_tasks, 1):
        message_lines.append(f"  {i}. {task}")
    
    message_lines.append(f"\n💡 *小贴士:* {tip}")
    
    content = {
        "date": today.isoformat(),
        "primary_category": primary_category,
        "tasks": all_tasks,
        "tips": tip,
        "message": "\n".join(message_lines)
    }
    
    return content


def main():
    """Generate and save daily content."""
    content = generate_daily_content()
    
    output_file = Path(__file__).parent / "daily_content.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=2)
    
    print(f"Daily content generated and saved to {output_file}")
    print(f"Tasks: {content['tasks']}")


if __name__ == "__main__":
    main()
