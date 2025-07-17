
-- Hive Unified Database Schema

-- User Management
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    role VARCHAR(50) DEFAULT 'developer',
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

-- Agent Management
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    endpoint VARCHAR(512) NOT NULL,
    model VARCHAR(255),
    specialization VARCHAR(100),
    capabilities JSONB,
    hardware_config JSONB,
    status VARCHAR(50) DEFAULT 'offline',
    performance_targets JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    last_seen TIMESTAMP
);

-- Workflow Management
CREATE TABLE workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    n8n_data JSONB NOT NULL,
    mcp_tools JSONB,
    created_by UUID REFERENCES users(id),
    version INTEGER DEFAULT 1,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Execution Tracking
CREATE TABLE executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID REFERENCES workflows(id),
    status VARCHAR(50) DEFAULT 'pending',
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    progress INTEGER DEFAULT 0,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Task Management
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    priority INTEGER DEFAULT 5,
    status VARCHAR(50) DEFAULT 'pending',
    assigned_agent_id UUID REFERENCES agents(id),
    workflow_id UUID REFERENCES workflows(id),
    execution_id UUID REFERENCES executions(id),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Performance Metrics (Time Series)
CREATE TABLE agent_metrics (
    agent_id UUID REFERENCES agents(id),
    timestamp TIMESTAMP NOT NULL,
    cpu_usage FLOAT,
    memory_usage FLOAT,
    gpu_usage FLOAT,
    tokens_per_second FLOAT,
    response_time FLOAT,
    active_tasks INTEGER,
    status VARCHAR(50),
    PRIMARY KEY (agent_id, timestamp)
);

-- System Alerts
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    agent_id UUID REFERENCES agents(id),
    resolved BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP
);

-- API Keys
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    key_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_agents_status ON agents(status);
CREATE INDEX idx_workflows_active ON workflows(active, created_at);
CREATE INDEX idx_executions_status ON executions(status, created_at);
CREATE INDEX idx_tasks_status_priority ON tasks(status, priority DESC, created_at);
CREATE INDEX idx_agent_metrics_timestamp ON agent_metrics(timestamp);
CREATE INDEX idx_agent_metrics_agent_time ON agent_metrics(agent_id, timestamp);
CREATE INDEX idx_alerts_unresolved ON alerts(resolved, created_at) WHERE resolved = false;
CREATE INDEX idx_projects_name ON projects(name);
CREATE INDEX idx_projects_bzzz_enabled ON projects(bzzz_enabled) WHERE bzzz_enabled = true;
CREATE INDEX idx_projects_ready_to_claim ON projects(ready_to_claim) WHERE ready_to_claim = true;

-- Project Management for Bzzz Integration
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'active',
    github_repo VARCHAR(255),
    git_url VARCHAR(255),
    git_owner VARCHAR(255),
    git_repository VARCHAR(255), 
    git_branch VARCHAR(255) DEFAULT 'main',
    bzzz_enabled BOOLEAN DEFAULT false,
    ready_to_claim BOOLEAN DEFAULT false,
    private_repo BOOLEAN DEFAULT false,
    github_token_required BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Refresh Tokens for Authentication
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Token Blacklist for Security
CREATE TABLE token_blacklist (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    blacklisted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Sample data
INSERT INTO users (email, hashed_password, role) VALUES 
('admin@hive.local', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewohT6ZErjH.2T.2', 'admin'),
('developer@hive.local', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewohT6ZErjH.2T.2', 'developer');

-- Sample project data
INSERT INTO projects (name, description, status, github_repo, git_url, git_owner, git_repository, git_branch, bzzz_enabled, ready_to_claim, private_repo, github_token_required) VALUES 
('hive', 'Distributed task coordination system with AI agents', 'active', 'anthonyrawlins/hive', 'https://github.com/anthonyrawlins/hive.git', 'anthonyrawlins', 'hive', 'main', true, true, false, false),
('bzzz', 'P2P collaborative development coordination system', 'active', 'anthonyrawlins/bzzz', 'https://github.com/anthonyrawlins/bzzz.git', 'anthonyrawlins', 'bzzz', 'main', true, true, false, false);
