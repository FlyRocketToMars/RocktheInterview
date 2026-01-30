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


def generate_daily_content(user_prefs: dict = None, user_gaps: list = None) -> dict:
    """
    Generate personalized daily study content.
    
    Args:
        user_prefs: Optional user preferences dict with content settings
        user_gaps: Optional list of skill gaps to prioritize
    
    Returns:
        Dict with tasks, tips, and formatted message
    """
    today = datetime.now()
    day_of_week = today.weekday()
    
    # Get content preferences
    content_prefs = user_prefs.get("content", {}) if user_prefs else {}
    task_count = content_prefs.get("task_count", 3)
    priority_gaps = content_prefs.get("priority_gaps", True)
    
    # Filter enabled categories
    enabled_categories = []
    if content_prefs.get("include_coding", True):
        enabled_categories.append("coding")
    if content_prefs.get("include_ml_theory", True):
        enabled_categories.append("ml_theory")
    if content_prefs.get("include_system_design", True):
        enabled_categories.append("system_design")
    if content_prefs.get("include_behavioral", True):
        enabled_categories.append("behavioral")
    
    # Default to all if none selected
    if not enabled_categories:
        enabled_categories = list(STUDY_TOPICS.keys())
    
    all_tasks = []
    
    # Priority 1: User's skill gaps (if enabled and available)
    if priority_gaps and user_gaps:
        gap_tasks = []
        for gap in user_gaps[:2]:  # Max 2 gap-based tasks
            gap_tasks.append(f"🎯 补齐技能: {gap}")
        all_tasks.extend(gap_tasks)
    
    # Priority 2: Rotate categories based on day of week
    available_categories = [c for c in enabled_categories if c in STUDY_TOPICS]
    if available_categories:
        primary_category = available_categories[day_of_week % len(available_categories)]
        secondary_category = available_categories[(day_of_week + 1) % len(available_categories)]
        
        # Fill remaining tasks
        remaining_count = task_count - len(all_tasks)
        if remaining_count > 0:
            primary_tasks = random.sample(
                STUDY_TOPICS[primary_category]["tasks"], 
                min(max(1, remaining_count - 1), len(STUDY_TOPICS[primary_category]["tasks"]))
            )
            all_tasks.extend(primary_tasks)
        
        remaining_count = task_count - len(all_tasks)
        if remaining_count > 0:
            secondary_tasks = random.sample(
                STUDY_TOPICS[secondary_category]["tasks"],
                min(remaining_count, len(STUDY_TOPICS[secondary_category]["tasks"]))
            )
            all_tasks.extend(secondary_tasks)
    
    # Ensure we have at least some tasks
    if not all_tasks:
        all_tasks = ["复习一个核心ML概念", "完成2道LeetCode题目"]
    
    # Select tip
    tip = random.choice(TIPS)
    
    # Generate message for Telegram
    message_lines = [f"📅 *{today.strftime('%Y年%m月%d日')}*\n"]
    
    if priority_gaps and user_gaps:
        message_lines.append("📌 今日重点: *技能Gap补齐*\n")
    elif available_categories:
        primary_category = available_categories[day_of_week % len(available_categories)]
        message_lines.append(f"📌 今日重点: *{STUDY_TOPICS[primary_category]['name']}*\n")
    
    message_lines.append("📚 *今日任务:*")
    
    for i, task in enumerate(all_tasks[:task_count], 1):
        message_lines.append(f"  {i}. {task}")
    
    message_lines.append(f"\n💡 *小贴士:* {tip}")
    
    content = {
        "date": today.isoformat(),
        "tasks": all_tasks[:task_count],
        "tips": tip,
        "message": "\n".join(message_lines),
        "personalized": bool(user_prefs or user_gaps)
    }
    
    return content


def generate_for_all_users() -> dict:
    """
    Generate personalized content for all subscribed users.
    
    Returns:
        Dict mapping email -> content
    """
    try:
        from .user_preferences import get_preferences
        prefs_manager = get_preferences()
        
        subscribers = prefs_manager.get_all_subscribed_users()
        user_contents = {}
        
        for user in subscribers:
            email = user["email"]
            user_prefs = user["prefs"]
            
            # TODO: Load user's gap analysis from session/database
            # For now, generate without gaps
            content = generate_daily_content(user_prefs=user_prefs)
            user_contents[email] = content
        
        return user_contents
    except Exception as e:
        print(f"Error generating for all users: {e}")
        return {}


def main():
    """Generate and save daily content."""
    # Try to generate personalized content for all users
    user_contents = generate_for_all_users()
    
    if user_contents:
        print(f"Generated personalized content for {len(user_contents)} users")
        
        # Save individual user content (for future use)
        for email, content in user_contents.items():
            print(f"  - {email}: {len(content['tasks'])} tasks")
    
    # Also generate default content for legacy/fallback
    default_content = generate_daily_content()
    
    output_file = Path(__file__).parent / "daily_content.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(default_content, f, ensure_ascii=False, indent=2)
    
    print(f"Default daily content saved to {output_file}")
    print(f"Tasks: {default_content['tasks']}")


if __name__ == "__main__":
    main()
