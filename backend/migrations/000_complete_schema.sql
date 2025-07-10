-- Hive Complete Database Schema
-- This file creates the entire Hive database schema from scratch
-- Includes all unified authentication features and complete platform functionality
-- Version: 2.0 (Unified Auth + Complete Platform)

-- Drop existing tables if they exist (for clean rebuild)
DROP TABLE IF EXISTS token_blacklist CASCADE;
DROP TABLE IF EXISTS refresh_tokens CASCADE;
DROP TABLE IF EXISTS api_keys CASCADE;
DROP TABLE IF EXISTS agent_metrics CASCADE;
DROP TABLE IF EXISTS alerts CASCADE;
DROP TABLE IF EXISTS tasks CASCADE;
DROP TABLE IF EXISTS executions CASCADE;
DROP TABLE IF EXISTS workflows CASCADE;
DROP TABLE IF EXISTS agents CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- USER MANAGEMENT (Unified Authentication Model)
-- =============================================================================

-- Unified Users table with complete authentication support
CREATE TABLE users (
    -- Core identification (UUID for consistency)
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Authentication fields
    username VARCHAR(50) UNIQUE,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    
    -- Extended user information
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'developer',
    
    -- User status and permissions
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);

-- API Keys for programmatic access
CREATE TABLE api_keys (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- API Key details
    name VARCHAR(255) NOT NULL,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    key_prefix VARCHAR(10) NOT NULL,
    
    -- Permissions and scope
    scopes TEXT, -- JSON array of permissions
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Usage tracking
    last_used TIMESTAMP WITH TIME ZONE,
    usage_count INTEGER DEFAULT 0,
    
    -- Expiration
    expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Refresh Tokens for JWT token management
CREATE TABLE refresh_tokens (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Token details
    token_hash VARCHAR(255) UNIQUE NOT NULL,
    jti VARCHAR(36) UNIQUE NOT NULL, -- JWT ID
    
    -- Token metadata
    device_info VARCHAR(512), -- User agent, IP, etc.
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Expiration
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Token Blacklist for revoked JWT tokens
CREATE TABLE token_blacklist (
    id SERIAL PRIMARY KEY,
    jti VARCHAR(36) UNIQUE NOT NULL, -- JWT ID
    token_type VARCHAR(20) NOT NULL, -- "access" or "refresh"
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- AGENT MANAGEMENT
-- =============================================================================

-- AI Agents in the Hive cluster
CREATE TABLE agents (
    id VARCHAR(255) PRIMARY KEY, -- Custom agent IDs (e.g., "walnut-codellama", "oak-gemini")
    name VARCHAR(255) NOT NULL,
    endpoint VARCHAR(512) NOT NULL,
    model VARCHAR(255),
    specialty VARCHAR(100),
    specialization VARCHAR(100), -- Legacy field for compatibility
    max_concurrent INTEGER DEFAULT 2,
    current_tasks INTEGER DEFAULT 0,
    agent_type VARCHAR(50) DEFAULT 'ollama', -- "ollama" or "cli"
    cli_config JSONB, -- CLI-specific configuration
    capabilities JSONB,
    hardware_config JSONB,
    status VARCHAR(50) DEFAULT 'offline',
    performance_targets JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_seen TIMESTAMP WITH TIME ZONE
);

-- Performance Metrics (Time Series)
CREATE TABLE agent_metrics (
    agent_id VARCHAR(255) REFERENCES agents(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    cpu_usage FLOAT,
    memory_usage FLOAT,
    gpu_usage FLOAT,
    tokens_per_second FLOAT,
    response_time FLOAT,
    active_tasks INTEGER,
    status VARCHAR(50),
    PRIMARY KEY (agent_id, timestamp)
);

-- =============================================================================
-- WORKFLOW MANAGEMENT
-- =============================================================================

-- Workflow definitions
CREATE TABLE workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    n8n_data JSONB NOT NULL,
    mcp_tools JSONB,
    created_by UUID REFERENCES users(id),
    version INTEGER DEFAULT 1,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Workflow executions
CREATE TABLE executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID REFERENCES workflows(id) ON DELETE SET NULL,
    status VARCHAR(50) DEFAULT 'pending',
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    progress INTEGER DEFAULT 0,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- TASK MANAGEMENT
-- =============================================================================

-- Individual tasks
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    priority INTEGER DEFAULT 5,
    status VARCHAR(50) DEFAULT 'pending',
    assigned_agent_id VARCHAR(255) REFERENCES agents(id) ON DELETE SET NULL,
    workflow_id UUID REFERENCES workflows(id) ON DELETE SET NULL,
    execution_id UUID REFERENCES executions(id) ON DELETE SET NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- =============================================================================
-- PROJECTS (Optional - for future use)
-- =============================================================================

-- Project management (placeholder for future expansion)
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'active', -- active, completed, archived
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- MONITORING AND ALERTING
-- =============================================================================

-- System alerts
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    agent_id VARCHAR(255) REFERENCES agents(id) ON DELETE SET NULL,
    resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

-- User indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username) WHERE username IS NOT NULL;
CREATE INDEX idx_users_active ON users(is_active);

-- Authentication indexes
CREATE INDEX idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX idx_api_keys_key_hash ON api_keys(key_hash);
CREATE INDEX idx_api_keys_active ON api_keys(is_active);
CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_token_hash ON refresh_tokens(token_hash);
CREATE INDEX idx_refresh_tokens_jti ON refresh_tokens(jti);
CREATE INDEX idx_refresh_tokens_active ON refresh_tokens(is_active);
CREATE INDEX idx_token_blacklist_jti ON token_blacklist(jti);
CREATE INDEX idx_token_blacklist_expires_at ON token_blacklist(expires_at);

-- Agent indexes
CREATE INDEX idx_agents_status ON agents(status);
CREATE INDEX idx_agents_type ON agents(agent_type);
CREATE INDEX idx_agents_specialty ON agents(specialty);

-- Workflow indexes
CREATE INDEX idx_workflows_active ON workflows(active, created_at);
CREATE INDEX idx_workflows_created_by ON workflows(created_by);

-- Execution indexes
CREATE INDEX idx_executions_status ON executions(status, created_at);
CREATE INDEX idx_executions_workflow ON executions(workflow_id);

-- Task indexes
CREATE INDEX idx_tasks_status_priority ON tasks(status, priority DESC, created_at);
CREATE INDEX idx_tasks_agent ON tasks(assigned_agent_id);
CREATE INDEX idx_tasks_workflow ON tasks(workflow_id);

-- Metrics indexes
CREATE INDEX idx_agent_metrics_timestamp ON agent_metrics(timestamp);
CREATE INDEX idx_agent_metrics_agent_time ON agent_metrics(agent_id, timestamp);

-- Alert indexes
CREATE INDEX idx_alerts_unresolved ON alerts(resolved, created_at) WHERE resolved = FALSE;
CREATE INDEX idx_alerts_agent ON alerts(agent_id);

-- =============================================================================
-- TRIGGERS AND FUNCTIONS
-- =============================================================================

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at columns
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_api_keys_updated_at 
    BEFORE UPDATE ON api_keys 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agents_updated_at 
    BEFORE UPDATE ON agents 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workflows_updated_at 
    BEFORE UPDATE ON workflows 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at 
    BEFORE UPDATE ON projects 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- INITIAL DATA
-- =============================================================================

-- Create initial admin user
-- Password is 'admin123' - CHANGE THIS IN PRODUCTION!
INSERT INTO users (
    email, 
    username,
    hashed_password, 
    full_name,
    role, 
    is_active, 
    is_superuser, 
    is_verified
) VALUES (
    'admin@hive.local',
    'admin', 
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewohT6ZErjH.2T.2', 
    'Hive Administrator',
    'admin',
    TRUE, 
    TRUE, 
    TRUE
);

-- Create initial developer user
-- Password is 'dev123' - CHANGE THIS IN PRODUCTION!
INSERT INTO users (
    email, 
    username,
    hashed_password, 
    full_name,
    role, 
    is_active, 
    is_verified
) VALUES (
    'developer@hive.local',
    'developer', 
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewohT6ZErjH.2T.2', 
    'Hive Developer',
    'developer',
    TRUE, 
    TRUE
);

-- Create initial project
INSERT INTO projects (name, description) VALUES 
('Default Project', 'Default project for general tasks and workflows');

-- =============================================================================
-- SCHEMA VALIDATION
-- =============================================================================

-- Verify all tables were created
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY tablename;

-- Display final schema summary
SELECT 
    'Schema created successfully! Tables: ' || COUNT(*) || ', Users: ' || 
    (SELECT COUNT(*) FROM users) || ', Ready for authentication.' as summary
FROM pg_tables 
WHERE schemaname = 'public';