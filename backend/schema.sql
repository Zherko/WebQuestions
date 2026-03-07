-- Enable pgcrypto for UUIDs if needed
-- CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Table for Questions
CREATE TABLE IF NOT EXISTS questions (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    text TEXT NOT NULL,
    category TEXT NOT NULL DEFAULT 'amigos',
    difficulty TEXT DEFAULT 'media',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table for User Profiles (Extension of Supabase Auth)
CREATE TABLE IF NOT EXISTS profiles (
    id UUID REFERENCES auth.users ON DELETE CASCADE PRIMARY KEY,
    name TEXT,
    email TEXT UNIQUE NOT NULL,
    birth_date DATE,
    total_score BIGINT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table for Game History / Scores
CREATE TABLE IF NOT EXISTS scores (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id UUID REFERENCES auth.users ON DELETE CASCADE NOT NULL,
    score BIGINT NOT NULL,
    mode TEXT NOT NULL,
    played_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_questions_category ON questions(category);
CREATE INDEX IF NOT EXISTS idx_scores_user ON scores(user_id);
