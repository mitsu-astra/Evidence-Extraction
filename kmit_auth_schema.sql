-- CUSTOM AUTHENTICATION SCHEMA FOR KMIT USERS
-- Run this in your Supabase SQL Editor

-- Users table with UID and metadata
CREATE TABLE IF NOT EXISTS kmit_users (
    id BIGSERIAL PRIMARY KEY,
    uid TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    department TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    
    -- Constraint: email must end with @kmit.edu.in
    CONSTRAINT email_domain_check CHECK (email LIKE '%@kmit.edu.in')
);

-- Index for fast UID lookup
CREATE INDEX IF NOT EXISTS idx_kmit_users_uid ON kmit_users(uid);
CREATE INDEX IF NOT EXISTS idx_kmit_users_email ON kmit_users(email);

-- Password logs (optional - for audit)
CREATE TABLE IF NOT EXISTS kmit_password_logs (
    id BIGSERIAL PRIMARY KEY,
    uid TEXT NOT NULL,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    used BOOLEAN DEFAULT false,
    FOREIGN KEY (uid) REFERENCES kmit_users(uid) ON DELETE CASCADE
);

-- Function to generate UID automatically
CREATE OR REPLACE FUNCTION generate_uid()
RETURNS TEXT AS $$
DECLARE
    new_uid TEXT;
    exists BOOLEAN;
BEGIN
    LOOP
        -- Generate UID: KMIT + 6 random digits
        new_uid := 'KMIT' || LPAD(FLOOR(RANDOM() * 1000000)::TEXT, 6, '0');
        
        -- Check if UID already exists
        SELECT EXISTS(SELECT 1 FROM kmit_users WHERE uid = new_uid) INTO exists;
        
        -- If unique, exit loop
        EXIT WHEN NOT exists;
    END LOOP;
    
    RETURN new_uid;
END;
$$ LANGUAGE plpgsql;

-- Disable RLS for development (enable later for production)
ALTER TABLE kmit_users DISABLE ROW LEVEL SECURITY;
ALTER TABLE kmit_password_logs DISABLE ROW LEVEL SECURITY;

-- Sample data (optional - remove in production)
-- INSERT INTO kmit_users (uid, email, full_name, department) VALUES
-- ('KMIT123456', 'student1@kmit.edu.in', 'John Doe', 'CSE'),
-- ('KMIT654321', 'faculty@kmit.edu.in', 'Jane Smith', 'ECE');
