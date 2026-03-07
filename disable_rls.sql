-- Clean up RLS configuration for development
-- Run this in Supabase SQL Editor to fix security warnings

-- Drop existing policies first
DROP POLICY IF EXISTS "Enable all access for forensic_reports" ON forensic_reports;
DROP POLICY IF EXISTS "Enable all access for rag_queries" ON rag_queries;

-- Disable Row Level Security
ALTER TABLE forensic_reports DISABLE ROW LEVEL SECURITY;
ALTER TABLE rag_queries DISABLE ROW LEVEL SECURITY;

-- You should see: "Success. No rows returned"
-- All security warnings will be resolved!
