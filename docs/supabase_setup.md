# Supabase Setup Guide

## 🚀 快速开始

### Step 1: 创建 Supabase 项目

1. 访问 [supabase.com](https://supabase.com) 并注册/登录
2. 点击 "New Project"
3. 填写项目信息：
   - **Name**: `interview-prep` (或任意名称)
   - **Database Password**: 记住这个密码
   - **Region**: 选择离你最近的区域
4. 点击 "Create new project"，等待 ~2 分钟

### Step 2: 创建数据表

在 Supabase Dashboard 中，打开 **SQL Editor**，运行以下 SQL：

```sql
-- Users table
CREATE TABLE users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id VARCHAR(50) UNIQUE NOT NULL,
    username VARCHAR(100) NOT NULL,
    points INTEGER DEFAULT 0,
    level INTEGER DEFAULT 0,
    badges JSONB DEFAULT '[]',
    total_answers INTEGER DEFAULT 0,
    total_questions INTEGER DEFAULT 0,
    answers_accepted INTEGER DEFAULT 0,
    total_upvotes_received INTEGER DEFAULT 0,
    total_upvotes_given INTEGER DEFAULT 0,
    current_streak INTEGER DEFAULT 0,
    max_streak INTEGER DEFAULT 0,
    last_login DATE,
    joined_at TIMESTAMP DEFAULT NOW(),
    ml_answers_accepted INTEGER DEFAULT 0,
    sd_answers_accepted INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Questions table for community Q&A
CREATE TABLE questions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT,
    category VARCHAR(50),
    author_id VARCHAR(50),
    author_name VARCHAR(100),
    upvotes INTEGER DEFAULT 0,
    views INTEGER DEFAULT 0,
    answer_count INTEGER DEFAULT 0,
    is_ai_question BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Answers table
CREATE TABLE answers (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    question_id UUID REFERENCES questions(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    author_id VARCHAR(50),
    author_name VARCHAR(100),
    upvotes INTEGER DEFAULT 0,
    is_accepted BOOLEAN DEFAULT FALSE,
    is_ai_generated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_users_points ON users(points DESC);
CREATE INDEX idx_users_user_id ON users(user_id);
CREATE INDEX idx_questions_created ON questions(created_at DESC);
CREATE INDEX idx_answers_question ON answers(question_id);

-- Enable Row Level Security (optional but recommended for production)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE answers ENABLE ROW LEVEL SECURITY;

-- Allow public read/write for now (adjust for production)
CREATE POLICY "Allow all" ON users FOR ALL USING (true);
CREATE POLICY "Allow all" ON questions FOR ALL USING (true);
CREATE POLICY "Allow all" ON answers FOR ALL USING (true);
```

### Step 3: 获取 API 密钥

1. 在 Supabase Dashboard 中，进入 **Settings** → **API**
2. 复制以下值：
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon public key**: `eyJhbGciOiJIUzI1NiIsInR...`

### Step 4: 配置环境变量

#### 本地开发 (`.env` 文件)

在项目根目录的 `.env` 文件中添加：

```
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR...
```

#### Streamlit Cloud

1. 进入你的 Streamlit Cloud 应用
2. 点击 **Settings** → **Secrets**
3. 添加以下内容：

```toml
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR..."
```

或者创建 `.streamlit/secrets.toml` 文件（本地）：

```toml
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR..."
```

### Step 5: 验证连接

重启应用后，用户数据会自动存入 Supabase。你可以在 Supabase Dashboard 的 **Table Editor** 中查看数据。

---

## 📊 数据结构

### users 表

| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | VARCHAR(50) | 用户唯一标识 (MD5 hash) |
| username | VARCHAR(100) | 用户名 |
| points | INTEGER | 积分 |
| level | INTEGER | 等级 |
| badges | JSONB | 徽章列表 |
| current_streak | INTEGER | 当前连续登录天数 |
| ... | ... | ... |

---

## 🔒 安全注意事项

1. **永远不要**将 `SUPABASE_KEY` 提交到 Git
2. 对于生产环境，配置更严格的 Row Level Security 策略
3. 考虑使用 Service Role Key 用于后端操作

---

## 🆘 常见问题

### Q: 没有配置 Supabase 会怎样？

A: 系统会自动回退到本地 JSON 文件存储，功能完全正常。

### Q: 如何迁移现有 JSON 数据到 Supabase？

A: 可以手动导入或写一个迁移脚本。需要的话告诉我，我可以帮你生成。
