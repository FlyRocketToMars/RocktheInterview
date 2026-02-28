-- SQL Migration to support AI Learning Planner, Daily Tasks, and Review Records in Supabase
-- Paste and run this in your Supabase SQL Editor

-- 1. Table for Learning Plans
CREATE TABLE IF NOT EXISTS public.learning_plans (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    template_id TEXT,
    template_name TEXT,
    start_date TEXT,
    end_date TEXT,
    daily_hours NUMERIC,
    current_week INTEGER,
    current_day INTEGER,
    completed_days INTEGER,
    total_days INTEGER,
    phases JSONB,
    daily_logs JSONB,
    created_at TEXT,
    status TEXT
);

-- Index for fast lookup by user
CREATE INDEX IF NOT EXISTS idx_learning_plans_user_id ON public.learning_plans(user_id);

-- 2. Table for Daily Learning Context
CREATE TABLE IF NOT EXISTS public.daily_learning_profiles (
    user_id TEXT PRIMARY KEY,
    profile_data JSONB,
    progress_data JSONB,
    daily_plans JSONB,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 3. Table for Spaced Repetition Review Records
CREATE TABLE IF NOT EXISTS public.review_records (
    user_id TEXT PRIMARY KEY,
    records_data JSONB,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);
