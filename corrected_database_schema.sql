-- Corrected Database Schema for User Authentication System
-- This version only creates necessary tables and doesn't modify non-existent ones

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

-- 2. Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active) WHERE is_active = true;

-- 3. Create emotional_tags table if it doesn't exist (needed for the system)
CREATE TABLE IF NOT EXISTS emotional_tags (
    id SERIAL PRIMARY KEY,
    tag_name VARCHAR(100) UNIQUE NOT NULL,
    core_emotion VARCHAR(50),
    response_type VARCHAR(100),
    tone_profile TEXT,
    user_id UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Create glyphs table if it doesn't exist
CREATE TABLE IF NOT EXISTS glyphs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    response_layer VARCHAR(50),
    depth INTEGER,
    glyph_type VARCHAR(50),
    symbolic_pairing TEXT,
    created_from_chat BOOLEAN DEFAULT false,
    source_message TEXT,
    emotional_tone VARCHAR(50),
    user_id UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Create glyph_logs table if it doesn't exist
CREATE TABLE IF NOT EXISTS glyph_logs (
    id SERIAL PRIMARY KEY,
    glyph_names TEXT,
    user_message TEXT,
    ai_response TEXT,
    processing_time_ms INTEGER,
    user_id UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. Create response_learning table for the learning system
CREATE TABLE IF NOT EXISTS response_learning (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    emotion_keywords JSONB,
    response_patterns JSONB,
    key_phrases JSONB,
    confidence_score DECIMAL(3,2),
    created_from_chat BOOLEAN DEFAULT true,
    user_id UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 7. Create indexes for user data isolation (only if columns exist)
DO $$
BEGIN
    -- Check if user_id column exists before creating index
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'emotional_tags' AND column_name = 'user_id') THEN
        CREATE INDEX IF NOT EXISTS idx_emotional_tags_user_id ON emotional_tags(user_id);
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'glyphs' AND column_name = 'user_id') THEN
        CREATE INDEX IF NOT EXISTS idx_glyphs_user_id ON glyphs(user_id);
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'glyph_logs' AND column_name = 'user_id') THEN
        CREATE INDEX IF NOT EXISTS idx_glyph_logs_user_id ON glyph_logs(user_id);
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'response_learning' AND column_name = 'user_id') THEN
        CREATE INDEX IF NOT EXISTS idx_response_learning_user_id ON response_learning(user_id);
    END IF;
END $$;

-- 8. Create unique constraint for user-specific glyphs
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'unique_user_glyph_name'
    ) THEN
        ALTER TABLE glyphs 
        ADD CONSTRAINT unique_user_glyph_name UNIQUE (user_id, name);
    END IF;
END $$;

-- 9. Enable Row Level Security (RLS) for data privacy (only on existing tables)
DO $$
BEGIN
    -- Enable RLS on users table
    ALTER TABLE users ENABLE ROW LEVEL SECURITY;
    
    -- Enable RLS on other tables only if they exist
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'emotional_tags') THEN
        ALTER TABLE emotional_tags ENABLE ROW LEVEL SECURITY;
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'glyphs') THEN
        ALTER TABLE glyphs ENABLE ROW LEVEL SECURITY;
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'glyph_logs') THEN
        ALTER TABLE glyph_logs ENABLE ROW LEVEL SECURITY;
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'response_learning') THEN
        ALTER TABLE response_learning ENABLE ROW LEVEL SECURITY;
    END IF;
END $$;

-- 10. Create RLS policies (only on tables that exist with user_id columns)
DO $$
BEGIN
    -- Users can only see their own profile
    DROP POLICY IF EXISTS "Users can view own profile" ON users;
    CREATE POLICY "Users can view own profile" ON users
        FOR ALL USING (id = auth.uid()::uuid);

    -- Create policies only if tables and columns exist
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'emotional_tags' AND column_name = 'user_id') THEN
        DROP POLICY IF EXISTS "Users can access own emotional tags" ON emotional_tags;
        CREATE POLICY "Users can access own emotional tags" ON emotional_tags
            FOR ALL USING (user_id IS NULL OR user_id = auth.uid()::uuid);
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'glyphs' AND column_name = 'user_id') THEN
        DROP POLICY IF EXISTS "Users can access own glyphs" ON glyphs;
        CREATE POLICY "Users can access own glyphs" ON glyphs
            FOR ALL USING (user_id = auth.uid()::uuid OR user_id IS NULL);
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'glyph_logs' AND column_name = 'user_id') THEN
        DROP POLICY IF EXISTS "Users can access own glyph logs" ON glyph_logs;
        CREATE POLICY "Users can access own glyph logs" ON glyph_logs
            FOR ALL USING (user_id = auth.uid()::uuid);
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'response_learning' AND column_name = 'user_id') THEN
        DROP POLICY IF EXISTS "Users can access own learning data" ON response_learning;
        CREATE POLICY "Users can access own learning data" ON response_learning
            FOR ALL USING (user_id = auth.uid()::uuid);
    END IF;
END $$;

-- 11. Create function to update user last_login
CREATE OR REPLACE FUNCTION update_user_last_login(user_uuid UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE users 
    SET last_login = NOW(), updated_at = NOW()
    WHERE id = user_uuid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 12. Create function for user account creation (used by edge function)
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
        RAISE EXCEPTION 'Failed to create user account: %', SQLERRM;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 13. Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- 14. Insert default global emotional tags (available to all users)
INSERT INTO emotional_tags (tag_name, core_emotion, response_type, tone_profile, user_id) 
VALUES 
    ('greeting', 'Neutral', 'Welcome', 'warm and inviting', NULL),
    ('plain', 'Neutral', 'Conversational', 'natural and direct', NULL),
    ('playful', 'Joy', 'Lighthearted', 'playful and humorous', NULL),
    ('grief', 'Sadness', 'Supportive', 'gentle and understanding', NULL),
    ('anxiety', 'Fear', 'Calming', 'reassuring and grounding', NULL),
    ('excitement', 'Joy', 'Energetic', 'enthusiastic and vibrant', NULL)
ON CONFLICT (tag_name) DO NOTHING;

-- 15. Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- Grant limited permissions for anonymous users (for public emotional tags only)
GRANT SELECT ON emotional_tags TO anon;

-- 16. Create view for user statistics (optional but useful)
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

-- Success message
SELECT 'Authentication database schema created successfully!' as result;