-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create enums
CREATE TYPE sentiment_enum AS ENUM ('positive', 'negative', 'neutral');
CREATE TYPE urgency_level AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE user_role AS ENUM ('admin', 'analyst', 'viewer');

-- Create indexes for better performance
-- These will be created automatically by SQLAlchemy, but listed here for reference

-- Sample data for testing (optional)
-- INSERT INTO tenants (id, name, slug, is_active) VALUES 
-- (gen_random_uuid(), 'Demo Company', 'demo-company', true);
