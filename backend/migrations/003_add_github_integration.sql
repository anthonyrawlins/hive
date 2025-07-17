-- Migration 003: Add GitHub Integration to Projects
-- Add GitHub repository integration fields and Bzzz configuration

ALTER TABLE projects ADD COLUMN github_repo VARCHAR;
ALTER TABLE projects ADD COLUMN git_url VARCHAR;
ALTER TABLE projects ADD COLUMN git_owner VARCHAR;
ALTER TABLE projects ADD COLUMN git_repository VARCHAR;
ALTER TABLE projects ADD COLUMN git_branch VARCHAR DEFAULT 'main';

-- Bzzz configuration fields
ALTER TABLE projects ADD COLUMN bzzz_enabled BOOLEAN DEFAULT FALSE;
ALTER TABLE projects ADD COLUMN ready_to_claim BOOLEAN DEFAULT FALSE;
ALTER TABLE projects ADD COLUMN private_repo BOOLEAN DEFAULT FALSE;
ALTER TABLE projects ADD COLUMN github_token_required BOOLEAN DEFAULT FALSE;

-- Additional metadata fields
ALTER TABLE projects ADD COLUMN metadata JSONB;
ALTER TABLE projects ADD COLUMN tags JSONB;

-- Create indexes for better performance
CREATE INDEX idx_projects_github_repo ON projects(github_repo);
CREATE INDEX idx_projects_bzzz_enabled ON projects(bzzz_enabled);
CREATE INDEX idx_projects_git_owner ON projects(git_owner);
CREATE INDEX idx_projects_git_repository ON projects(git_repository);

-- Add comments for documentation
COMMENT ON COLUMN projects.github_repo IS 'GitHub repository in owner/repo format';
COMMENT ON COLUMN projects.git_url IS 'Full Git repository URL';
COMMENT ON COLUMN projects.bzzz_enabled IS 'Whether this project is enabled for Bzzz task scanning';
COMMENT ON COLUMN projects.ready_to_claim IS 'Whether Bzzz agents can claim tasks from this project';
COMMENT ON COLUMN projects.metadata IS 'Additional project metadata as JSON';
COMMENT ON COLUMN projects.tags IS 'Project tags for categorization';