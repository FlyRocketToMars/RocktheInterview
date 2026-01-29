# MLE Interview Prep Platform

🎯 基于 Gap Analysis 的个性化机器学习工程师面试准备平台

## 功能特点

- **📄 简历解析**: 上传/粘贴简历，自动提取技能关键词
- **🎯 目标匹配**: 选择目标公司和职位，查看面试结构
- **📋 JD分析**: 输入职位描述，提取技能要求
- **📊 Gap Analysis**: 对比简历与JD，识别需要补齐的技能
- **📚 学习计划**: 生成个性化的面试准备计划
- **📬 每日推送**: 通过微信公众号/Telegram/邮件推送学习任务

## 技术栈

- **Frontend**: Streamlit
- **Data**: JSON (公司/技能数据)
- **Automation**: GitHub Actions (定时任务/推送)
- **Notifications**: WeChat API / Telegram Bot / Email

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行应用

```bash
cd app
streamlit run main.py
```

### 3. 配置推送 (可选)

在 `.env` 文件中配置:

```env
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
NOTIFY_EMAIL=recipient@example.com

# WeChat (需要企业微信或公众号)
WECHAT_CORP_ID=your_corp_id
WECHAT_AGENT_ID=your_agent_id
WECHAT_SECRET=your_secret
```

## 项目结构

```
interview-prep/
├── .github/workflows/      # GitHub Actions
│   └── daily_push.yml      # 每日推送任务
├── app/
│   ├── main.py             # Streamlit 入口
│   └── components/
│       └── skill_extractor.py
├── data/
│   ├── companies.json      # 公司面试数据
│   └── skills_taxonomy.json
├── notifications/          # 推送模块
│   ├── telegram_bot.py
│   ├── email_sender.py
│   └── wechat_push.py
└── requirements.txt
```

## License

MIT
