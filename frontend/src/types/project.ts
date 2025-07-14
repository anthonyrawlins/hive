export interface BzzzConfig {
  git_url?: string;
  git_owner?: string;
  git_repository?: string;
  git_branch?: string;
  bzzz_enabled?: boolean;
  ready_to_claim?: boolean;
  private_repo?: boolean;
  github_token_required?: boolean;
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  status: 'active' | 'inactive' | 'archived';
  created_at: string;
  updated_at: string;
  metadata?: Record<string, any>;
  workflows?: string[]; // workflow IDs
  tags?: string[];
  bzzz_config?: BzzzConfig;
  
  // Additional fields from filesystem analysis
  github_repo?: string;
  workflow_count?: number;
  file_count?: number;
  has_project_plan?: boolean;
  has_todos?: boolean;
}

export interface ProjectWorkflow {
  id: string;
  project_id: string;
  workflow_id: string;
  order: number;
  enabled: boolean;
  created_at: string;
}

export interface ProjectMetrics {
  total_workflows: number;
  active_workflows: number;
  total_executions: number;
  recent_executions: number;
  success_rate: number;
  last_activity?: string;
}

export interface CreateProjectRequest {
  name: string;
  description?: string;
  tags?: string[];
  metadata?: Record<string, any>;
  bzzz_config?: BzzzConfig;
}

export interface UpdateProjectRequest {
  name?: string;
  description?: string;
  status?: 'active' | 'inactive' | 'archived';
  tags?: string[];
  metadata?: Record<string, any>;
  bzzz_config?: BzzzConfig;
}

export interface BzzzTask {
  number: number;
  title: string;
  description: string;
  state: 'open' | 'closed';
  labels: string[];
  created_at: string;
  updated_at: string;
  html_url: string;
  is_claimed: boolean;
  assignees: string[];
  task_type: string;
}

export interface BzzzRepository {
  project_id: number;
  name: string;
  git_url: string;
  owner: string;
  repository: string;
  branch: string;
  bzzz_enabled: boolean;
  ready_to_claim: boolean;
  private_repo: boolean;
  github_token_required: boolean;
}