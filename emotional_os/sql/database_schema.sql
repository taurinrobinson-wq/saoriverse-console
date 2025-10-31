-- Database Schema for User Authentication System
-- Run this in your Supabase SQL Editor to create the required tables

-- 1. Create users table for authentication
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255),
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Create index for faster username lookups
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active) WHERE is_active = true;

-- 3. Update existing tables to include user_id for data isolation

-- Add user_id to emotional_tags table (if not exists)
ALTER TABLE emotional_tags 
ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES users(id);

-- Add user_id to glyphs table (if not exists) 
ALTER TABLE glyphs
ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES users(id);

-- Add user_id to glyph_logs table (if not exists)
ALTER TABLE glyph_logs
ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES users(id);

-- Add user_id to response_learning table (if not exists)
ALTER TABLE response_learning 
ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES users(id);

-- 4. Create indexes for user data isolation
CREATE INDEX IF NOT EXISTS idx_emotional_tags_user_id ON emotional_tags(user_id);
CREATE INDEX IF NOT EXISTS idx_glyphs_user_id ON glyphs(user_id);
CREATE INDEX IF NOT EXISTS idx_glyph_logs_user_id ON glyph_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_response_learning_user_id ON response_learning(user_id);

-- 5. Create unique constraints for user-specific data
ALTER TABLE glyphs 
DROP CONSTRAINT IF EXISTS unique_user_glyph_name;
ALTER TABLE glyphs 
ADD CONSTRAINT unique_user_glyph_name UNIQUE (user_id, name);

-- 6. Create Row Level Security (RLS) policies for data privacy

-- Enable RLS on all user tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE emotional_tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE glyphs ENABLE ROW LEVEL SECURITY;
ALTER TABLE glyph_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE response_learning ENABLE ROW LEVEL SECURITY;

-- Users can only see their own profile
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (id = auth.uid() OR id = current_user_id());

-- Users can only access their own emotional tags
CREATE POLICY "Users can access own emotional tags" ON emotional_tags
    FOR ALL USING (user_id IS NULL OR user_id = current_user_id());

-- Users can only access their own glyphs
CREATE POLICY "Users can access own glyphs" ON glyphs
    FOR ALL USING (user_id = current_user_id());

-- Users can only access their own glyph logs
CREATE POLICY "Users can access own glyph logs" ON glyph_logs
    FOR ALL USING (user_id = current_user_id());

-- Users can only access their own learning data
CREATE POLICY "Users can access own learning data" ON response_learning
    FOR ALL USING (user_id = current_user_id());

-- 7. Create function to get current user ID (for RLS policies)
CREATE OR REPLACE FUNCTION current_user_id()
RETURNS UUID AS $$
BEGIN
    -- This would typically come from JWT token or session
    -- For now, return from a custom header or context
    RETURN NULL; -- Placeholder - implement based on your auth system
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 8. Create function to update user last_login
CREATE OR REPLACE FUNCTION update_user_last_login(user_uuid UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE users 
    SET last_login = NOW(), updated_at = NOW()
    WHERE id = user_uuid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 9. Create view for user statistics
CREATE OR REPLACE VIEW user_stats AS
SELECT 
    u.id,
    u.username,
    u.created_at,
    u.last_login,
    COALESCE(conversation_count, 0) as conversation_count,
    COALESCE(glyph_count, 0) as glyph_count,
    COALESCE(learning_entries, 0) as learning_entries
FROM users u
LEFT JOIN (
    SELECT user_id, COUNT(*) as conversation_count
    FROM glyph_logs 
    WHERE user_id IS NOT NULL
    GROUP BY user_id
) conversations ON u.id = conversations.user_id
LEFT JOIN (
    SELECT user_id, COUNT(*) as glyph_count
    FROM glyphs 
    WHERE user_id IS NOT NULL
    GROUP BY user_id
) user_glyphs ON u.id = user_glyphs.user_id
LEFT JOIN (
    SELECT user_id, COUNT(*) as learning_entries
    FROM response_learning 
    WHERE user_id IS NOT NULL
    GROUP BY user_id
) user_learning ON u.id = user_learning.user_id
WHERE u.is_active = true;

-- 10. Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- 11. Insert sample global emotional tags (available to all users)
INSERT INTO emotional_tags (tag_name, core_emotion, response_type, tone_profile, user_id) 
VALUES 
    ('greeting', 'Neutral', 'Welcome', 'warm and inviting', NULL),
    ('plain', 'Neutral', 'Conversational', 'natural and direct', NULL),
    ('playful', 'Joy', 'Lighthearted', 'playful and humorous', NULL)
ON CONFLICT (tag_name) DO NOTHING;

-- 12. Create admin functions for user management
CREATE OR REPLACE FUNCTION create_user_account(
    p_username VARCHAR(50),
    p_email VARCHAR(255),
    p_password_hash TEXT,
    p_salt TEXT
)
RETURNS UUID AS $$
DECLARE
    new_user_id UUID;
BEGIN
    INSERT INTO users (username, email, password_hash, salt)
    VALUES (p_username, p_email, p_password_hash, p_salt)
    RETURNING id INTO new_user_id;
    
    RETURN new_user_id;
EXCEPTION
    WHEN unique_violation THEN
        RAISE EXCEPTION 'Username already exists';
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Failed to create user account';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 13. Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- Grant limited permissions for anonymous users (for public emotional tags only)
GRANT SELECT ON emotional_tags TO anon;

COMMIT;