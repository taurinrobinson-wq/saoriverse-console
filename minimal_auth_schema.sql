-- MINIMAL Authentication Setup - Just Users Table
-- Run this if the full schema still has issues

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

-- 2. Create basic indexes
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active) WHERE is_active = true;

-- 3. Enable RLS on users table
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- 4. Create basic RLS policy
DROP POLICY IF EXISTS "Users can view own profile" ON users;
CREATE POLICY "Users can view own profile" ON users
    FOR ALL USING (id = auth.uid()::uuid);

-- 5. Create user creation function
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

-- 6. Grant permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON users TO authenticated;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- Success!
SELECT 'Minimal authentication setup complete!' as result;